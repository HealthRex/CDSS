#!/usr/bin/python
"""
Test suite for BoxClient.py.
"""

import inspect
import os
import unittest

from LocalEnv import TEST_RUNNER_VERBOSITY
from medinfo.common.test.Util import make_test_suite, MedInfoTestCase
from starr.box.BoxClient import BoxClient

class TestBoxClient(MedInfoTestCase):
    def setUp(self):
        self.client = BoxClient()
        self.remote_folder_id = 48912846936
        self.upload_file_name = 'box-upload-test.txt'
        self.download_file_name = 'box-download-test.txt'
        module = inspect.getfile(inspect.currentframe())
        self.package = os.path.dirname(os.path.abspath(module))

    def tearDown(self):
        uf = self.client.get_file(self.remote_folder_id, self.upload_file_name)
        ## uf will be None after test_download_file
        if uf: uf.delete()
        
        df = '/'.join([self.package, 'test-' + self.download_file_name])
        try:
            os.remove(df)
        except OSError:
            pass

    def test_download_file(self):
        # Define file to be downloaded.
        verify_local_file_path = '/'.join([self.package, self.download_file_name])
        test_local_file_path = '/'.join([self.package, 'test-' + self.download_file_name])
        self.client.download_file(self.remote_folder_id, self.download_file_name, test_local_file_path)
        # Check file content.
        test_file = open(test_local_file_path)
        verify_file = open(verify_local_file_path)
        self.assertEqualFile(test_file, verify_file)

    def test_upload_file(self):
        # Define file to be uploaded.
        local_file_path = '/'.join([self.package, self.upload_file_name])
        # Upload file.
        remote_file = self.client.upload_file(local_file_path, self.remote_folder_id, self.upload_file_name)
        # Check file content.
        remote_content = remote_file.content()
        local_content = open('/'.join([self.package, self.upload_file_name])).read()

        self.assertEqual(remote_content, local_content)

if __name__=="__main__":
    suite = make_test_suite(TestBoxClient)
    unittest.TextTestRunner(verbosity=TEST_RUNNER_VERBOSITY).run(suite)
