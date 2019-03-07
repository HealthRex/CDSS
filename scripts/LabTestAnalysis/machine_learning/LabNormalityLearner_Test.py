


import LabNormalityLearner as LNL
import LabNormalityLearner_Config as Config
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

remover = LNL.FeatureRemover(Config.features_to_remove)

fm_io = FeatureMatrixIO()
raw_matrix = fm_io.read_file_to_data_frame('LabNormalityLearner_TestData/LABA1C-normality-matrix-raw.tab')
print raw_matrix.shape

processed_matrix_removed = remover.transform(raw_matrix)
print processed_matrix_removed.shape