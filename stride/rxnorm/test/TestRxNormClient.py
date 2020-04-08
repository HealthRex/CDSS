#!/usr/bin/env python
"""
Test suite for respective module in application package.
"""

import unittest

from LocalEnv import PATH_TO_CDSS, TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from starr.rxnorm.RxNormClient import RxNormClient

class TestRxNormClient(MedInfoTestCase):
    def setUp(self):
        self.client = RxNormClient()
        self.TEST_CASES = [
            {
                'rxcui': 18600,
                'name': 'azatadine',
                'properties': {
                    'propConceptGroup': {
                        'propConcept': [
                            {
                                'propCategory': 'ATTRIBUTES',
                                'propName': 'TTY',
                                'propValue': 'IN'
                            },
                            {
                                'propCategory': 'ATTRIBUTES',
                                'propName': 'GENERAL_CARDINALITY',
                                'propValue': 'SINGLE'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'RxCUI',
                                'propValue': '18600'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'NUI',
                                'propValue': 'N0000007088'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'NUI',
                                'propValue': 'N0000147714'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'UMLSCUI',
                                'propValue': 'C0052759'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'VUID',
                                'propValue': '4019620'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'ATC',
                                'propValue': 'R06AX09'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'DRUGBANK',
                                'propValue': 'DB00719'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'MESH',
                                'propValue': 'C006656'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'SNOMEDCT',
                                'propValue': '1594006'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'SNOMEDCT',
                                'propValue': '372662006'
                            },
                            {
                                'propCategory': 'CODES',
                                'propName': 'MMSL_CODE',
                                'propValue': 'GNd00791'
                            },
                            {
                                'propCategory': 'NAMES',
                                'propName': 'RxNorm Name',
                                'propValue': 'azatadine'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'Anatomical Therapeutic Chemical'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'Drug Bank'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'Multum MediSource Lexicon'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'Medical Subject Headings'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'National Drug Data File Plus Source Vocabulary'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'National Drug File'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'US Edition of SNOMED_CT'
                            },
                            {
                                'propCategory': 'SOURCES',
                                'propName': 'Source',
                                'propValue': 'Veterans Health Administration National Drug File'
                            }
                        ]
                    }
                }
            }
        ]

    def tearDown(self):
        pass

    def test_fetch_properties_by_rxcui(self):
        for test_case in self.TEST_CASES:
            rxcui = test_case['rxcui']
            expected_properties = test_case['properties']
            actual_properties = self.client.fetch_properties_by_rxcui(rxcui)

            self.assertEqual(expected_properties, actual_properties)

    def test_fetch_name_by_rxcui(self):
        for test_case in self.TEST_CASES:
            rxcui = test_case['rxcui']
            expected_name = test_case['name']
            actual_name = self.client.fetch_name_by_rxcui(rxcui)

            self.assertEqual(expected_name, actual_name)

if __name__=='__main__':
    suite = make_test_suite(TestRxNormClient)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
