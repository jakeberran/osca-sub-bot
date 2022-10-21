from decouple import config
import json

testing = config('TESTING')
defaultDatabasePath = 'app/testDatabase.json' if testing else 'app/database.json'

def getDB(databasePath=defaultDatabasePath):
  with open(databasePath, 'r') as f:
    strData = f.read()
  
  dictData = json.loads(strData) # load as python dictionary
  return dictData

def overwriteDB(dict, databasePath=defaultDatabasePath):
  jsonString = json.dumps(dict, indent=2)

  # Open in overwrite mode
  with open(databasePath, 'w') as f:
    f.write(jsonString)

def updateTopId(id, databasePath=defaultDatabasePath):
  dictData = getDB(databasePath)
  dictData['lastIdProcessed'] = id
  overwriteDB(dictData, databasePath)