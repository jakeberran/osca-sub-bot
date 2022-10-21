# replace this with the actual python email object if it ever makes sense to
import json

class Email:
  def __init__(self, id = '', From = '', subject = '', body = '', contentType = 'text/plain', timestamp = None):
    self.id = id
    self.From = From
    self.subject = subject
    self.body = body
    self.contentType = contentType
    self.timestamp = timestamp
  
  def __str__(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
    # return f"id: {self.id},\nFrom: {self.From},\nsubject: {self.subject},\nbody: {self.body}"
