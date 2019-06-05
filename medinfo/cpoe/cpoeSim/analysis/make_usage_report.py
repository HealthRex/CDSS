import pandas as pd
from CPOETrackerAnalysis import aggregate_simulation_data

out_file = ''  # Fill in with path to which csv output will be saved
data_home = ''  # Fill in with path to directory containing v4 json files

# Run aggregator
aggregate_simulation_data(data_home, output_path=out_file)
