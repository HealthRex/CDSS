'''
setup credentials: export GOOGLE_APPLICATION_CREDENTIALS='<path to json>'
'''

import psycopg2 as pg

from scripts.GoogleCloud.BQ.BigQueryConnect import BigQueryConnect

class LocalStrideConnect:

    def __init__(self, db_name, user_name, password):
        self.conn = pg.connect(dbname=db_name, user=user_name, password=password)

    def get_row_count(self, table_name):
        cur = self.conn.cursor()
        cur.execute(f'SELECT COUNT(*) from {table_name};')
        count = cur.fetchone()[0]
        return count

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def compare_table_row_counts(table_list, pg_db_name, pg_user, pg_pw):
    local_stride = LocalStrideConnect(pg_db_name, pg_user, pg_pw)
    bq_stride = BigQueryConnect()

    print('table_name\tlocal_count\tbq_count\tmatch')

    for table_name in table_list:
        local_count = local_stride.get_row_count(table_name)
        bq_count = bq_stride.get_row_count(table_name)

        count_good = 'YES' if local_count == bq_count else 'MISMATCH'

        print(f'{table_name}\t{local_count}\t{bq_count}\t{count_good}')

    return


if __name__ == '__main__':
    stride_table_list = [   'stride_2008_2017.backup_link_patient_item',
                            'stride_2008_2017.clinical_item',
                            'stride_2008_2017.clinical_item_association',
                            'stride_2008_2017.clinical_item_category',
                            'stride_2008_2017.clinical_item_link',
                            'stride_2008_2017.collection_type',
                            'stride_2008_2017.data_cache',
                            'stride_2008_2017.item_collection',
                            'stride_2008_2017.item_collection_item',
                            'stride_2008_2017.order_result_stat',
                            'stride_2008_2017.patient_item',
                            'stride_2008_2017.patient_item_collection_link',
                            'stride_2008_2017.stride_admit',
                            'stride_2008_2017.stride_adt',
                            'stride_2008_2017.stride_chargemaster',
                            'stride_2008_2017.stride_culture_micro',
                            'stride_2008_2017.stride_drg',
                            'stride_2008_2017.stride_dx_list',
                            'stride_2008_2017.stride_flowsheet',
                            'stride_2008_2017.stride_icd9_cm',
                            'stride_2008_2017.stride_income',
                            'stride_2008_2017.stride_io_flowsheet',
                            'stride_2008_2017.stride_mapped_meds',
                            'stride_2008_2017.stride_medication_mpi',
                            'stride_2008_2017.stride_note',
                            'stride_2008_2017.stride_order_med',
                            'stride_2008_2017.stride_order_medmixinfo',
                            'stride_2008_2017.stride_order_proc',
                            'stride_2008_2017.stride_order_results',
                            'stride_2008_2017.stride_orderset_order_med',
                            'stride_2008_2017.stride_orderset_order_proc',
                            'stride_2008_2017.stride_patient',
                            'stride_2008_2017.stride_patient_encounter',
                            'stride_2008_2017.stride_preadmit_med',
                            'stride_2008_2017.stride_treatment_team'
                         ]
    #stride_table_list = ['stride_2008_2017.order_result_stat', 'stride_2008_2017.collection_type']

    # stride_db_name = input('Enter STRIDE db name: ')
    # stride_db_user = input('Enter STRIDE db user: ')
    # stride_db_pw = input('Enter STRIDE db user: ')
    stride_db_name = stride_db_user = stride_db_pw = 'postgres'
    compare_table_row_counts(stride_table_list, stride_db_name, stride_db_user, stride_db_pw)