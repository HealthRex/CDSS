

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
    def __init__(self, lab_type, data_source_train, data_source_test, version):
        self.lab_type = lab_type
        self.data_source_train = data_source_train
        self.data_source_test = data_source_test
        self.version = version

        self.machine_learning_folderpath = os.path.join(project_folderpath,
                                                        'machine_learning',
                                                        )

        self.dataset_foldername = 'data-%s-src-%s-dst-%s-%s'%(lab_type,
                                                   data_source_train,
                                                   data_source_test,
                                                   version
                                                   )


        self.raw_matrix_filename_template = '%s-normality-matrix-raw.tab'


class FileOrganizerLocal():
    '''
    Structure:
    machine_learning / ml_dataset_folder / ml_lab_folder / cached pipeline

    '''

    def __init__(self, lab, lab_type, data_source, version):
        self.lab = lab
        self.lab_type = lab_type
        self.data_source = data_source
        self.version = version

        self.cur_tag = '%s-%s-%s'% (data_source, lab_type, version)


        self.dataset_foldername = 'data-%s' % self.cur_tag
        self.ml_dataset_folderpath = os.path.join(machine_learning_folderpath,
                                               self.dataset_foldername)
        if not os.path.exists(self.ml_dataset_folderpath):
            logging.info('Path %s not existing, creating...' % self.ml_dataset_folderpath)
            os.mkdir(self.ml_dataset_folderpath)
        else:
            logging.info('Path %s exists...' % self.ml_dataset_folderpath)

        self.raw_matrix_filename_template = '%s-normality-matrix-raw.tab'

        self.cached_pipeline_filename = 'pipeline_memory_%s' % self.cur_tag


        self.ml_lab_folderpath = os.path.join(self.ml_dataset_folderpath, lab)
        if not os.path.exists(self.ml_lab_folderpath):
            logging.info('Path %s not existing, creating...' % self.ml_lab_folderpath)
            os.mkdir(self.ml_lab_folderpath)
        else:
            logging.info('Path %s exists...' % self.ml_lab_folderpath)

        self.raw_matrix_filepath = os.path.join(self.ml_lab_folderpath,
                                           self.raw_matrix_filename_template % self.lab)

        self.cached_pipeline_filepath = os.path.join(self.ml_lab_folderpath,
                                                     self.cached_pipeline_filename)

    def get_raw_matrix(self):
        return FeatureMatrixIO().read_file_to_data_frame(self.raw_matrix_filepath)

