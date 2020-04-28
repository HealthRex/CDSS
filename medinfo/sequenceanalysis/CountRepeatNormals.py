from collections import defaultdict
import numpy as np

from .SequenceAnalyzer import SequenceAnalyzer

class CountRepeatNormals(object):
  def __init__(self, patient_col, labresult_col, datetime_col, window_sizes):
    self.window_sizes = window_sizes
    self.global_stats = defaultdict(lambda: defaultdict(lambda: np.array([0, 0])))

    # Extract the patient_id from a row, where patient_id is in column 0
    def extract_patient_id_key_fn(row):
      return row[patient_col]

    def handle_sentinel_queue_fn(window_size, vars_dict, sentinel, row):
      vars_dict['prior_history'] = bool(row[datetime_col] - sentinel[datetime_col] <= window_size)

    # After running filter/pop queue, if results in empty queue, then do stuff here (reset prior_history record having no prior records within window / as opposed to an abnormal value being present before)
    def emptied_queue_handler_fn(window_size, vars_dict, row):
      vars_dict['prior_history'] = False

    # Acts as the mapper of a map-reduce step, where the "reduce" is left up to the user
    def extract_key_value_fn(window_size, queue, vars_dict):
      if vars_dict['prior_history']:
        # if there is prior_history, set number_consecutive_normals as usual
        number_consecutive_normals = len(queue)
      else:
        # else set number_consecutive_normals as None
        number_consecutive_normals = None
      return (window_size.days, number_consecutive_normals), 1

    # Extract the datetime from a row, where datetime is in column 2
    def extract_datetime_fn(row):
      return row[datetime_col]

    # Column 1 of row is a string that contains the lab result
    def add_row_condition_fn(window_size, queue, vars_dict, row):
      return 'InRange' in row[labresult_col]

    def clear_queue_condition_fn(window_size, queue, vars_dict, row):
      return not vars_dict['row_added']

    self.sequence_analyzer = SequenceAnalyzer()

    # Basically doing split by patientId, assuming that patientId is the first column
    self.sequence_analyzer.split_data_on_key(extract_patient_id_key_fn)

    # Prior_history reflects whether something was previously in queue. Init vars allows pass in parameter dictionary
    self.sequence_analyzer.initialize_vars({'prior_history': False})

    # If queue is just a sentinel, this will evaluate. Example sentinel value: Cleared queue after every abnormal test, but still need to keep track of date of abnormal value
    # Check whether queue has a single sentinel value, but need some residual value (e.g., last date to allow maintenance of prior_history)
    self.sequence_analyzer.handle_sentinel_queue(handle_sentinel_queue_fn)

    # Pop queue criteria, for example to remove items from head of queue as progress
    self.sequence_analyzer.pop_queue(extract_datetime_fn, emptied_queue_handler_fn)

    self.sequence_analyzer.extract_key_value(extract_key_value_fn)

    self.sequence_analyzer.add_row(add_row_condition_fn)
    self.sequence_analyzer.clear_queue(clear_queue_condition_fn, add_sentinel=True)

    self.sequence_analyzer.set_var('prior_history', lambda window_size, queue, vars_dict, row: True)

    self.sequence_analyzer.build(2)

  def run(self, base_name, results):
    counts = defaultdict(lambda: np.array([0, 0]))
    for return_values in self.sequence_analyzer.run(results, self.window_sizes):
      (key, value), row_added = return_values
      counts[key][0] += value
      if row_added:
        counts[key][1] += value

    # switch (window_size, 0) to mean no priors,
    # and switch (window_size, None) to be the total count
    total_counts = defaultdict(lambda: np.array([0, 0]))
    for k, v in counts.items():
      # Aggregate total number of results and positive results
      total_counts[k[0]] += v
    for window_size in self.window_sizes:
      # Set (1, 0) to (1, None)
      counts[(window_size.days, 0)] = counts[(window_size.days, None)]
      # Set (window_size, None) to the sum of calculated above
      counts[(window_size.days, None)] = total_counts[window_size.days]

    for k, v in counts.items():
      self.global_stats[base_name][k] += v
