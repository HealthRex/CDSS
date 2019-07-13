'''
need a delete list to remove from GCP after testing (do this in web GUI)
'''
import os.environ
from pathlib import Path

from scripts.GoogleCloud.BQ.BigQueryConnect import BigQueryConnect

def test_creating_from_csv(csv_path, type_path):
    bqc = BigQueryConnect()
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'
    p = Path(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    assert p.exists(), '{os.environ["GOOGLE_APPLICATION_CREDENTIALS"]} does not exist.'

    bqc.create_new_dataset('test_dataset_delete_me')
    schema = bqc.read_table_types(type_table_path)

    bqc.load_csv_to_table('test_dataset_delete_me', 'test_table_delete_me', csv_path, auto_detect_schema=False,\
                          schema=schema, skip_rows=1)
    return

if __name__ == '__main__':
    CSV_path = input('Enter CSV_path: ')
    type_table_path = input('Enter type table path: ')
    test_creating_from_csv(CSV_path, type_table_path)




