

'''
Takes care where raw, process, intermediate, and final output store.
'''

import LocalEnv
import os
import logging
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS,
                                  'scripts/LabTestAnalysis')
machine_learning_folderpath = os.path.join(project_folderpath,
                                           'machine_learning',)

class FileOrganizerRemote():
    def __init__(self, lab_type, data_source_src, data_source_dst, version):
        self.lab_type = lab_type
        self.data_source_src = data_source_src
        self.data_source_dst = data_source_dst
        self.version = version

        self.machine_learning_folderpath = os.path.join(project_folderpath,
                                                        'machine_learning',
                                                        )

        self.dataset_foldername = 'data-%s-src-%s-dst-%s-%s'%(lab_type,
                                                              data_source_src,
                                                              data_source_dst,
                                                    version
                                                   )


        self.raw_matrix_filename_template = '%s-normality-matrix-raw.tab'

    def get_raw_matrix(self, data_tag):
        if data_tag == "src":
            return FeatureMatrixIO().read_file_to_data_frame(self.raw_matrix_filepath)
        else:
            return FeatureMatrixIO().read_file_to_data_frame(self.raw_matrix_filepath)


class FileOrganizerLocal():
    '''
    Structure:
    machine_learning / ml_dataset_folder / ml_lab_folder / cached pipeline
    '''

    def __init__(self, working_folderpath):
        self.working_folderpath = working_folderpath

    def get_output_filepath(self):
        return os.path.join(self.working_folderpath, "direct_output.csv")