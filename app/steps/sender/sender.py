# skipped your comments for readability
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
import os
import logging
logger = logging.getLogger('sender')

def sendEmail(From, to, subject, body):
  username = config('EMAIL_USERNAME') # os.environ["EMAIL_USERNAME"] # for Azure
  password = config('EMAIL_PASSWORD') # os.environ["EMAIL_PASSWORD"]
  smtp_server = config('SMTP_SERVER') # os.environ["SMTP_SERVER"]
  
  logger.info('========== SENDING EMAIL ==========')

  msg = MIMEMultipart('alternative')
  msg['Subject'] = subject
  msg['From'] = From
  msg['To'] = to

  part2 = MIMEText(body, 'html') 
  # formats the email correctly for normal email readers
  # change html to ??? if you're just doing plain text

  # Add the body to the message
  msg.attach(part2)

  # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
  s = smtplib.SMTP_SSL(smtp_server)
  
  # uncomment if interested in the actual smtp conversation
  # s.set_debuglevel(1)
  
  # do the smtp auth; sends ehlo if it hasn't been sent already
  s.login(username, password)

  # send the email
  s.sendmail(From, to, msg.as_string())

  # quit the SMTP connection
  s.quit()

  logger.info('Email sent successfully.')

# For testing
if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
  # Get the test HTML file.
  thisDir = 'app/steps/writer/'
  inFile = thisDir + 'result.html'

  with open(inFile, 'r') as f:
    From = "Sub Bot"
    to = config('TEST_TO_EMAIL')
    
    date_string = datetime.now().strftime("%A, %m/%d %H:%M")
    subject = f"\U0001F916 Daily Subs | {date_string}"
    
    test_body = f.read()

    sendEmail(From, to, subject, test_body)