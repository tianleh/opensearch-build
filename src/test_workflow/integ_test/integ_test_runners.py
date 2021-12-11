# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.


from test_workflow.integ_test.integ_test_runner_opensearch import IntegTestRunnerOpenSearch
from test_workflow.integ_test.integ_test_runner_opensearch_dashboards import IntegTestRunnerOpenSearchDashboards
from test_workflow.test_args import TestArgs


class IntegTestRunners:
    RUNNERS = {
        "OpenSearch": IntegTestRunnerOpenSearch,
        "OpenSearch Dashboards": IntegTestRunnerOpenSearchDashboards
    }

    @classmethod
    def from_test_manifest(cls, args: TestArgs):
        return cls.RUNNERS[args.test_manifest.name](args)
