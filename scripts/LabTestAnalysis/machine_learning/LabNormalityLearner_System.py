

'''

Takes care where raw, process, intermediate, and final output store.

'''

import LocalEnv
import os
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
project_folderpath = os.path.join(LocalEnv.PATH_TO_CDSS,
                                  'scripts/LabTestAnalysis')

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
    def __init__(self, lab_type, data_source, version):
        self.lab_type = lab_type
        self.data_source = data_source
        self.version = version

        self.machine_learning_folderpath = os.path.join(project_folderpath,
                                                        'machine_learning',
                                                        )
        self.dataset_foldername = 'data-%s-%s-%s' % (data_source,
                                                     lab_type,
                                                     version
                                                     )

        self.raw_matrix_filename_template = '%s-normality-matrix-raw.tab'

    def get_raw_matrix(self, lab, data_label):
        raw_matrix_filepath = os.path.join(self.machine_learning_folderpath,
                                           lab,
                                           self.raw_matrix_filename_template % lab
                                          )
        return FeatureMatrixIO().read_file_to_data_frame(raw_matrix_filepath)


    def get_cached_pipeline_filepath(self, lab):
        return