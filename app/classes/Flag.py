# Used to flag text (the bodies of emails)

# each flag will have a 
  # - position (index within the string)
  # - type (e.g. isSubRequest or isCover or isLead or weekday or time or type)
  # - value (e.g. True, or "wednesday", or "nameOverride")
  # - priority (to deal with conflicting flags), higher is higher priority

class Flag:
  def __init__(self, position, type, value, priority = 3):
    self.position = position
    self.type = type
    self.value = value
    self.priority = priority

  def __repr__(self):
    return f"{self.type}: {self.value} @{self.position} (priority {self.priority})"