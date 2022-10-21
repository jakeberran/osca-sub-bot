import jinja2
from helpers.db import getDB
from helpers.shifts import datetimeToShiftInfo
from datetime import datetime, timedelta
import copy
from decouple import config
import logging
logger = logging.getLogger('writer')

ggroup = config('TO_EMAIL')

def writeEmail(From, to, subject, databasePath):
  logger.info('========== WRITING EMAIL ==========')

  # The directory of this script relative to /osca-sub-bot/, useful for accessing template.html and result.html
  thisDir = 'app/steps/writer/'
  templatePath = thisDir + 'template.html'
  resultPath = thisDir + 'result.html'

  # Grab sub requests from the database
  subRequests = copy.deepcopy(getDB(databasePath)['subRequests'])

  subRequests.sort(key = lambda r: datetime.fromisoformat(r['shift']['datetime']))

  validRequests = []

  for i, r in enumerate(subRequests):
    shiftInfo = datetimeToShiftInfo(r['shift']['datetime'])
    if shiftInfo:
      for key in shiftInfo.keys():
        subRequests[i]['shift'][key] = shiftInfo[key]
      
      # Set the end time to one hour after the shift time
      subRequests[i]['shift']['endDatetime'] = datetime.isoformat(datetime.fromisoformat(r['shift']['datetime']) + timedelta(hours = 1))

      # Edit the info if it is a Head Cook / PIC shift
      if r['shift']['isLead']:
        meal, Type = r['shift']['type'].split(' ')
        if Type.lower() == 'cook':
          subRequests[i]['shift']['type'] = meal + ' Head Cook'

          # Update the end time to three hours after the shift time
          subRequests[i]['shift']['endDatetime'] = datetime.isoformat(datetime.fromisoformat(r['shift']['datetime']) + timedelta(hours = 3))
        elif Type.lower() == 'crew':
          subRequests[i]['shift']['type'] = meal + ' PIC'

      # Edit info if it is a special meal, and not Head/PIC
      elif r['shift']['isSpecial']:
        meal, Type = r['shift']['type'].split(' ')
        if Type.lower() == 'cook':
          subRequests[i]['shift']['type'] = 'Special Meal Cook'
          # Update the end time to three hours after the shift time
          subRequests[i]['shift']['endDatetime'] = datetime.isoformat(datetime.fromisoformat(r['shift']['datetime']) + timedelta(hours = 3))

      validRequests.append(subRequests[i])

  logger.info(f'{len(validRequests)} valid sub requests will be included in the email.')

  # Write the email HTML using the template.
  body = jinja2.Environment(
    loader = jinja2.FileSystemLoader('./')
  ).get_template(templatePath).render(
    subRequests = validRequests, 
    today = datetime.now().strftime("%m/%d"),
    ggroup = ggroup,
    subsBotEmail = config('EMAIL_USERNAME')
  )

  with open(resultPath,'w') as f: f.write(body) # overwrites old result.html
  return (From, to, subject, body)

if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
  writeEmail(config('EMAIL_USERNAME'), config('TO_EMAIL'), 'Testing writer.py', config('DATABASE_PATH'))

# Dump for template
# {% if r['isNew'] %} background-color: rgb(255, 255, 0, 0.8); {% elif r['isBoosted'] %} background-color: rgb(86, 249, 255, 0.3); {% endif %}