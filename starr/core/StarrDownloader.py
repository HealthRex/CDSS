#!/usr/bin/python
"""
Simple wrapper around BoxClient for downloading STARR data from Box.
"""

from LocalEnv import BOX_STARR_FOLDER_ID
from starr.box.BoxClient import BoxClient

class StarrDownloader:
    def __init__():
        self.box = BoxClient()

    @staticmethod
    def download_starr_data():
        
        self.box.download_file(BOX_STARR_FOLDER_ID, file_name, local_path)
