import types
from collections import defaultdict, deque

class SequenceAnalyzer(object):
  def __init__(self):
    self.built = False
    self.pipeline = []

  #TODO: do something cool where each function's input variables can change / are fluid
  def split_data_on_key(self, extract_key_fn):
    assert len(self.pipeline) == 0
    def func(data):
      if isinstance(data, types.GeneratorType):
        current_split = [data.next()]
      elif isinstance(data, types.ListType):
        current_split = [data[0]]
        data = data[1:]
      for row in data:
        if extract_key_fn(row) != extract_key_fn(current_split[-1]):
          yield current_split
          current_split = []
        current_split.append(row)
      yield current_split
    self.pipeline.append(('split_data', func))

  def initialize_vars(self, vars_dict):
    self.vars = vars_dict

  def filter_row(self, filter_row_fn):
    pass

  # TODO handle placement of None somewhere else (if date is in column 0, this might need to happen. possible solution, make a tuple of (None, row) to denote a sentinel
  def handle_sentinel_queue(self, handle_sentinel_queue_fn):
    def func(window_size, queue, vars_dict, row):
      if queue and queue[0][0] is None:
        handle_sentinel_queue_fn(window_size, vars_dict, queue[0], row)
        queue.clear()
    self.pipeline.append(('handle_sentinel_queue', func))

  # def filter_queue(self, filter_queue_fn, filter_if_fn=None, filter_else_handler_fn=None, filter_sentinel_fn=None):
  #   def func(window_size, queue, vars_dict, popped_queue, row):
  #     if queue:
  #       # TODO: handle NONE
  #       if filter_if_fn(window_size, queue, vars_dict, row):
  #         while queue and filter_queue_fn(window_size, queue, vars_dict, row):
  #           popped_queue = True
  #           queue.popleft()
  #       elif filter_else_handler_fn is not None:
  #         filter_else_handler_fn(window_size, queue, vars_dict, row)

  #     if filter_sentinel_fn is not None and popped_queue and len(queue) == 0:
  #       filter_sentinel_fn(window_size, vars_dict, row)
  #   self.pipeline.append('filter_queue', func)


  def pop_queue(self, timedelta_fn, extract_datetime_fn, emptied_queue_handler_fn=None):
    def func(window_size, queue, vars_dict, row):
      popped_queue = False
      if queue and queue[0][0] is not None:
        # while queue and filter_queue_fn(window_size, queue, vars_dict, row):
        while queue and timedelta_fn(extract_datetime_fn(row), extract_datetime_fn(queue[0])) > window_size:
          popped_queue = True
          queue.popleft()
      if emptied_queue_handler_fn is not None and popped_queue and not queue:
        emptied_queue_handler_fn(window_size, vars_dict, row)
    self.pipeline.append(('pop_queue', func))

  def extract_key_value(self, extract_key_value_fn):
    self.pipeline.append(('extract_key_value', extract_key_value_fn))

  def set_var(self, var_name, set_value_fn):
    def func(window_size, queue, vars_dict, row):
      vars_dict[var_name] = set_value_fn(window_size, queue, vars_dict, row)
    self.pipeline.append(('set_var', func))

  def filter_sentinel(self, filter_sentinel_fn, use_vars):
    pass

  def add_row(self, condition_fn):
    def func(window_size, queue, vars_dict, row):
      vars_dict['row_added'] = condition_fn(window_size, queue, vars_dict, row)
      if vars_dict['row_added']:
        # if normal, increment normal_count
        queue.append(row)
      return vars_dict['row_added']

      #   stats[(window_size, number_consecutive_normals)][1] += 1
      # else:
      #   vars_dict['row_added'] = False
      #   # else clear the queue and add a sentinel value with the date of the
      #   # most recent result
    self.pipeline.append(('add_row', func))

  def clear_queue(self, condition_fn, add_sentinel=False):
    def func(window_size, queue, vars_dict, row):
      if condition_fn(window_size, queue, vars_dict, row):
        queue.clear()
        if add_sentinel:
          # queue.append((None, row))
          queue.append((None, None, row[2]))
    self.pipeline.append(('clear_queue', func))

  def select_window(self, select_window_fn, use_vars):
    pass

  def compute_stats(self, compute_stats_fn, use_vars):
    pass

  def build(self):
    self.built = True

  def run(self, data, bins):
    # check if built
    assert self.built
    data_split_generator = data
    pipeline = self.pipeline
    if self.pipeline[0][0] == 'split_data':
      data_split_generator = self.pipeline[0][1](data)
      pipeline = pipeline[1:]

    for data_split in data_split_generator:
      # print(data_split)
      bins_queue = [deque() for _ in xrange(len(bins))]
      bins_vars_dict = [dict(self.vars) for _ in xrange(len(bins))]
      for row in data_split:
        # print(row)
        for window_size, queue, vars_dict in zip(bins, bins_queue, bins_vars_dict):
          # print(queue)
          vars_dict['row_added'] = False
          return_values = []
          for name, func in pipeline:
            if name == 'handle_sentinel_queue':
              func(window_size, queue, vars_dict, row)
            elif name == 'pop_queue':
              func(window_size, queue, vars_dict, row)
            elif name == 'set_var':
              func(window_size, queue, vars_dict, row)
            elif name == 'extract_key_value':
              return_values.append(func(window_size, queue, vars_dict))
            elif name == 'add_row':
              return_values.append(func(window_size, queue, vars_dict, row))
            elif name == 'clear_queue':
              func(window_size, queue, vars_dict, row)
          # print(queue)
          yield return_values


class utils(object):
  NUMBER_SECONDS_IN_A_DAY = 86400

  @classmethod
  def get_day_difference(cls, datetime1, datetime2):
    return (datetime1 - datetime2).total_seconds() / cls.NUMBER_SECONDS_IN_A_DAY
