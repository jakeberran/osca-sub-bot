# To easily load and overwrite JSON files

from decouple import config
import json

testing = config('TESTING', default=True, cast=bool)

def getDB(databasePath):
  with open(databasePath, 'r') as f:
    strData = f.read()
  
  dictData = json.loads(strData) # load as python dictionary
  return dictData

def overwriteDB(dict, databasePath):
  jsonString = json.dumps(dict, indent=2)

  # Open in overwrite mode
  with open(databasePath, 'w') as f:
    f.write(jsonString)

def updateTopId(id, databasePath):
  dictData = getDB(databasePath)
  dictData['lastIdProcessed'] = id
  overwriteDB(dictData, databasePath)