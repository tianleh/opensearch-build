# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

import unittest

from system.process import Process, ProcessNotStartedError, ProcessStartedError

import logging
import os
import subprocess
import time

import requests
import yaml

class TestProcess(unittest.TestCase):
    def test(self):

        process_handler = Process()

        process_handler.start("./tests/tests_system/data/wait_for_input.sh", ".")

        self.assertTrue(process_handler.started)
        self.assertIsNotNone(process_handler.pid)
        self.assertIsNotNone(process_handler.output)
        self.assertIsNotNone(process_handler.error)

        # return_code, stdout_data, stderr_data = process_handler.terminate()

        # self.assertIsNone(return_code)
        # self.assertIsNotNone(stdout_data)
        # self.assertIsNotNone(stderr_data)

        # self.assertFalse(process_handler.started)
        # self.assertIsNone(process_handler.pid)
        # self.assertIsNone(process_handler.output)
        # self.assertIsNone(process_handler.error)

    # def test_start_twice(self):
    #     process_handler = Process()
    #     process_handler.start("ls", ".")

    #     with self.assertRaises(ProcessStartedError) as ctx:
    #         process_handler.start("pwd", ".")

    #     self.assertTrue(str(ctx.exception).startswith("Process already started, pid: "))

    # def test_terminate_unstarted_process(self):
    #     process_handler = Process()

    #     with self.assertRaises(ProcessNotStartedError) as ctx:
    #         process_handler.terminate()

    #     self.assertEqual(str(ctx.exception), "Process has not started")
    
    # def test_endpoint(self):
    #     logging.info("Waiting for service to become available")
    #     # url = self.url("/_cluster/health")
    #     url = "https://localhost:9200/_cluster/health"

    #     for attempt in range(100):
    #         try:
    #             logging.info(f"Pinging {url} attempt {attempt}")
    #             response = requests.get(url, verify=False, auth=("admin", "admin"), timeout=2)
    #             logging.info(f"{response.status_code}: {response.text}")
    #             if response.status_code == 200 and ('"status":"green"' or '"status":"yellow"' in response.text):
    #                 logging.info("Service is available")
    #                 return

    #         except requests.exceptions.ReadTimeout:
    #             logging.info("Timeout")

    #         except requests.exceptions.ConnectionError:
    #         # except:
    #             logging.info("Service not available yet")
    #             # if self.process_handler.output:
    #             #     logging.info("- stdout:")
    #             #     self.process_handler.output.flush()
    #             #     logging.info(self.process_handler.output.read())
    #             # if self.process_handler.error:
    #             #     logging.info("- stderr:")
    #             #     self.process_handler.error.flush()
    #             #     logging.info(self.process_handler.error.read())
    #         finally:
    #             logging.info("The 'try except' is finished")
            
    #         time.sleep(10)
