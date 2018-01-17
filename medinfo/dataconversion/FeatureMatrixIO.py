#!/usr/bin/python
"""
Utility class for reading and writing feature matrix files.
"""

import datetime
import os
from pandas import read_csv

class FeatureMatrixIO:
    def __init__(self):
        pass

    def read_file_to_data_frame(self, in_file_path, datetime_col_index=None):
        if datetime_col_index is None:
            datetime_col_index = 1
        data_frame = read_csv(in_file_path, sep='\t', comment='#', \
            parse_dates=[datetime_col_index])

        return data_frame

    def write_data_frame_to_file(self, data_frame, out_file_path, header=None):
        columns = list(data_frame.columns.values)
        if header is None:
            header = []

        # Open out_file.
        out_file = open(out_file_path, 'w')

        # Write header.
        for line in header:
            out_file.write('# %s\n' % line)

        # Write columns.
        column_list = '\t'.join(columns)
        out_file.write('%s\n' % column_list)

        # Write data.
        row_list = list()
        for index, row in data_frame.iterrows():
            row_str = '\t'.join([str(row[column]) for column in columns])
            out_file.write('%s\n' % row_str)

    def strip_header(self, in_file_path, out_file_path=None):
        # Set default out_file_path if none provided.
        if out_file_path is None:
            template = '%s.stripped-header.tab'
            out_file_path = template % in_file_path

        # Copies file and strips header from copy.
        in_file = open(in_file_path, 'r')
        out_file = open(out_file_path, 'w')

        # Copy line by line, ignoring header.
        for line in in_file:
            if line[0] == '#':
                continue
            else:
                out_file.write(line)

        in_file.close()
        out_file.close()

        return out_file_path
