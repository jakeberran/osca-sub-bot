# Each action is a singular addition / deletion / boost
import json

class Action:
  def __init__(self, actionType, data = {}):
    """
    :param actionType: either "add" or "delete" or "boost"
    :param data: if actionType === "add", then all the params in a sub request,
    otherwise just email (str), time (of shift as datetime)
    """
    self.actionType = actionType
    self.data = data

  def __repr__(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
