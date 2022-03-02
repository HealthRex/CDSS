"""
Definition of CohortBuilder - a class to construct a cohort (set of examples)
"""
import decimal
import pandas as pd

class CohortBuilder(object):
    """
    A class for constructing a cohort table and saving to a bigquery project.
    A cohort table should have at minimum three columns:
        1. anon_id : the patient id
        2. observation_id : a unique identifier for each observation 
        3. index_time : prediction time for each observation
        4. `label` : binary or multiclass indicating class membership of the
            observations. This may be multiple columns (if in multlilabel
            setting) and will have column names as specified in `label_columns`
            attribute.
    """

    def __init__(self, dataset_name, table_name, label_columns,
                 project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        self.project_id = project_id
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.label_columns = label_columns

    def build_cohort(self, query, transform=lambda x: x):
        """
        Uses provided query and transformation function to construct a dataframe
        representation of the cohort.  Query will vary from task to task and is
        user supplied, as is the transform function.  The transform function
        exists so that the user can apply additional logic in python to result
        of query to generate the final cohort dataframe.  By default transform
        is an identity function, meaning the result from query will be the
        cohort dataframe.

        Args:
            query : a SQL query to collect a cohort of interest
            transform : a python function to be applied ot result of query
                to construct final cohort table
        """
        self.df = pd.read_gbq(query, progress_bar_type='tqdm')
        self.df = transform(self.df)

        # Check for required columns
        try:
            assert 'anon_id' in self.df.columns
            assert 'observation_id' in self.df.columns
            assert 'index_time' in self.df.columns
            for label in self.label_columns:
                assert label in self.df.columns
        except:
            print("Unexpected columns")
            for col in self.df.columns:
                print(col)
        
        # Older version of pandas_gbq reads in numeric column as decimal
        if isinstance(self.df.observation_id.values[0], decimal.Decimal):
            self.df = self.df.assign(observation_id=lambda x:
                [int(str(d).split('.')[0]) for d in x.observation_id]
            )

    def write_cohort_table(self, overwrite=False, schema=None):
        """
        Writes the cohort dataframe to specified bigquery project, dataset,
        and table with appropriate table schema.

        Args:
            overwrite: if true overwrite existing table
            schema: dictionary of table schema, if None detect automatically. 
        """
        if overwrite:
            if_exists = 'replace'
        else:
            if_exists = 'fail'
        self.df.to_gbq(
            destination_table=f"{self.dataset_name}.{self.table_name}",
            project_id=self.project_id,
            if_exists=if_exists,
            table_schema=schema
        )
