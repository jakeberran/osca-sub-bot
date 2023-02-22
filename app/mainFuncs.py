from steps.reader.reader import readEmails
from steps.parser.parser import parseEmail
from steps.handler.handler import handleActions
from steps.writer.writer import writeEmail
from steps.sender.sender import sendEmail
from decouple import config
from datetime import datetime
from helpers.db import getDB, overwriteDB, updateTopId
import logging
import dotenv
import os
logger = logging.getLogger('app')

def readParseAndHandle(readNemails = False):
  logger.info('\n\nSTARTING APP...')
  
  # get in the new emails
  inMessages, topId = readEmails(config('DATABASE_PATH'), readNEmails=readNemails)

  # for each one, run it through the text parser to parse it into actions (add <entry>, delete <thing>)
  actions = []
  for message in inMessages:
    newActions = parseEmail(message)
    actions.extend(newActions)

  # handle the actions by updating the temp database
  handleActions(config('DATABASE_PATH'), actions)

  # update the top id only after we've done everything
  updateTopId(topId, config('DATABASE_PATH'))

def getCurrentSubRequests():
  return getDB(config('DATABASE_PATH'))['subRequests']

def updateSubRequests(subRequestsList):
  topId = getDB(config('DATABASE_PATH'))['lastIdProcessed']
  dct = {
    'lastIdProcessed': topId,
    'subRequests': subRequestsList
  }
  overwriteDB(dct, config('DATABASE_PATH'))

def updateDatabasePath():
  # Set the non-settable variables
  dotenv_file = dotenv.find_dotenv()
  dotenv.load_dotenv(dotenv_file)

  if config('TESTING', default=True, cast=bool):
    databasePath = 'app/data/testDatabase.json'
  else:
    databasePath = 'app/data/database.json'
  
  os.environ['DATABASE_PATH'] = databasePath
  dotenv.set_key(dotenv_file, 'DATABASE_PATH', os.environ['DATABASE_PATH'])

def writeAndSend(testing = True):
  # Set variables for writing the email
  From = "Sub Bot"
  test_to = config('TEST_TO_EMAIL')
  real_to = config('REAL_TO_EMAIL')
  
  date_string = datetime.now().strftime("%A, %m/%d (%I:%M %p)")
  subject = f"\U0001F916 Daily Subs | {date_string} {'(TESTING)' if testing else ''}"

  try:
    if len(getDB(config('DATABASE_PATH'))['subRequests']) == 0:
      logger.info('No new sub requests. No email will send.')
      return 0

    # write the email
    if testing:
      to = test_to
    else:
      to = real_to

    sendParams = writeEmail(From, to, subject, config('DATABASE_PATH'))

    sendEmail(*sendParams)

    return 1

  except Exception as e:
    logger.error('Error in writing and sending the email:' + str(e))
    return -1

# If running this script directly (e.g. for testing), then just call runApp()
if __name__ == "__main__":
  logging.basicConfig(
    format='%(levelname)s: %(message)s', 
    level=logging.INFO, # logging.DEBUG or logging.INFO
    filename='app/debugging.log',
    filemode='a',
    datefmt='%H:%M:%S'
  )

  readParseAndHandle()
  writeAndSend(testing=True)