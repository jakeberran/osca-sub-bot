from steps.reader.reader import readEmails
from steps.parser.parser import parseEmail
from steps.handler.handler import handleActions
from steps.writer.writer import writeEmail
from steps.sender.sender import sendEmail
from decouple import config
from datetime import datetime
from helpers.db import getDB, updateTopId
import logging
logger = logging.getLogger('app')

def runApp(readNemails = False):
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

  # Set variables for writing the email
  From = "Sub Bot"
  to = config('TO_EMAIL')
  
  date_string = datetime.now().strftime("%A, %m/%d (%I:%M %p)")
  subject = f"\U0001F916 Daily Subs | {date_string}"

  try:
    if len(getDB(config('DATABASE_PATH'))['subRequests']) == 0:
      logger.info('No new sub requests. No email will send.')
      return

    # write the email
    sendParams = writeEmail(From, to, subject, config('DATABASE_PATH'))

    sendEmail(*sendParams)

    # update the top id only after we've done everything
    updateTopId(topId, config('DATABASE_PATH'))

    return

  except:
    logger.error('Error in writing and sending the email.')
    return

# If running this script directly (e.g. for testing), then just call runApp()
if __name__ == "__main__":
  logging.basicConfig(
    format='%(levelname)s: %(message)s', 
    level=logging.INFO, # logging.DEBUG or logging.INFO
    filename='app/debugging.log',
    filemode='a',
    datefmt='%H:%M:%S'
  )

  runApp()