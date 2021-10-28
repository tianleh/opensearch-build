# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import subprocess
import time

import psutil  # type: ignore
import requests
import yaml

from aws.s3_bucket import S3Bucket
from manifests.bundle_manifest import BundleManifest
from paths.tree_walker import walk
from test_workflow.test_cluster import ClusterCreationException, TestCluster
from test_workflow.test_recorder.test_recorder import TestRecorder
from test_workflow.test_recorder.test_result_data import TestResultData


class LocalTestCluster(TestCluster):
    """
    Represents an on-box test cluster. This class downloads a bundle (from a BundleManifest) and runs it as a background process.
    """

    def __init__(self, work_dir, component_name, additional_cluster_config, bundle_manifest, security_enabled,
                 component_test_config,
                 test_recorder: TestRecorder,
                 s3_bucket_name=None):
        self.manifest = bundle_manifest
        self.work_dir = os.path.join(work_dir, "local-test-cluster")
        os.makedirs(self.work_dir, exist_ok=True)
        self.component_name = component_name
        self.security_enabled = security_enabled
        self.component_test_config = component_test_config
        self.bucket_name = s3_bucket_name
        self.additional_cluster_config = additional_cluster_config
        self.process = None
        self.save_logs = test_recorder.local_cluster_logs

    def create_cluster(self):
        self.download()
        self.stdout = open("stdout.txt", "w")
        self.stderr = open("stderr.txt", "w")
        self.install_dir = f"opensearch-{self.manifest.build.version}"
        logging.info(f"Started OpenSearch with install_dir {self.install_dir}")

        if not self.security_enabled:
            self.disable_security(self.install_dir)
        if self.additional_cluster_config is not None:
            self.__add_plugin_specific_config(self.additional_cluster_config,
                                              os.path.join(self.install_dir, "config", "opensearch.yml"))
        
        os.system("pwd")
        os.system("ls")
        self.process = subprocess.Popen(
            "./opensearch-tar-install.sh",
            cwd=self.install_dir,
            shell=True,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        logging.info(f"Started OpenSearch with parent PID {self.process.pid}")
        self.wait_for_service()

        self.install_dir_dashboards = BundleManifest.get_tarball_name_without_extension_for_dashboards(
            self.manifest.build.version, 
            self.manifest.build.architecture
        )

        logging.info(f"Started OpenSearch Dashboards with install_dir {self.install_dir_dashboards}")

        self.download_dashboards()
        os.system("pwd")
        os.system("ls")
        # os.system("ls opensearch-dashboards-1.1.0")
        self.process_dashboards = subprocess.Popen(
            "./bin/opensearch-dashboards",
            cwd=self.install_dir_dashboards,
            shell=True,
            stdout=self.stdout,
            stderr=self.stderr,
        )
        logging.info(f"Started OpenSearch Dashboards with parent PID {self.process_dashboards.pid}")
        self.wait_for_service_dashboards()

    def endpoint(self):
        return "localhost"

    def port(self):
        return 9200

    def port_dashboards(self):
        return 5601

    def destroy(self):
        if self.process is None:
            logging.info("Local test cluster is not started")
            return
        self.terminate_process()
        self.terminate_process_dashboards()
        log_files = walk(os.path.join(self.work_dir, self.install_dir, "logs"))
        test_result_data = TestResultData(self.component_name, self.component_test_config, self.return_code,
                                          self.local_cluster_stdout, self.local_cluster_stderr, log_files)
        self.save_logs.save_test_result_data(test_result_data)

    def url(self, path=""):
        # return "https://search-tianleh-test-os-l6fb7p4khyk5vriksf2zh2ubpy.us-east-1.es.amazonaws.com/_dashboards"
        return f'{"https" if self.security_enabled else "http"}://{self.endpoint()}:{self.port()}{path}'

    def url_dashboards(self, path=""):
        # return "https://search-tianleh-test-os-l6fb7p4khyk5vriksf2zh2ubpy.us-east-1.es.amazonaws.com/_dashboards"
        # return f'{"https" if self.security_enabled else "http"}://{self.endpoint()}:{self.port_dashboards()}{path}'
        return f'{"http"}://{self.endpoint()}:{self.port_dashboards()}{path}'

    def __download_tarball_from_s3(self):
        s3_path = BundleManifest.get_tarball_relative_location(
            self.manifest.build.id,
            self.manifest.build.version,
            self.manifest.build.architecture,
        )
        S3Bucket(self.bucket_name).download_file(s3_path, self.work_dir)
        return BundleManifest.get_tarball_name(
            self.manifest.build.version,
            self.manifest.build.architecture,
        )

    def __download_dashboards_tarball_from_s3(self):
        s3_path = BundleManifest.get_tarball_relative_location_for_dashboards(
            self.manifest.build.id, self.manifest.build.version, self.manifest.build.architecture)
        S3Bucket(self.bucket_name).download_file(s3_path, self.work_dir)
        return BundleManifest.get_tarball_name_for_dashboards(self.manifest.build.version, self.manifest.build.architecture)

    def download(self):
        os.system("pwd")
        logging.info(f"Creating local test cluster in {self.work_dir}")
        os.chdir(self.work_dir)
        logging.info("Downloading bundle from s3")
        bundle_name = self.__download_tarball_from_s3()

        logging.info(f'Downloaded bundle name for opensearch {bundle_name}')

        logging.info(f'Downloaded bundle to {os.path.realpath(bundle_name)}')
        logging.info("Unpacking")
        subprocess.check_call(f"tar -xzf {bundle_name}", shell=True)
        logging.info("Unpacked")
        os.system("pwd")

    def download_dashboards(self):
        os.system("pwd")
        logging.info(f"Creating local test cluster for dashboards in {self.work_dir}")
        os.chdir(self.work_dir)
        logging.info("Downloading bundle from s3")
        bundle_name = self.__download_dashboards_tarball_from_s3()

        # self.install_dir_dashboards = f"opensearch-dashboards-{self.manifest.build.version}"

        logging.info(f'Downloaded bundle name for opensearch dashboards {bundle_name}')

        logging.info(f'Downloaded dashboards bundle to {os.path.realpath(bundle_name)}')
        logging.info("Unpacking")
        # subprocess.check_call(f"mkdir {self.install_dir_dashboards} && tar -xzf {bundle_name} -C {self.install_dir_dashboards}", shell=True)
        subprocess.check_call(f"tar -xzf {bundle_name}", shell=True)
        logging.info("Unpacked")
        os.system("pwd")
        os.system("ls opensearch-dashboards-1.1.0")
        

    def disable_security(self, dir):
        subprocess.check_call(
            f'echo "plugins.security.disabled: true" >> {os.path.join(dir, "config", "opensearch.yml")}',
            shell=True,
        )

    def __add_plugin_specific_config(self, additional_config: dict, file):
        with open(file, "a") as yamlfile:
            yamlfile.write(yaml.dump(additional_config))

    def wait_for_service(self):
        logging.info("Waiting for service to become available")
        url = self.url("/_cluster/health")

        for attempt in range(10):
            try:
                logging.info(f"Pinging {url} attempt {attempt}")
                response = requests.get(url, verify=False, auth=("admin", "admin"))
                logging.info(f"{response.status_code}: {response.text}")
                if response.status_code == 200 and ('"status":"green"' or '"status":"yellow"' in response.text):
                    logging.info("Service is available")
                    return
            except requests.exceptions.ConnectionError:
                logging.info("Service not available yet")
            time.sleep(10)
        raise ClusterCreationException("Cluster is not available after 10 attempts")

    def wait_for_service_dashboards(self):
        logging.info("Waiting for dashboards service to become available")
        
        url = self.url_dashboards("/api/status")

        for attempt in range(10):
            try:
                logging.info(f"Pinging {url} attempt {attempt}")
                # response = requests.get(url, verify=False, auth=("admin", "admin"))
                response = requests.get(url, verify=False)
                logging.info(f"{response.status_code}: {response.text}")
                if response.status_code == 200: # and ('"status":"green"' or '"status":"yellow"' in response.text):
                    logging.info("Service is available")
                    return
            except requests.exceptions.ConnectionError:
                logging.info("Service not available yet")
            time.sleep(10)
        raise ClusterCreationException("Cluster is not available after 10 attempts")

    def terminate_process(self):
        parent = psutil.Process(self.process.pid)
        logging.debug("Checking for child processes")
        child_processes = parent.children(recursive=True)
        for child in child_processes:
            logging.debug(f"Found child process with pid {child.pid}")
            if child.pid != self.process.pid:
                logging.debug(f"Sending SIGKILL to {child.pid} ")
                child.kill()
        logging.info(f"Sending SIGTERM to PID {self.process.pid}")
        self.process.terminate()
        try:
            logging.info("Waiting for process to terminate")
            self.process.wait(10)
        except subprocess.TimeoutExpired:
            logging.info("Process did not terminate after 10 seconds. Sending SIGKILL")
            self.process.kill()
            try:
                logging.info("Waiting for process to terminate")
                self.process.wait(10)
            except subprocess.TimeoutExpired:
                logging.info("Process failed to terminate even after SIGKILL")
                raise
        finally:
            logging.info(f"Process terminated with exit code {self.process.returncode}")
            with open(os.path.join(os.path.realpath(self.work_dir), self.stdout.name), "r") as stdout:
                self.local_cluster_stdout = stdout.read()
            with open(os.path.join(os.path.realpath(self.work_dir), self.stderr.name), "r") as stderr:
                self.local_cluster_stderr = stderr.read()
            self.return_code = self.process.returncode
            self.stdout.close()
            self.stderr.close()
            self.process = None

    def terminate_process_dashboards(self):
        parent = psutil.Process(self.process_dashboards.pid)
        logging.debug("Checking for child processes")
        child_processes = parent.children(recursive=True)
        for child in child_processes:
            logging.debug(f"Found child process with pid {child.pid}")
            if child.pid != self.process_dashboards.pid:
                logging.debug(f"Sending SIGKILL to {child.pid} ")
                child.kill()
        logging.info(f"Sending SIGTERM to PID {self.process_dashboards.pid}")
        self.process_dashboards.terminate()
        try:
            logging.info("Waiting for process to terminate")
            self.process_dashboards.wait(10)
        except subprocess.TimeoutExpired:
            logging.info("Process did not terminate after 10 seconds. Sending SIGKILL")
            self.process_dashboards.kill()
            try:
                logging.info("Waiting for process to terminate")
                self.process_dashboards.wait(10)
            except subprocess.TimeoutExpired:
                logging.info("Process failed to terminate even after SIGKILL")
                raise
        finally:
            logging.info(f"Process terminated with exit code {self.process_dashboards.returncode}")
            with open(os.path.join(os.path.realpath(self.work_dir), self.stdout.name), "r") as stdout:
                self.local_cluster_stdout = stdout.read()
            with open(os.path.join(os.path.realpath(self.work_dir), self.stderr.name), "r") as stderr:
                self.local_cluster_stderr = stderr.read()
            self.return_code = self.process_dashboards.returncode
            self.stdout.close()
            self.stderr.close()
            self.process_dashboards = None