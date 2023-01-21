# Goal - convert datetimes into shift info and vice versa

from datetime import datetime
import logging
logger = logging.getLogger('shifts')

DATE_FORMAT = '%m/%d'
TIME_FORMAT = '%I:%M %p'

shiftTypes = {
  '08:20 AM': 'Breakfast Crew',
  '09:20 AM': 'Lunch Cook',
  '10:20 AM': 'Lunch Cook',
  '11:20 AM': 'Lunch Cook',
  '11:50 AM': 'Lunch Pre-Crew',
  '01:00 PM': 'Lunch Crew',
  '03:20 PM': 'Dinner Cook',
  '04:20 PM': 'Dinner Cook',
  '05:20 PM': 'Dinner Cook',
  '05:50 PM': 'Dinner Pre-Crew',
  '07:00 PM': 'Dinner Crew',
  '08:30 PM': 'Commando Crew'
}

# This function should not be applied to head cook shifts
# This function should be used only in writer.py, really
def datetimeToShiftInfo(dateTime):
  '''
  Takes a datetime or a string in ISO 8601 format and converts it to a shift (dict)
  '''
  if isinstance(dateTime, str):
    dateTime = datetime.fromisoformat(dateTime)
    if (dateTime - datetime.now()).days > 100:
      logger.warning(f'\U0001F6A8 Shift over 100 days in the future (skipping): { shiftInfo }')
      return

  shiftInfo = {}

  print(dateTime)
  shiftInfo['date'] = dateTime.strftime(DATE_FORMAT)
  shiftInfo['weekday'] = dateTime.strftime("%A")
  shiftInfo['time'] = dateTime.strftime(TIME_FORMAT)
  try:
    shiftInfo['type'] = shiftTypes[shiftInfo['time']]
    return shiftInfo
  except KeyError:
    logger.warning(f'\U0001F6A8 Invalid shift time (skipping): { shiftInfo }')
    return

def shiftInfoToDatetime(shift):
  '''
  Takes a shift info (dict with date, weekday, time, and type) and converts it to a datetime
  '''
  if 'datetime' not in shift.keys() and all(k in shift.keys() for k in ['date', 'time']):
    # todo fill this out

    month, day = shift['date'].split('/')

    try:
      time12 = datetime.strptime(shift['time'], "%I:%M %p")
      time24 = datetime.strftime(time12, "%H:%M")
      hour, minutes = time24.split(':')

      dt = datetime(datetime.now().year, int(month), int(day), int(hour), int(minutes), 0, 0)
      
      
      return dt.isoformat()
    except:
      logger.error('Error getting datetime from shift in shiftInfoToDatetime')

  else:
    return shift['datetime'] # an ISO 8601 string

def isOver(shift):
  try:
    dt = datetime.fromisoformat(shiftInfoToDatetime(shift))
    return dt < datetime.now()
  except:
    logger.error('Could not determine if the following shift is over: ' + str(shift))
    return True

# For testing
if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

  shift = datetimeToShiftInfo('2022-09-25T09:20:00.000')
  dt = shiftInfoToDatetime({
    'date': '8/16',
    'time': '10:20 AM'
  })
  logger.debug(shift)
  logger.debug(dt)