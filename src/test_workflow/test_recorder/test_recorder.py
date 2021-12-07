# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import logging
import os
import shutil

import yaml

from test_workflow.test_recorder.log_recorder import LogRecorder
from test_workflow.test_recorder.test_result_data import TestResultData


class TestRecorder:
    def __init__(self, test_run_id, test_type, tests_dir):
        self.test_run_id = test_run_id
        self.test_type = test_type
        self.location = os.path.join(tests_dir, str(self.test_run_id), self.test_type)
        os.makedirs(self.location, exist_ok=True)
        logging.info(f"TestRecorder recording logs in {self.location}")
        self.local_cluster_logs = self.LocalClusterLogs(self)
        self.remote_cluster_logs = self.RemoteClusterLogs(self)
        self.test_results_logs = self.TestResultsLogs(self)

    def _create_base_folder_structure(self, component_name, component_test_config):
        dest_directory = os.path.join(self.location, str(component_name), str(component_test_config))
        os.makedirs(dest_directory, exist_ok=True)
        return os.path.realpath(dest_directory)

    def _generate_std_files(self, stdout, stderr, output_path):
        with open(os.path.join(output_path, "stdout.txt"), "w") as stdout_file:
            stdout_file.write(stdout)
        with open(os.path.join(output_path, "stderr.txt"), "w") as stderr_file:
            stderr_file.write(stderr)

    def _generate_yml(self, test_result_data: TestResultData, output_path):
        outcome = {
            "test_type": self.test_type,
            "test_run_id": self.test_run_id,
            "component_name": test_result_data.component_name,
            "test_config": test_result_data.component_test_config,
            "exit_code": test_result_data.exit_code,
        }
        with open(os.path.join(output_path, "%s.yml" % test_result_data.component_name), "w") as file:
            yaml.dump(outcome, file)
        return os.path.realpath("%s.yml" % test_result_data.component_name)

    class LocalClusterLogs(LogRecorder):
        def __init__(self, parent_class):
            self.parent_class = parent_class

        def save_test_result_data(self, test_result_data: TestResultData):
            base = self.parent_class._create_base_folder_structure(test_result_data.component_name, test_result_data.component_test_config)

            dest_directory = os.path.join(base, "local-cluster-logs")

            logging.info(f"save_test_result_data dest_directory is {dest_directory}")

            os.makedirs(dest_directory, exist_ok=True)
            log_files = test_result_data.log_files

            logging.info(f"log_files is {log_files}")

            logging.info(
                f"Recording local cluster logs for {test_result_data.component_name} with test configuration as "
                f"{test_result_data.component_test_config} at {os.path.realpath(dest_directory)}"
            )
            self.parent_class._generate_std_files(
                test_result_data.stdout,
                test_result_data.stderr,
                os.path.realpath(dest_directory),
            )

            # This is a sample log_files
            # [
            #     (
            #         '/tmp/tmpux1u0r47/local-test-cluster/opensearch-1.2.0/logs',
            #         [],
            #         [
            #             'opensearch_index_indexing_slowlog.log',
            #             'opensearch_deprecation.json',
            #             'opensearch.log',
            #             'gc.log',
            #             'opensearch_index_search_slowlog.json',
            #             'gc.log.00',
            #             'opensearch_index_search_slowlog.log',
            #             'opensearch_deprecation.log',
            #             'opensearch_index_indexing_slowlog.json',
            #             'opensearch_server.json'
            #         ]
            #     )
            # ]
            for log_dest_dir_name, source_log_dir in log_files.items():
                dest_file = os.path.join(dest_directory, log_dest_dir_name)
                shutil.copytree(source_log_dir, dest_file)

            # for log_file in log_files[0][2]:
            #     dest_file = os.path.join(dest_directory, os.path.basename(log_file))
            #     shutil.copyfile(os.path.join(log_files[0][0], log_file), dest_file)

    class RemoteClusterLogs(LogRecorder):
        def __init__(self, parent_class):
            self.parent_class = parent_class

        def save_test_result_data(self, test_result_data: TestResultData):
            base = self.parent_class._create_base_folder_structure(test_result_data.component_name, test_result_data.component_test_config)
            dest_directory = os.path.join(base, "remote-cluster-logs")
            os.makedirs(dest_directory, exist_ok=True)
            logging.info(
                f"Recording remote cluster logs for {test_result_data.component_name} with test configuration as "
                f"{test_result_data.component_test_config} at {os.path.realpath(dest_directory)}"
            )
            self.parent_class._generate_yml(test_result_data, dest_directory)

    class TestResultsLogs(LogRecorder):
        def __init__(self, parent_class):
            self.parent_class = parent_class

        def save_test_result_data(self, test_result_data: TestResultData):
            base = self.parent_class._create_base_folder_structure(test_result_data.component_name, test_result_data.component_test_config)
            dest_directory = os.path.join(base, "test-results")
            os.makedirs(dest_directory, exist_ok=False)
            logging.info(f"Recording component test results for {test_result_data.component_name} at " f"{os.path.realpath(dest_directory)}")
            self.parent_class._generate_std_files(test_result_data.stdout, test_result_data.stderr, dest_directory)
            if test_result_data.log_files is not None:

                for log_dest_dir_name, source_log_dir in test_result_data.log_files.items():

                    if os.path.exists(source_log_dir):
                        dest_file = os.path.join(dest_directory, log_dest_dir_name)
                        shutil.copytree(source_log_dir, dest_file)

                # results_dir = list(test_result_data.log_files)
                # for result in results_dir:
                #     dest_file = os.path.join(dest_directory, os.path.basename(result[0]))

                #     logging.info("*******")
                #     logging.info(f"result[0] is {result[0]}")
                #     logging.info("*******")
                #     shutil.copyfile(result[0], dest_file)
            self.parent_class._generate_yml(test_result_data, dest_directory)
