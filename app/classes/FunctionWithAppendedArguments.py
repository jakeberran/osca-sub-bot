# Used to call a function with stored parameters
# parameters should be a dict
# Parameters are appended onto the function call

class FunctionWithAppendedArguments:
  def __init__(self, fn, *parameters):
    self.fn = fn
    self.parameters = parameters
  
  def __call__(self, *args):
    self.fn(*args, *self.parameters)