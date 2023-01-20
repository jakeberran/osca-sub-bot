import imaplib
import email
from email.header import decode_header
import json
from decouple import config
import os
import webbrowser
from datetime import datetime
import logging
logger = logging.getLogger('reader')

from classes.EmailClass import Email # custom email class, use the provided email module when ready
from helpers.db import getDB, overwriteDB, updateTopId

def readEmails(databasePath, inbox = 'INBOX', outputJsonPath = False, readNEmails = False):
  username = config('EMAIL_USERNAME') # os.environ["EMAIL_USERNAME"]
  password = config('EMAIL_PASSWORD') # os.environ["EMAIL_PASSWORD"]
  imap_server = config('IMAP_SERVER') # os.environ["IMAP_SERVER"]
  
  try:
    logger.info('Logging into the IMAP server...')
    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)
  except Exception as e:
    raise Exception('There was an issue logging into the IMAP server.')
  logger.info('Successfully logged in.\n')

  # Log folder names in debugging mode (no spaces works best)
  logger.debug('FOLDERS FOUND:')
  for i in imap.list()[1]:
    l = i.decode().split(' "/" ')
    logger.debug(i)
    logger.debug(l[0] + " = " + l[1])
  
  status, emails = imap.select(inbox) # imap.select("INBOX")

  # total number of emails
  topId = int(emails[0]) # the count of messages in the inbox, or top id
  logger.info('Top email ID: ' + str(topId))

  logger.debug('Updating most recent email ID read...')
  try:
    # get the stored previous top email id
    data = getDB(databasePath)
      
    previousTopId = data['lastIdProcessed'] # get the previous top id
    logger.info('Previous top ID was ' + str(previousTopId))
    data['lastIdProcessed'] = topId # replace with the new top id

    with open('app/topIdLog.csv', 'a') as f:
      f.write(f'\n{datetime.now().isoformat() },{topId}')

    # read N emails if testing
    if readNEmails != False:
      previousTopId = topId - int(readNEmails)

  except:
    raise Exception('There was a problem updating the most recent email ID.')
  logger.debug('Update successful.\n')

  imap.list()

  messages = []

  logger.info('Reading new emails...')
  for i in range(topId, previousTopId, -1):
      # fetch the email message by ID
      res, msg = imap.fetch(str(i), "(RFC822)")

      message = Email()
      message.id = i

      for response in msg:
          if isinstance(response, tuple):
              # parse a bytes email into a message object
              msg = email.message_from_bytes(response[1])
              # logger.debug(msg) # for testing, this really gets you a LOT of logging

              # decode the email subject
              subject, encoding = decode_header(msg["Subject"])[0]
              if isinstance(subject, bytes):
                  # if it's a bytes, decode to str
                  subject = subject.decode(encoding)

              # decode email sender
              From, encoding = decode_header(msg.get("From"))[0]
              if isinstance(From, bytes):
                  From = From.decode(encoding)

              # decode email timestamp
              timestamp, encoding = decode_header(msg.get("Date"))[0]
              if isinstance(timestamp, bytes):
                  From = From.decode(encoding)

              # set these properties on the message
              message.subject = subject
              message.From = From
              try:
                message.timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %z').isoformat()
              except:
                try:
                  message.timestamp = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z').isoformat()
                except Exception as e:
                  logger.error(e)
              # if the email message is multipart
              if msg.is_multipart():
                  # iterate over email parts
                  for part in msg.walk():
                      # extract content type of email
                      content_type = part.get_content_type()
                      content_disposition = str(part.get("Content-Disposition"))
                      try:
                          # get the email body
                          body = part.get_payload(decode=True).decode()
                      except:
                          pass
                      if content_type == "text/plain" and "attachment" not in content_disposition:
                          message.body = body

                      # skip attachments
                      elif "attachment" in content_disposition:
                          break
                          # download attachment
                          filename = part.get_filename()
                          if filename:
                              folder_name = clean(subject)
                              if not os.path.isdir(folder_name):
                                  # make a folder for this email (named after the subject)
                                  os.mkdir(folder_name)
                              filepath = os.path.join(folder_name, filename)
                              # download attachment and save it
                              open(filepath, "wb").write(part.get_payload(decode=True))
              
              # message is single-part
              else:
                  try:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # take only text email parts
                        message.body = body
                  except:
                    logger.error(f'ERROR DECODING MESSAGE: {msg}')
                    continue
              if content_type == "text/html":
                  break
                  # if it's HTML, create a new HTML file and open it in browser
                  folder_name = clean(subject)
                  if not os.path.isdir(folder_name):
                      # make a folder for this email (named after the subject)
                      os.mkdir(folder_name)
                  filename = "index.html"
                  filepath = os.path.join(folder_name, filename)
                  # write the file
                  open(filepath, "w").write(body)
                  # open in the default browser
                  webbrowser.open(filepath)
      
      # add to the messages
      messages.append(message)
  
  # Reverse the messages so the oldest one is processed first
  messages.reverse()

  logger.info(f'Read {topId - previousTopId} new email' + ('.' if topId - previousTopId == 1 else 's.') + '\n')
  
  logger.info('Logging out of IMAP server...')
  # close the connection and logout
  imap.close()
  imap.logout()
  logger.info('Logged out.')

  if (outputJsonPath != False):
    msgsAsDicts = [vars(m) for m in messages]
    with open(outputJsonPath, 'w') as f:
      f.write(json.dumps(msgsAsDicts, indent=2))

  return messages, topId

# For testing
if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
  messages, topId = readEmails(databasePath= config('DATABASE_PATH'), inbox='INBOX', outputJsonPath='autoreplyEmail.json')

  updateTopId(topId, config('DATABASE_PATH'))

  # for message in messages:
  #   logger.debug(message)
  # logger.debug(('\n\n' + "="*100 + '\n\n').join(map(str, messages)))