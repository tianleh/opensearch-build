#!/usr/bin/env python

# SPDX-License-Identifier: Apache-2.0
#
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

from manifests.bundle_manifest import BundleManifest
from system import console
from test_workflow.bwc_test.bwc_test_suite import BwcTestSuite
from test_workflow.test_args import TestArgs

args = TestArgs()
console.configure(level=args.logging_level)

manifest = BundleManifest.from_file(args.manifest)


def bwc_test_suite():
    test_suite = BwcTestSuite(manifest, args.component, args.keep)
    test_suite.execute()


bwc_test_suite()
