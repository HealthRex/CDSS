import json
import sys
import time
from optparse import OptionParser

import pandas as pd

from CPOETrackerAnalysis import aggregate_simulation_data
from medinfo.common.Const import COMMENT_TAG
from medinfo.common.Util import log
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery


def make_usage_report(data_home, out_file):
    aggregate_simulation_data(data_home, output_path=out_file)
    csv = pd.read_csv(out_file)

    # add calculated fields
    csv['recommenderOn'] = [1 if recommended_option > 0 else 0 for recommended_option in csv['recommended_options']]
    csv['ratioOrdersFromRecommenderVsUniqueRecommenderOptions'] = \
        1.0 * csv['orders_from_recommender'] / csv['unqique_recommended_options']
    csv['ratioOrdersFromManualSearchVsManualSearchOptions'] = \
        1.0 * csv['orders_from_manual_search'] / csv['manual_search_options']
    csv['ratioOrdersFromRecommenderVsTotalOrders'] = \
        1.0 * csv['orders_from_recommender'] / csv['total_orders']
    csv['ratioOrdersFromManualSearchVsTotalOrders'] = \
        1.0 * csv['orders_from_manual_search'] / csv['total_orders']

    # add sim_case
    query = SQLQuery()
    query.addSelect("sim_patient_id")
    query.addSelect("sim_case_name as sim_case")
    query.addFrom("sim_grading_key sgk")
    query.addJoin("sim_patient_order spo",
                  "sgk.clinical_item_id = spo.clinical_item_id and spo.sim_state_id = sgk.sim_state_id")
    query.addGroupBy("sim_patient_id")
    query.addGroupBy("sim_case_name")

    case_names = DBUtil.execute(str(query))

    # merge sim_case column
    complete_csv = pd.merge(csv, pd.DataFrame(case_names, columns=['sim_patient_id', 'sim_case']),
                            left_on='patient', right_on='sim_patient_id')

    # sort by user, patient combo
    complete_csv = complete_csv.sort_values(['user', 'sim_case', 'sim_patient_id'])

    # output (without row numbers)
    columns_order = ['user', 'sim_case', 'sim_patient_id', 'recommenderOn', 'elapsed_time', 'total_num_clicks',
                     'num_note_clicks', 'num_results_review_clicks', 'recommended_options',
                     'unqique_recommended_options', 'manual_search_options', 'total_orders', 'orders_from_recommender',
                     'orders_from_manual_search', 'orders_from_recommender_missed',
                     'ratioOrdersFromRecommenderVsUniqueRecommenderOptions',
                     'ratioOrdersFromManualSearchVsManualSearchOptions',
                     'ratioOrdersFromRecommenderVsTotalOrders', 'ratioOrdersFromManualSearchVsTotalOrders']
    complete_csv.to_csv(out_file, index=False, columns=columns_order)


if __name__ == "__main__":
    """Main method, callable from command line"""
    usage_str = "usage: %prog <inputJsonDataFolder> <outputFile>\n" \
                "   <outputFile> CSV file with the usage report."

    parser = OptionParser(usage=usage_str)
    (options, args) = parser.parse_args(sys.argv[1:])

    log.info("Starting: " + str.join(" ", sys.argv))
    timer = time.time()
    summary_data = {"argv": sys.argv}

    if len(args) < 2:
        parser.print_help()
        sys.exit()

    input_folder = args[0]

    output_filename = args[1]

    # Print comment line with arguments to allow for deconstruction later as well as extra results
    print(COMMENT_TAG, json.dumps(summary_data))

    make_usage_report(input_folder, output_filename)

    timer = time.time() - timer
    log.info("%.3f seconds to complete", timer)
