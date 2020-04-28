import json
import sys
import time
from optparse import OptionParser

import pandas as pd

from medinfo.cpoe.cpoeSim.analysis.CPOETrackerAnalysis import aggregate_simulation_data
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM
from medinfo.common.Util import log
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.cpoe.cpoeSim.SimManager import SimManager


def make_usage_report(data_home, graders, out_file, survey_file=None):
    aggregate_simulation_data(data_home, output_path=out_file)
    csv = pd.read_csv(out_file)

    add_calculated_fields_to(csv)
    csv = add_sim_case_column_to(csv)
    csv, grade_columns_names = add_grades_to(csv, graders)

    # output (without row numbers)
    columns_order = ['user', 'sim_case', 'sim_patient_id'] + grade_columns_names \
                    + ['recommenderOn', 'elapsed_time', 'total_num_clicks', 'num_note_clicks',
                       'num_results_review_clicks', 'recommended_options', 'unique_recommended_options',
                       'manual_search_options', 'total_orders', 'orders_from_recommender', 'orders_from_manual_search',
                       'orders_from_recommender_missed', 'ratioOrdersFromRecommenderVsUniqueRecommenderOptions',
                       'ratioOrdersFromManualSearchVsManualSearchOptions', 'ratioOrdersFromRecommenderVsTotalOrders',
                       'ratioOrdersFromManualSearchVsTotalOrders']

    if survey_file:
        csv = add_resident_column(columns_order, csv, survey_file)

    # sort by user, sim_case, sim_patient_id combo
    csv = csv.sort_values(['user', 'sim_case', 'sim_patient_id'])

    csv.to_csv(out_file, index=False, columns=columns_order)


def add_calculated_fields_to(csv):
    csv['recommenderOn'] = [1 if recommended_option > 0 else 0 for recommended_option in csv['recommended_options']]
    csv['ratioOrdersFromRecommenderVsUniqueRecommenderOptions'] = \
        1.0 * csv['orders_from_recommender'] / csv['unique_recommended_options']
    csv['ratioOrdersFromManualSearchVsManualSearchOptions'] = \
        1.0 * csv['orders_from_manual_search'] / csv['manual_search_options']
    csv['ratioOrdersFromRecommenderVsTotalOrders'] = \
        1.0 * csv['orders_from_recommender'] / csv['total_orders']
    csv['ratioOrdersFromManualSearchVsTotalOrders'] = \
        1.0 * csv['orders_from_manual_search'] / csv['total_orders']


def add_sim_case_column_to(csv):
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
    csv = pd.merge(csv, pd.DataFrame(case_names, columns=['sim_patient_id', 'sim_case']),
                   left_on='patient', right_on='sim_patient_id')
    return csv


def add_grades_to(csv, graders):
    sim_manager = SimManager()
    grade_columns_ordered = []
    for i, grader in enumerate(sorted(graders)):
        grade_column = 'grade ({})'.format(grader)
        grades = sim_manager.grade_cases(csv['patient'].values.astype(dtype=object), grader)

        # validate most_active_user_id == most_graded_user_id
        inconsistent_users = [grade for grade in grades if grade['most_active_user_id'] != grade['most_graded_user_id']]
        if inconsistent_users:
            for inconsistent_user in inconsistent_users:
                log.warn("Case {} grading issue: most_active_user_id <> most_graded_user_id ({} <> {})!"
                         .format(inconsistent_user['sim_patient_id'],
                                 inconsistent_user['most_active_user_id'],
                                 inconsistent_user['most_graded_user_id']))

        grade_results = pd.DataFrame(grades, columns=['sim_patient_id', 'most_active_user_id', 'total_score'])
        patient_id_column = 'grade{}_patient_id'.format(i)
        grade_results.rename(columns={'sim_patient_id': patient_id_column}, inplace=True)
        csv = pd.merge(csv, grade_results,
                       left_on=['patient', 'user'], right_on=[patient_id_column, 'most_active_user_id'])
        csv.rename(columns={'total_score': grade_column}, inplace=True)
        grade_columns_ordered.append(grade_column)

    # don't need grader name if there's only 1 grade
    # if len(grade_columns_ordered) == 1:
    #     csv.rename(columns={grade_columns_ordered[0]: 'grade'}, inplace=True)
    #     grade_columns_ordered = ['grade']

    return csv, grade_columns_ordered


def add_resident_column(columns_order, csv, survey_file):
    survey_responses = pd.read_csv(survey_file)
    # retrieve sim_user_ids
    query = SQLQuery()
    query.addSelect("sim_user_id")
    query.addSelect("name")
    query.addFrom("sim_user")
    query.addWhereIn("name", survey_responses['Physician User Name'])
    user_ids = DBUtil.execute(query)
    survey_responses = pd.merge(survey_responses, pd.DataFrame(user_ids, columns=['sim_user_id', 'name']),
                                left_on='Physician User Name', right_on='name')
    csv = pd.merge(csv, survey_responses,
                   left_on='user', right_on='sim_user_id')
    columns_order.insert(1, 'resident')
    return csv


def main(argv):
    """Main method, callable from command line"""
    usage_str = "usage: %prog [options] <inputJsonDataFolder> <outputFile>\n" \
                "   <outputFile> CSV file with the usage report."

    parser = OptionParser(usage=usage_str)
    parser.add_option("-g", "--graders", dest="graders", help="Comma-separated list of graders to use for grading")
    parser.add_option("-s", "--survey", dest="survey_file", help="Path to a survey CSV file (used for adding 'resident' column)")

    (options, args) = parser.parse_args(argv[1:])

    log.info("Starting: " + str.join(" ", argv))
    timer = time.time()
    summary_data = {"argv": argv}

    grader_ids = set()
    if not options.graders:  # graders is a mandatory parameter
        print("No graders given. Cannot grade patient cases. Exiting.\n")
        parser.print_help()
        sys.exit()
    else:
        grader_ids.update(options.graders.split(VALUE_DELIM))

    survey_file = None
    if options.survey_file:
        survey_file = options.survey_file

    if len(args) < 2:  # we need input and output files given
        print("Given parameters are not enough. Exiting.\n")
        parser.print_help()
        sys.exit()

    input_folder = args[0]
    output_filename = args[1]

    # Print comment line with arguments to allow for deconstruction later as well as extra results
    print(COMMENT_TAG, json.dumps(summary_data))

    make_usage_report(input_folder, grader_ids, output_filename, survey_file)

    timer = time.time() - timer
    log.info("%.3f seconds to complete", timer)


if __name__ == "__main__":
    main(sys.argv)
