import logging
import os
import unittest
from unittest.mock import patch

from test_workflow.test_args import TestArgs


class TestTestArgs(unittest.TestCase):

    ARGS_PY = os.path.realpath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "run_bwc_test.py"
        )
    )

    PATH = os.path.join(
        os.path.dirname(__file__), "data"
    )

    TEST_MANIFEST_PATH = os.path.join(
        os.path.dirname(__file__), "data", "test_manifest.yml"
    )

    TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH = os.path.join(
        os.path.dirname(__file__), "data", "test-manifest-opensearch-dashboards.yml"
    )

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_PATH])
    def test_opensearch_default_with_opensearch_test_manifest(self):
        test_args = TestArgs()
        self.assertFalse(hasattr(test_args, "opensearch"))
        self.assertFalse(hasattr(test_args, "opensearch_dashboards_path"))

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.INFO)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_PATH, "--paths", "opensearch=" + TEST_MANIFEST_PATH])
    def test_opensearch_file_with_opensearch_test_manifest(self):
        test_args = TestArgs()
        self.assertEqual(test_args.paths.get("opensearch"), os.path.realpath(self.TEST_MANIFEST_PATH))
        self.assertFalse(hasattr(test_args.paths, "opensearch_dashboards_path"))

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.INFO)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_PATH, "--paths", "opensearch=https://ci.opensearch.org/x/y", "--verbose"])
    def test_opensearch_url_with_opensearch_test_manifest(self):
        test_args = TestArgs()
        self.assertEqual(test_args.paths.get("opensearch"), "https://ci.opensearch.org/x/y")
        self.assertFalse(hasattr(test_args.paths, "opensearch_dashboards_path"))

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.DEBUG)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH, "--paths", "opensearch=" + TEST_MANIFEST_PATH])
    def test_opensearch_dashboards_default_with_opensearch_dashboards_test_manifest(self):
        test_args = TestArgs()
        self.assertFalse(hasattr(test_args.paths, "opensearch_dashboards_path"))
        self.assertEqual(test_args.paths.get("opensearch"), self.TEST_MANIFEST_PATH)

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.INFO)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)

    @patch(
        "argparse._sys.argv",
        [
            ARGS_PY,
            TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH,
            "--paths",
            "opensearch-dashboards=" + TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH,
            "opensearch=" + TEST_MANIFEST_PATH
        ]
    )
    def test_opensearch_dashboards_file_with_opensearch_dashboards_test_manifest(self):
        test_args = TestArgs()
        self.assertEqual(test_args.paths.get("opensearch-dashboards"), self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)
        self.assertEqual(test_args.paths.get("opensearch"), self.TEST_MANIFEST_PATH)

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.INFO)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH, "--paths", "opensearch-dashboards=https://ci.opensearch.org/x/y", "opensearch=" + TEST_MANIFEST_PATH])
    def test_opensearch_dashboards_url_with_opensearch_dashboards_test_manifest(self):
        test_args = TestArgs()
        self.assertEqual(test_args.paths.get("opensearch-dashboards"), "https://ci.opensearch.org/x/y")
        self.assertEqual(test_args.paths.get("opensearch"), self.TEST_MANIFEST_PATH)

        self.assertIsNotNone(test_args.test_run_id)
        self.assertIsNone(test_args.component)
        self.assertFalse(test_args.keep)
        self.assertEqual(test_args.logging_level, logging.INFO)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)

    @patch(
        "argparse._sys.argv",
        [
            ARGS_PY,
            TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH,
            "--paths",
            "opensearch=https://ci.opensearch.org/x/y",
            "opensearch-dashboards=https://ci.opensearch.org/x/y/dashboards",
            "--verbose"
        ]
    )
    def test_opensearch_url_opensearch_dashboards_url_with_opensearch_dashboards_test_manifest(self):
        test_args = TestArgs()
        self.assertEqual(test_args.paths.get("opensearch"), "https://ci.opensearch.org/x/y")
        self.assertEqual(test_args.paths.get("opensearch-dashboards"), "https://ci.opensearch.org/x/y/dashboards")
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_OPENSEARCH_DASHBOARDS_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_PATH, "--paths", "opensearch=" + TEST_MANIFEST_PATH, "--test-run-id", "6"])
    def test_run_id(self):
        test_args = TestArgs()
        self.assertEqual(test_args.test_run_id, 6)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_PATH)

    @patch("argparse._sys.argv", [ARGS_PY, TEST_MANIFEST_PATH, "--paths", "opensearch=" + TEST_MANIFEST_PATH, "--verbose"])
    def test_verbose(self):
        test_args = TestArgs()
        self.assertEqual(test_args.logging_level, logging.DEBUG)
        self.assertEqual(test_args.test_manifest_path, self.TEST_MANIFEST_PATH)
