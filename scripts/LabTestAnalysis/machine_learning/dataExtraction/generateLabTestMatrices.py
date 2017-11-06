#!/usr/bin/python

from medinfo.common.Util import log
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from LabTestMatrix import LabTestMatrix

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
MATRIX_NAME_FORMAT = "%s-panel-%s-cpts-%s-pat-%s-epi.tab"

def getComponentsInLabPanel(labPanel):
    # Initialize DB connection.
    connection = DBUtil.connection()
    cursor = connection.cursor()

    # Build query to get component names for panel.
    query = SQLQuery()
    query.addSelect("base_name")
    query.addFrom("stride_order_proc AS sop")
    query.addFrom("stride_order_results AS sor")
    query.addWhere("sop.order_proc_id = sor.order_proc_id")
    query.addWhere("proc_code = '%s'" % labPanel)
    query.addGroupBy("base_name")

    # Return component names in list.
    cursor.execute(str(query))
    return [ row[0] for row in cursor.fetchall() ]

# Generates LabTestMatrix entities for (a) each individual component of the
# lab panel and (b) the entire panel.
def generateLabPanelMatrices(labPanel):
    components = getComponentsInLabPanel(labPanel)

    # Generate feature matrix for each component.
    for component in components:
        log.info("\t%s" % component)
        matrix = LabTestMatrix([component], NUM_ROWS_PER_MATRIX)
        matrix.writeLabTestMatrix(MATRIX_NAME_FORMAT % (labPanel, component, \
            matrix.numPatients, matrix.numPatientEpisodes))

    # Generate feature matrix for all components.
    matrix = LabTestMatrix(components, NUM_ROWS_PER_MATRIX)
    matrix.writeLabTestMatrix(MATRIX_NAME_FORMAT % (labPanel, 'all', \
        matrix.numPatients, matrix.numPatientEpisodes))

# Generates LabTestMatrices for TOP_LAB_PANELS_BY_VOLUME.
def generateTopLabPanelMatrices():
    for panel in TOP_LAB_PANELS_BY_VOLUME:
        log.info(panel)
        generateLabPanelMatrices(panel)

if __name__ == "__main__":
    generateTopLabPanelMatrices()
