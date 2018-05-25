import types
from collections import defaultdict, deque

class SequenceAnalyzer(object):
  def __init__(self):
    self.initialized_add_row = False
    self.initialized_extract_key_value = False
    self.initialized_pop_queue = False
    self.num_return_values = 0
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

  def handle_sentinel_queue(self, handle_sentinel_queue_fn):
    def func(window_size, queue, vars_dict, row):
      if queue and queue[0][0] is None:
        handle_sentinel_queue_fn(window_size, vars_dict, queue[0][1], row)
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
        while queue and timedelta_fn(extract_datetime_fn(row), extract_datetime_fn(queue[0])) > window_size:
          popped_queue = True
          queue.popleft()
      if emptied_queue_handler_fn is not None and popped_queue and not queue:
        emptied_queue_handler_fn(window_size, vars_dict, row)
    self.initialized_pop_queue = True
    self.pipeline.append(('pop_queue', func))

  def extract_key_value(self, extract_key_value_fn):
    self.pipeline.append(('extract_key_value', extract_key_value_fn))
    self.initialized_extract_key_value = True
    self.num_return_values += 1

  def set_var(self, var_name, set_value_fn):
    def func(window_size, queue, vars_dict, row):
      vars_dict[var_name] = set_value_fn(window_size, queue, vars_dict, row)
    self.pipeline.append(('set_var', func))

  def filter_sentinel(self, filter_sentinel_fn, use_vars):
    pass

  def add_row(self, condition_fn):
    def func(window_size, queue, vars_dict, row):
      vars_dict['row_added'] = False
      if condition_fn(window_size, queue, vars_dict, row):
        vars_dict['row_added'] = True
        queue.append(row)
      return vars_dict['row_added']

    self.pipeline.append(('add_row', func))
    self.initialized_add_row = True
    self.num_return_values += 1

  def clear_queue(self, condition_fn, add_sentinel=False):
    def func(window_size, queue, vars_dict, row):
      if condition_fn(window_size, queue, vars_dict, row):
        queue.clear()
        if add_sentinel:
          queue.append((None, row))
    self.pipeline.append(('clear_queue', func))

  def select_window(self, select_window_fn, use_vars):
    pass

  def compute_stats(self, compute_stats_fn, use_vars):
    pass

  def build(self, num_return_values):
    # Ensure that extract_key_value, pop_queue, and add_row are all called,
    # the module will not function properly if they aren't called
    assert self.initialized_add_row
    assert self.initialized_extract_key_value
    assert self.initialized_pop_queue

    # Checks that user knows how many values are going to be returned
    assert num_return_values == self.num_return_values
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
      bins_queue = [deque() for _ in xrange(len(bins))]
      bins_vars_dict = [dict(self.vars) for _ in xrange(len(bins))]
      for row in data_split:
        for window_size, queue, vars_dict in zip(bins, bins_queue, bins_vars_dict):
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
          yield return_values


class utils(object):
  NUMBER_SECONDS_IN_A_DAY = 86400

  @classmethod
  def get_day_difference(cls, datetime1, datetime2):
    return (datetime1 - datetime2).total_seconds() / cls.NUMBER_SECONDS_IN_A_DAY
