'''
TODO: still work-in-progress
TODO: need a delete list to remove from GCP after testing
'''
import os
from pathlib import Path

from scripts.GoogleCloud.BQ.BigQueryConnect import BigQueryConnect

def test_creating_from_csv(csv_path):
    bqc = BigQueryConnect()
    assert 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ, 'GOOGLE_APPLICATION_CREDENTIALS is not set.'
    p = Path(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    assert p.exists(), '{os.environ["GOOGLE_APPLICATION_CREDENTIALS"]} does not exist.'

    bqc.create_new_dataset('test_dataset_delete_me')

    bqc.load_csv_to_table('test_dataset_delete_me', 'test_table_delete_me', csv_path)
    return

if __name__ == '__main__':
    CSV_path = '/Users/starli/stride_treatment_team.csv'
    test_creating_from_csv(CSV_path)




