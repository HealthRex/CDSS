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
                    u'propConceptGroup': {
                        u'propConcept': [
                            {
                                u'propCategory': u'ATTRIBUTES',
                                u'propName': u'TTY',
                                u'propValue': u'IN'
                            },
                            {
                                u'propCategory': u'ATTRIBUTES',
                                u'propName': u'GENERAL_CARDINALITY',
                                u'propValue': u'SINGLE'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'RxCUI',
                                u'propValue': u'18600'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'NUI',
                                u'propValue': u'N0000007088'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'NUI',
                                u'propValue': u'N0000147714'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'UMLSCUI',
                                u'propValue': u'C0052759'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'VUID',
                                u'propValue': u'4019620'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'ATC',
                                u'propValue': u'R06AX09'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'DRUGBANK',
                                u'propValue': u'DB00719'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'MESH',
                                u'propValue': u'C006656'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'SNOMEDCT',
                                u'propValue': u'1594006'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'SNOMEDCT',
                                u'propValue': u'372662006'
                            },
                            {
                                u'propCategory': u'CODES',
                                u'propName': u'MMSL_CODE',
                                u'propValue': u'GNd00791'
                            },
                            {
                                u'propCategory': u'NAMES',
                                u'propName': u'RxNorm Name',
                                u'propValue': u'azatadine'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'Anatomical Therapeutic Chemical'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'Drug Bank'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'Multum MediSource Lexicon'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'Medical Subject Headings'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'National Drug Data File Plus Source Vocabulary'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'National Drug File'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'US Edition of SNOMED_CT'
                            },
                            {
                                u'propCategory': u'SOURCES',
                                u'propName': u'Source',
                                u'propValue': u'Veterans Health Administration National Drug File'
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
