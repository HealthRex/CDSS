#!/usr/bin/python

from medinfo.common.Util import log
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from LabNormalityMatrix import LabNormalityMatrix

# Includes list of the top 25 most commonly ordered lab tests,
# unioned with the top 25 most expensive by volume (count * price) lab tests.
# There's a lot of overlap, so only 28 lab tests in total.
TOP_LAB_PANELS_BY_VOLUME = [
    "LABA1C", "LABABG", "LABBLC", "LABBLC2", "LABCAI",
    "LABCBCD", "LABCBCO", "LABHFP", "LABLAC", "LABMB",
    "LABMETB", "LABMETC", "LABMGN", "LABNTBNP", "LABPCG3",
    "LABPCTNI", "LABPHOS", "LABPOCGLU", "LABPT", "LABPTT",
    "LABROMRS", "LABTNI", "LABTYPSNI", "LABUA", "LABUAPRN",
    "LABURNC", "LABVANPRL", "LABVBG"
]

# How many rows do we need in the feature matrix?
NUM_ROWS_PER_MATRIX = 10000

# Format for matrix file names.
# Includes the name of the lab panel, the names of the components, the number
# of patients, and the number of episodes.
MATRIX_NAME_FORMAT = "%s-panel-%s-pat-%s-epi.tab"

# Generates LabTestMatrix entities for (a) each individual component of the
# lab panel and (b) the entire panel.
def generateLabPanelMatrices(labPanel):
    # Generate feature matrix for all components.
    matrix = LabNormalityMatrix(labPanel, NUM_ROWS_PER_MATRIX)
    matrix.write_matrix(MATRIX_NAME_FORMAT % (labPanel, \
        matrix.numPatients, matrix.numPatientEpisodes))

# Generates LabTestMatrices for TOP_LAB_PANELS_BY_VOLUME.
def generateTopLabPanelMatrices():
    for panel in TOP_LAB_PANELS_BY_VOLUME:
        log.info(panel)
        generateLabPanelMatrices(panel)

if __name__ == "__main__":
    generateTopLabPanelMatrices()
