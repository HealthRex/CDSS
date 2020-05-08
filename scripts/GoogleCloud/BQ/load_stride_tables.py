#!/usr/bin/env python3

import os
from pathlib import Path

from .BigQueryConnect import BigQueryConnect

class LoadStride:

    @staticmethod
    def load_stride_tables(csv_dir, type_dir, tables_file):
        bqc = BigQueryConnect()
        assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'
        p = Path(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        assert p.exists(), '{os.environ["GOOGLE_APPLICATION_CREDENTIALS"]} does not exist.'

        tables = [line.rstrip('\n') for line in open(tables_file)]

        for table in tables:
            print(f'Loading {table}')
            schema = bqc.read_table_types(type_dir + '/' + table + '.types')
            bqc.load_csv_to_table('stride_2008_2017', table, csv_dir + '/' + table + '.csv', auto_detect_schema=False,\
                              schema=schema, skip_rows=1)
            print(f'Done loading {table}')
        return

if __name__ == '__main__':
    csv_dir = input('Enter csv directory: ')
    type_table_dir = input('Enter type table directory: ')
    table_list_file = input('Enter table list file: ')
    LoadStride.load_stride_tables(csv_dir, type_table_dir, table_list_file)



