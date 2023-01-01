# Parses email content into actions (e.g. add an entry, delete an entry, boost an entry)
# helperRegexs.py has all the patterns, this file can be for the more detailed processing


import json
from classes.EmailClass import Email
from classes.Action import Action
from classes.FunctionWithAppendedArguments import FunctionWithAppendedArguments
import regex as re
from classes.Flag import Flag
from datetime import datetime, timedelta
import types
import logging
import copy
logger = logging.getLogger('parser')

# GLOBALS
DATE_FORMAT = '%m/%d'
TIME_FORMAT = '%I:%M %p'
NOW = datetime.now()

# Matching strings for different flags
requestTypePatterns = {
  '\\b(sub|subbing|subbed|subs|sub\\?|(someone|anyone|please|plz) cover|cover my|fill in|take my|take over|swap|trade)\\b': 'sub',
  "(data for sub bot sub \\(please don't delete\\):)": 'subAuto',
  '\\b(cover(ed|ing)|i can (sub|cover|take)|all good)\\b': 'cover',
  "(data for sub bot cover \\(please don't delete\\):)": 'coverAuto',
  '\\b((boost|bump)(|ing))\\b': 'boost'
}

shiftTypePatterns = {
  '\\b((breakfast|brekkie) crew)\\b': 'breakfast crew',
  '\\b(pre(| |-)crew)\\b': 'pre-crew',
  '\\b((\\w*(?<!pre(| |-))crew(|s))|(pic))\\b': 'crew',
  '\\b(commando)\\b': 'commando',
  '\\b(cook|cookshift)\\b': 'cook'
}

mealPatterns = {
  '\\b(lunch|lonch)\\b': 'lunch',
  '\\b(dinner|din)\\b': 'dinner',
  '\\b(pizza|zza)\\b': 'pizza'
}

miscPatterns = {
  '\\b(head(| |-)cook|pic)\\b': 'lead',
  '\\b(special meal)\\b': 'special'
}

textPatterns = {
  '((\\r\\n\\r\\n)|((?<!\\r\\n)(\\r\\n)(?!\\r\\n)))': 'newline' # matches single or double
}

# todo store all these globally somewhere
shiftTypeTimes = {
  'breakfast crew': ['08:20 AM'],
  'pre-crew': ['11:50 AM', '05:50 PM'],
  'crew': ['08:20 AM', '01:00 PM', '07:00 PM'],
  'commando': ['08:30 PM'],
  'cook': ['09:20 AM', '10:20 AM', '11:20 AM', '03:20 PM', '04:20 PM', '05:20 PM']
}

mealTimes = {
  'lunch': ['11:50 AM', '01:00 PM', '09:20 AM', '10:20 AM', '11:20 AM'],
  'dinner': ['05:50 PM', '07:00 PM', '03:20 PM', '04:20 PM', '05:20 PM'],
  'pizza': ['05:50 PM', '07:00 PM', '03:20 PM', '04:20 PM', '05:20 PM']
}

miscTimes = {
  'lead': ['09:20 AM', '01:00 PM', '03:20 PM', '07:00 PM'],
  'special': ['09:20 AM', '01:00 PM', '03:20 PM', '07:00 PM']
}

allShiftTimes = []
for times in shiftTypeTimes.values():
  allShiftTimes = list(set(allShiftTimes + times))


'''
========== DATES ==========
'''
next14days = []
for i in range(14):
  next14days.append((datetime.today() + timedelta(days=i)).strftime(DATE_FORMAT))

# As a helper for the date patterns
weekdayPatterns = {
  '(monday|mon)': 0,
  '(tuesday|tue|tues)': 1,
  '(wednesday|wed)': 2,
  '(thursday|thu|thurs)': 3,
  '(friday|fri)': 4,
  '(saturday|sat)': 5,
  '(sunday|sun)': 6
}

monthPatterns = {
  '(jan|january)': 1,
  '(feb|february|febuary)': 2,
  '(mar|march)': 3,
  '(apr|april)': 4,
  '(may)': 5,
  '(jun|june)': 6,
  '(jul|july)': 7,
  '(aug|august)': 8,
  '(sep|sept|september)': 9,
  '(oct|october)': 10,
  '(nov|november)': 11,
  '(dec|december)': 12
}

# valid date day numbers
validDayNum = '((3[0-1])|([1-2][0-9])|([1-9]))'
validDaySuffixes = '(st|nd|rd|th)'

# weekdays, months
abbrWeekday = '(sun|mon|tue|wed|thu|fri|sat)'
spAbbrWeekday = '(lun|mar|mie|jue|vie|s\u00e1b|dom)'
abbrMonth = '(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
fullMonth = '(january|february|march|april|may|june|july|august|september|october|november|december)'
numericDate = '[0-9]{1,2} ?\\/ ?[0-9]{1,2}'

# Handler for today/tomorrow
# TODO check these
def handleToday(s, date): # s is placeholder for the match, which is unimportant
  logger.info(f'handling tomorrow relative to {date}')
  if date == False:
    today = datetime.today()
  else:
    today = datetime.strptime(date, DATE_FORMAT)
  return today.strftime(DATE_FORMAT)

def handleTomorrow(s, date):
  logger.info(f'handling tomorrow relative to {date}')
  if date == False:
    tomorrow = datetime.today() + timedelta(days=1)
  else:
    tomorrow = datetime.strptime(date, DATE_FORMAT) + timedelta(days=1)
  return tomorrow.strftime(DATE_FORMAT)

# Handler for "the 3rd", etc.
def handleTheDay(s, date):
  try:
    day = re.findall('\\d+', s)[0] # extract the day number
    month = str(NOW.month if NOW.day < int(day) else NOW.month + 1)
    return f'{day.zfill(2)}/{month.zfill(2)}'
  except:
    logger.error(f'No day number found in {s} relative to {date}')

# Handler for this week
def handleThisWeek(s, date, targetWeekday):
  logger.info(f'handling this {targetWeekday} relative to {date}')
  if date == False:
    refDate = datetime.today()
  else:
    refDate = datetime.strptime(date, DATE_FORMAT)
  refWeekday = (refDate.weekday() - 2) % 7
  logger.info('reference weekday is ' + str(refWeekday))

  if refWeekday == targetWeekday:
    daysToAdd = 7
  else:
    daysToAdd = (targetWeekday - refWeekday) % 7 # behaves correctly for negatives

  logger.info(daysToAdd)
  logger.info('got ' + (refDate + timedelta(days = daysToAdd)).strftime(DATE_FORMAT))
  return (refDate + timedelta(days = daysToAdd)).strftime(DATE_FORMAT)

# Handler for next week
def handleNextWeek(s, date, targetWeekday):
  
  logger.info(f'handling next {targetWeekday} relative to {date}')
  if date == False:
    refDate = datetime.today()
  else:
    refDate = datetime.strptime(date, DATE_FORMAT)
  refWeekday = (refDate.weekday() - 2) % 7
  logger.info('reference weekday is ' + str(refWeekday))

  if refWeekday == targetWeekday:
    daysToAdd = 7
  else:
    daysToAdd = (targetWeekday - refWeekday) % 7 # behaves correctly for negatives

  if refWeekday == targetWeekday:
    return (refDate + timedelta(days = daysToAdd)).strftime(DATE_FORMAT)
  else:
    return (refDate + timedelta(days = daysToAdd + 7)).strftime(DATE_FORMAT)

# For each pattern, a parsing function to coerce it into standard format (HH:MM with no am/pm???)
datePatterns = {
  '\\b(today|tonight|tn|tonite)\\b': handleToday,
  '\\b(tomorrow|tmrw)\\b': handleTomorrow,
  f'\\b(the {validDayNum}{validDaySuffixes})\\b': handleTheDay
}

# Append datePatterns with feb 8th and 2/8
for i, key in enumerate(monthPatterns.keys()):
  datePatterns[f'\\b{key} {validDayNum}{validDaySuffixes}?\\b'] = monthPatterns[key] # 1,2,3 etc. (yes this allows 30nd)
  datePatterns[f'\\b({i+1} ?(\\/) ?{validDayNum})\\b'] = monthPatterns[key]
  # TODO decide if dash should be allowed as date separator

handleThisWeekWrappers = []
handleNextWeekWrappers = []

# Append datePatterns with weekdays, including "next (weekday)"
# With negative lookahead to rule out "Tuesday, 7/14"
for i, weekday in enumerate(weekdayPatterns.keys()):
  thisWeekKey = f'\\b(\\w*(?<!next ){weekday}(?!,? ({abbrMonth}|{fullMonth}|{numericDate})))\\b'
  nextWeekKey = f'\\b(next {weekday}(?!,? ({abbrMonth}|{fullMonth}|{numericDate})))\\b'

  # TODO from 10/26 figure this out, it is always having 6 as the target weekday, so something bad is happening here

  datePatterns[thisWeekKey] = FunctionWithAppendedArguments(handleThisWeek, i)

  datePatterns[nextWeekKey] = FunctionWithAppendedArguments(handleNextWeek, i)

for key in datePatterns.keys():
  if callable(datePatterns[key]):
    datePatterns[key]('sunday', '10/12')

# Formats a date string nicely (take in the monthNum)
def handleDateStr(dateStr = '', monthNum = 1):
  # strip off the st|nd|rd|th if needed
  if not dateStr[-1].isnumeric():
    dateStr = dateStr[:-2]
  dayNum = re.split('[\\/ ]', dateStr)[-1].replace(' ', '').zfill(2)
  return f'{str(monthNum).zfill(2)}/{dayNum}'


'''
========== TIMES ==========
'''
def handleSingleTimeStr(timeStr):
  timeStr = timeStr.replace('at', '').replace(' ', '')
  parts = re.split('[:\\.pa ]', timeStr)
  hours = parts[0].zfill(2)

  # set minutes
  if len(parts) >= 2:
    if parts[1].isnumeric():
      minutes = parts[1].zfill(2)
    else:
      minutes = '00'
  else:
    minutes = '00'

  if 'am' in timeStr or 'a.m' in timeStr:
    m = 'AM'
  elif 'pm' in timeStr or 'p.m' in timeStr:
    m = 'PM'
  else: # defaults to 9am-8pm (can be overridden by breakfast crew later on)
    if int(hours) > 8 and int(hours) < 12:
      m = 'AM'
    elif int(hours) <= 8 or int(hours) == 12:
      m = 'PM'

  return f'{hours}:{minutes} {m}'
  # return HH:MM AM|PM

# Time ranges; "3:20 and 4:20"
_timeRangeConnector = 'to|-|and|through' # for the splitting
timeRangeConnector = f' ?({_timeRangeConnector}) ?' # the real one

def handleTimeRangeStr(timeRangeStr):
  startStr, endStr = re.split(_timeRangeConnector, timeRangeStr.replace(' ', '')) # remove whitespace first then split
  start = handleSingleTimeStr(startStr)
  end = handleSingleTimeStr(endStr)

  # Fix cases like 8-9 converting to 8pm-9am
  if start[-2:] == 'PM' and end[-2:] == 'AM':
    end = end[:-2] + 'PM' # more likely to be commando than breakfast if no other info?
  
  # If "and" was the separator, then the end time is actually an hour after
  if 'and' in timeRangeStr:
    end = (datetime.strptime(end, TIME_FORMAT) + timedelta(hours=1)).strftime(TIME_FORMAT)
  
  return start, end

# TIME REGEXS
standardTime = '((1[0-2]|0?[1-9])(:|\\.)([0-5][0-9]) ?([AaPp]\\.?[Mm]\\.?)?)'
atTime = '((at (1[0-2]|0?[1-9]))(?!:) ?([AaPp]\\.?[Mm]\\.?)?)'
hourOnlyTime = '((1[0-2]|0?[1-9]) ?([AaPp]\\.?[Mm]\\.?))'
singleTime = f'({standardTime}|{atTime}|{hourOnlyTime})'

singleTime = f'(?<!{singleTime}{timeRangeConnector}){singleTime}(?!{timeRangeConnector}{singleTime})'

timeRange = f'((1[0-2]|0?[1-9])((:|\\.)([0-5][0-9]))? ?([AaPp]\\.?[Mm]\\.?)?){timeRangeConnector}((1[0-2]|0?[1-9])((:|\\.)([0-5][0-9]))? ?([AaPp]\\.?[Mm]\\.?)?)'

timePatterns = {
  f'\\b({singleTime})\\b': handleSingleTimeStr,
  f'\\b({timeRange})\\b': handleTimeRangeStr # precedence over the last one
}



'''
========== THE ACTUAL FUNCTIONS ==========
'''
def parseEmail(message):
  logger.info('===== PARSING EMAIL CONTENT =====')
  # Set id, name, email, sentTime, isNew right off the bat,
  # will apply to all actions
  id = message.id

  # check if it has the Name <Email> format
  if '<' in message.From and '>' in message.From:
    name, email = message.From.replace('>', '').split('<')
    if name == '':
      name = email
    else:
      name = name.strip()
  else:
    name = email = message.From

  sentDatetime = message.timestamp

  logger.info(name + ', ' + email)

  # work in lowercase to not go crazy
  body = message.body.lower()

  # Use regex to split the body into messages, 
  # then the original email is the last one (if last != first) and the
  # email being processed is the first one
  convoSplitter = f"\\b((on {abbrWeekday}, {abbrMonth} {validDayNum})|(on {abbrMonth} {validDayNum}, 20[0-9][0-9])|(el {spAbbrWeekday}))\\b"

  splitters = re.finditer(convoSplitter, body)
  splitters = [s for s in splitters]
  splitMessage = []

  if len(splitters) > 0:
    leftIndex = 0

    # the first (newest) part has datetime of whenever the email was sent
    partDatetime = sentDatetime
    for i, match in enumerate(splitters):
      start, end = match.span(0)
      rightIndex = start
        
      splitMessage.append((partDatetime, body[leftIndex:rightIndex]))

      # gather the part datetime of the next part before going to the next iteration or moving on
      if i != 0:
        dateInfo = body[start:end]
        dateInfo = dateInfo[dateInfo.index(' ') + 1:]
        try:
          partDatetime = datetime.strptime(dateInfo, '%a, %b %-d').isoformat()
        except:
          try:
            partDatetime = datetime.strptime(dateInfo, '%b %-d, %Y').isoformat()
          except:
            partDatetime = NOW.isoformat()

      # Start looking where we left off
      leftIndex = end

    # add the oldest part on
    splitMessage.append((partDatetime, body[leftIndex:]))
  else:
    splitMessage.append((sentDatetime, body))
  
  messageParts = []

  for i, temp in enumerate(splitMessage): # this is what gmail does #TODO make sure there's no other ways they write it
    # the first email in the chain will not have the <address> wrote: [actual body]
    if i == 0:
      tempSender = email # the sender of the email passed into this function
      tempBody = temp[1]
    else:
      if temp[1]:
        possibleEmails = re.findall('[ <]([a-zA-Z0-9-.\r\n]*@oberlin.edu)[ >]?', temp[1]) # prioritize the @oberlin.edu
        possibleEmails.extend(re.findall('<(.*@.*)>', temp[1]))
        if len(possibleEmails) > 0:
          tempSender = possibleEmails[0] # will get the sender email address of this email in the chain
          tempBody = re.split('wrote:|escrib', temp[1], maxsplit=1)[-1] # body is the part after "<address> wrote:" 
          # todo is this what we want?
        else:
          logger.warn('Could not find an email address in: ' + temp[1])
          continue # skip over the append
    
    # add on the datetime that part was sent
    try:
      tempDate = datetime.fromisoformat(temp[0]).strftime(DATE_FORMAT)
    except:
      tempDate = False
        
    messageParts.append({'senderEmail': tempSender, 'sentDate': tempDate, 'body': tempBody})
  
  if len(messageParts) > 1:
    logger.debug(f'Split into a conversation of {len(messageParts)} messages.')

  if len(messageParts) == 0:
    logger.error('SKIPPING AN EMAIL: ' + body[:50])
    return

  this = messageParts[0]
  orig = messageParts[-1]
  # add the subject to the start of the original message
  orig['body'] = message.subject.lower() + '\n' + orig['body']

  # todo separate out flags and shift helpers into different files?
  newFlags = makeFlags(this['body'], this['sentDate'])
  origFlags = makeFlags(orig['body'], orig['sentDate'])

  thisSender = this['senderEmail']
  origSender = orig['senderEmail']

  def flagLines(flagList):
    flagList = list(filter(lambda f: f.value != 'newline', flagList))
    return map(lambda arr: str(arr), flagList)

  # Log flags
  if len(messageParts) == 1:
    logger.debug(f'Email <{origSender}> flags:\n\t' + '\n\t'.join(flagLines(origFlags)))

  else:
    logger.debug(f'Original email <{origSender}> flags:\n\t' + '\n\t'.join(flagLines(origFlags)))
    logger.debug(f'\nNew email <{thisSender}> flags:\n\t' + '\n\t'.join(flagLines(newFlags)))



  '''
  ========== FLAGS INTO ACTIONS ==========
  '''
  actions = []

  # PARSE ORIGINAL EMAIL

  # Auto-filled sub
  if hasFlag(origFlags, value='subAuto'):
    dataStr = orig['body'].split("data for sub bot sub (please don't delete):")[-1].replace('\r', '').replace('\n', '').replace(' ', '')

    sub, requesterEmail, requesterDatetime, isLead, isSpecial = dataStr.split(',')
    
    isLead = True if isLead == 'islead=true' else False
    isSpecial = True if isSpecial == 'isspecial=true' else False
    
    actions.append(Action('add', {
      'sender': {
        'email': requesterEmail
      },
      'shift': {
        'datetime': requesterDatetime.replace('t', 'T'),
        "isLead": isLead,
        "isSpecial": isSpecial
    }}))
    return actions # finish up, this was an auto-filled reply

  # Auto-filled cover
  if hasFlag(origFlags, value='coverAuto'):
    dataStr = orig['body'].split("data for sub bot cover (please don't delete):")[-1].replace('\r', '').replace('\n', '').replace(' ', '')

    covered, requesterEmail, requesterDatetime = dataStr.split(',')
    actions.append(Action('delete', {
      'sender': {
        'email': requesterEmail
      },
      'shift': {
        'datetime': requesterDatetime.replace('t', 'T')
    }}))
    return actions # finish up, this was an auto-filled reply

  # Orig email is sub request
  if hasFlag(origFlags, value='sub'):
    origShifts = flagsToShifts(origFlags, False)

    # Plain sub request
    if len(messageParts) == 1:
      for shift in origShifts:
        actions.append(Action('add', {
          'shift': shift
        }))

    # Covering
    elif hasFlag(newFlags, value='cover'): # we are dealing with a possible cover or boost
      shiftsCovered = flagsToShifts(newFlags, True) # if not fully specific, will try to delete all possible shifts it may refer to
      
      if len(shiftsCovered) == 0: # assume covering all, if no specific info can be found
        shiftsToDelete = origShifts
      else: # future todo make this more robust, allow weaker information
        shiftsToDelete = shiftsCovered

      for shift in shiftsToDelete:
        actions.append(Action('delete', {
          'shift': shift # will only need datetime but that's ok
        }))

    # If boosting, just boost all of them
    elif hasFlag(newFlags, value='boost'):
      for shift in origShifts:
        actions.append(Action('boost', {
          'shift': shift # will only need datetime but that's ok
        }))
        # if they are already deleted, the boosting will do nothing anyway

    elif hasFlag(newFlags, value='sub'):
      shiftsRequested = flagsToShifts(newFlags, False) # not treating as a "cover" (cartesian product delete targeting) anymore

      for shift in shiftsRequested:
        actions.append(Action('add', {
          'shift': shift
        }))





  # Append actions with global (w.r.t. this particular email) info
  for i, a in enumerate(actions):
    actions[i].id = id
    
    if a.actionType == 'add':
      actions[i].data['sender'] = {
        'name': name,
        'email': email,
        'datetime': sentDatetime
      }
    
    elif orig['senderEmail']:
      actions[i].data['sender'] = {
        'email': orig['senderEmail']
      }

  return actions
  # Action('add', {
  #     'id': 25,
  #     'sender': {
  #       'name': "bart simpson",
  #       'email': 'bs@aol.com',
  #       'datetime': '2020-03-09T22:18:26.625',
  #     },
  #     'shift': {
  #       'datetime': '2022-09-15T17:20:00.000',
  #       'isLead': True,
  #       'isSpecial': False
  #     }
  #   }),
  #   Action('boost', {
  #     'email': 'bs@aol.com',
  #     'shift': {
  #       'datetime': '2022-09-30T11:20:00.000'
  #     }
  #   })



# Check if a flag exists in a list, only do one of value, type
def hasFlag(flagList, value=False, type=False):
  if value != False:
    return any(f.value == value for f in flagList)
  if type != False:
    return any(f.type == type for f in flagList)

# Filter a list of flags by type
def flagsOfType(flagList, types=[]):
  if type(types) == str:
    types = [types]
  return filter(lambda f: f.type == type, flagList)

# Test if a list intersects with another list, if empty treat as universal set
# Can use False to force empty return
def intersection(list1, list2):
  if list1 == False or list2 == False:
    return []
  if len(list1) == 0:
    return list2
  if len(list2) == 0:
    return list1
  return [x for x in list1 if x in list2]

def timespanToTimes(startEndTuple):
  '''
  Returns every hour starting with the start time and stopping before the end time
  '''
  times = []

  try:
    start = datetime.strptime(startEndTuple[0], TIME_FORMAT)
    end = datetime.strptime(startEndTuple[1], TIME_FORMAT)
    hours = int(timedelta.total_seconds(end - start) / 3600)

    for i in range(hours):
      times.append((start + timedelta(hours=i)).strftime(TIME_FORMAT))
    return times
  except:
    logger.error(f'Error in converting a timespan to times: {startEndTuple}')
    return []

def dateTimeToIso(date, time):
  try:
    result = datetime.strptime(str(NOW.year) + ' ' + date + ' ' + time, '%Y %m/%d' + ' ' + TIME_FORMAT).isoformat()
    return result
  except:
    logger.error(f'Error in dateTimeToIso applied to {date} {time}')
    return ''



# Insert a flag into a list of temp buckets, or create a new bucket
def insertFlag(flag, buckets = [], allDatesTimes = {'dates': [], 'times': []}, isCover = False):
  logger.debug('\nHandling: ' + str(flag) + '\non: ' + str(buckets))
  newShifts = []
  newFlags = []
  poppedABucket = False

  emptyBucket = {
    'dates': [],
    'times': [],
    'isLead': False,
    'isSpecial': False
  }

  emptyAllDatesTimes = {'dates': [], 'times': []}

  # Clear out empty buckets
  # todo empty shouldn't happen but does
  buckets = list(filter(lambda b: (len(b['dates']) > 0 or len(b['times']) > 0), buckets))

  # Make sure there is at least one bucket
  if len(buckets) == 0:
    buckets.append(emptyBucket)
  
  # Handling for all "time" flags
  if flag.type in ['shiftType', 'meal', 'time']:
    if flag.type == 'shiftType':
      possTimes = shiftTypeTimes[flag.value]
    elif flag.type == 'meal':
      possTimes = mealTimes[flag.value]
    elif flag.type == 'time':
      if type(flag.value) == tuple:
        allTimes = timespanToTimes(flag.value)
        
        # the first hour in the range will be this handleFlag
        possTimes = [allTimes[0]]
        
        # For the rest of the hours, make a new flag
        # unless it's suspected to be a head cook shift 
        # or special meal cook, which are 3 hours
        # If it's over three hours, don't because it must be an error
        if len(allTimes) <= 3 and not ((buckets[-1]['isLead'] or buckets[-1]['isSpecial']) and len(intersection(buckets[-1]['times'], shiftTypeTimes['cook'])) > 0):
          for t in allTimes[1:]:
            
            newFlags.append(Flag(flag.position, 'time', t))
            logger.debug('\tNew flag, ' + str(Flag(flag.position, 'time', t)))

          # todo fix safely? place another date after all these times
          if len(allDatesTimes['dates']) == 1:
            newFlags.append(Flag(flag.position, 'date', allDatesTimes['dates'][0]))
            logger.debug('\tNew flag, ' + str(Flag(flag.position, 'date', allDatesTimes['dates'][0])))
      
      # For single times
      else:
        possTimes = [flag.value]

    proposedPossTimes = intersection(possTimes, buckets[-1]['times'])

    # if it's a "new" time, then add it on to the allTimes,
    # if it's not then narrow down the existing list
    if len(intersection(allDatesTimes['times'], possTimes)) == 0:
      allDatesTimes['times'].extend(possTimes)
    else:
      allDatesTimes['times'] = intersection(allDatesTimes['times'], possTimes)
    
    # If the incoming possible times intersects with the existing times
    # (including case where existing = []), then replace the times 
    if len(proposedPossTimes) > 0:
      buckets[-1]['times'] = proposedPossTimes
    else:
      # create a new bucket with those possible times filled in
      buckets.append(emptyBucket)
      buckets[-1]['times'].extend(possTimes) # use the original times

  elif flag.type == 'date':
    # ensure we do not have duplicate dates in there
    # there should only ever be one date!!
    if flag.value in buckets[-1]['dates']:
      pass
    elif len(buckets[-1]['dates']) == 0:
      buckets[-1]['dates'].append(flag.value)
    else:
      buckets.append(emptyBucket)
      buckets[-1]['dates'].append(flag.value)

    if flag.value not in allDatesTimes['dates']:
      allDatesTimes['dates'].append(flag.value)

  # Head cook / PIC / special meal only applies to the current (last) bucket
  # will not try to be used to fill out unfilled buckets
  elif flag.value == 'lead':
    buckets[-1]['isLead'] = True
    # might as well narrow down times to head cooks and PICs
    buckets[-1]['times'] = intersection(buckets[-1]['times'], miscTimes['lead'])
  elif flag.value == 'special':
    buckets[-1]['isSpecial'] = True
    # might as well narrow down times to special cook and crew times
    buckets[-1]['times'] = intersection(buckets[-1]['times'], miscTimes['special'])


  # If last bucket is ready to pop out, pop it out as a shift
  if len(buckets[-1]['dates']) == 1 and len(buckets[-1]['times']) == 1:
    bucket = buckets.pop(-1)
    poppedABucket = True
    logger.debug(f'Popped a bucket in main pop stage: {bucket["dates"][0]} {bucket["times"][0]}')
    newShifts.append({
      'datetime': dateTimeToIso(bucket['dates'][0], bucket['times'][0]),
      'isLead': bucket['isLead'],
      'isSpecial': bucket['isSpecial']
    })

  # If only one date has been implied total, or only one time has been implied so far
  # then try to clear out all the preceding buckets (if they exist) using it
  # If this succeeds, then clear out allDatesTimes, as the buckets have been
  # cleared out, and we can start fresh with the next flag
  # It should be impossible for both to be one and have buckets to clear out
  # Also force trying to clear out the buckets when you hit a newline.
  if (poppedABucket and len(buckets) > 0) or flag.value == 'newline':
    logger.debug('All dates and times: ' + str(allDatesTimes))
    
    if len(allDatesTimes['dates']) == 1 and len(allDatesTimes['times']) != 1:
      if len(allDatesTimes['times']) == 0: # if no date found, try the next 14 days
        allDatesTimes['times'].extend(allShiftTimes)

      while len(buckets) > 0:

        # take out the empty buckets
        # todo this shouldn't happen but does
        buckets = list(filter(lambda b: (len(b['dates']) > 0 or len(b['times']) > 0), buckets))
        if len(buckets) == 0:
          break

        logger.debug('Trying to apply dates to: ' + str(buckets))
        buckets[-1]['dates'] = allDatesTimes['dates']
        # If last bucket is ready to pop out, pop it out as a shift
        # TODO way to do this routine without copy-paste??
        if len(buckets[-1]['dates']) == 1 and len(buckets[-1]['times']) == 1:
          bucket = buckets.pop(-1)
          logger.debug(f'Popped a bucket in clearing stage: {bucket["dates"][0]} {bucket["times"][0]}')
          newShifts.append({
            'datetime': dateTimeToIso(bucket['dates'][0], bucket['times'][0]),
            'isLead': bucket['isLead'],
            'isSpecial': bucket['isSpecial']
          })

        # If it's not, consider it an error and log it (Unless it's the cover email!!)
        # If this wasn't an error, it would let people put info about
        # shift A on either side of a fully specified shift B
        else:
          logger.warn(f'Unfinished bucket after trying date = {buckets[-1]["dates"][0]} on:\n{buckets}')

          # If we are trying to match covered shifts, we actually want the cartesian product of the remaining buckets,
          # because it doesn't have to be fully specified shift, it just has to be fully specified *with respect to*
          # the original email. So we might as well try to delete any possible shift it could be referring to.
          if (isCover):
            for date in buckets[-1]['dates']:
              for time in buckets[-1]['times']:
                newShifts.append({
                  'datetime': dateTimeToIso(date, time),
                  'isLead': buckets[-1]['isLead'],
                  'isSpecial': buckets[-1]['isSpecial']
                })

          break
      # Clear out the allDatesTimes
      allDatesTimes = emptyAllDatesTimes
    
    elif len(allDatesTimes['times']) == 1 and len(allDatesTimes['dates']) != 1:
      if len(allDatesTimes['dates']) == 0: # if no date found, try the next 14 days
        allDatesTimes['dates'].extend(next14days)
      
      while len(buckets) > 0:
        
        # take out the empty buckets
        # todo this shouldn't happen but does
        buckets = list(filter(lambda b: (len(b['dates']) > 0 or len(b['times']) > 0), buckets))
        if len(buckets) == 0:
          break

        logger.debug('Trying to apply times to: ' + str(buckets))
        buckets[-1]['times'] = allDatesTimes['times']
        # If last bucket is ready to pop out, pop it out as a shift
        if len(buckets[-1]['dates']) == 1 and len(buckets[-1]['times']) == 1:
          bucket = buckets.pop(-1)
          logger.debug(f'Popped a bucket in clearing stage: {bucket["dates"][0]} {bucket["times"][0]}')
          newShifts.append({
            'datetime': dateTimeToIso(bucket['dates'][0], bucket['times'][0]),
            'isLead': bucket['isLead'],
            'isSpecial': bucket['isSpecial']
          })

        # If it's not, consider it an error and log it (Unless it's the cover email!!)
        else:
          logger.warning(f'Unfinished bucket after trying time = {buckets[-1]["times"][0]} on:\n{buckets}')

          # If we are trying to match covered shifts, we actually want the cartesian product of the remaining buckets,
          # because it doesn't have to be fully specified shift, it just has to be fully specified *with respect to*
          # the original email. So we might as well try to delete any possible shift it could be referring to.
          if (isCover):
            for date in buckets[-1]['dates']:
              for time in buckets[-1]['times']:
                newShifts.append({
                  'datetime': dateTimeToIso(date, time),
                  'isLead': buckets[-1]['isLead'],
                  'isSpecial': buckets[-1]['isSpecial']
                })

          break
      # Clear out the allDatesTimes
      allDatesTimes = emptyAllDatesTimes
    elif flag.value == 'newline': # treat newline as a reset
      allDatesTimes = emptyAllDatesTimes
      buckets = [emptyBucket]
  
  return newShifts, buckets, allDatesTimes, newFlags

# Wrapper for insertFlag for a list of flags, and only outputs the shifts
def flagsToShifts(flagList, isCover = False):
  shifts = []
  buckets = []
  allDatesTimes = {'dates': [], 'times': []}
  for f in flagList:
    newShifts, buckets, allDatesTimes, newFlags = insertFlag(f, buckets, allDatesTimes, isCover)
    nestedNewShifts = []
    for nf in newFlags: # only need one level of recursion, it's only if we find time ranges
      nestedNewShifts, buckets, allDatesTimes, noNewFlags = insertFlag(nf, buckets, allDatesTimes, isCover)
    shifts.extend(newShifts)
    shifts.extend(nestedNewShifts)
  return shifts



# Make flags out of email text (subj + body, usually)
def makeFlags(text, date):
  # make a series of "flags", by running the email through the helper regexs.
  # each flag will have a 
  # - position (index within the string)
  # - type (e.g. isSubRequest or isCover or isLead or weekday or time or type)
  # - value (e.g. True, or "wednesday", or "nameOverride")
  
  flags = []

  # REQUEST TYPES
  for p in requestTypePatterns.keys():
    for match in re.finditer(p, text):
      # todo checks for priority?
      flags.append(Flag(match.start(), 'requestType', requestTypePatterns[p]))

  # SHIFT TYPES
  for p in shiftTypePatterns.keys():
    for match in re.finditer(p, text):
      # todo checks for priority?
      flags.append(Flag(match.start(), 'shiftType', shiftTypePatterns[p]))

  # MEALS
  for p in mealPatterns.keys():
    for match in re.finditer(p, text):
      # todo checks for priority?
      flags.append(Flag(match.start(), 'meal', mealPatterns[p]))
  
  # TEXT (NEWLINES)
  for p in textPatterns.keys():
    for match in re.finditer(p, text):
      # todo checks for priority?
      flags.append(Flag(match.start(), 'text', textPatterns[p]))

  # MISC
  for p in miscPatterns.keys():
    for match in re.finditer(p, text):
      # todo checks for priority?
      flags.append(Flag(match.start(), 'misc', miscPatterns[p]))

  # DATES
  for p in datePatterns.keys():
    for match in re.finditer(p, text):
      value = datePatterns[p]
      if callable(value): # for "the 3rd" and today/tomorrow
        result = value(match.group(0), date) # https://docs.python.org/3/library/re.html#re.Match.group
        # passes in both arguments, each is for a different function
      elif isinstance(value, int): # for "August 3" or "8/3"
        result = handleDateStr(match.group(0), value)
      elif isinstance(value, str):
        result = value # for "today", "tomorrow", days of week
      flags.append(Flag(match.start(), 'date', result))
  
  # TIMES
  for p in timePatterns.keys():
    for match in re.finditer(p, text):
      handler = timePatterns[p]
      result = handler(match.group(0))
      flags.append(Flag(match.start(), 'time', result))

  flags.sort(key = lambda f: f.position)
  return flags






# For testing
if __name__ == '__main__':
  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
  # Option 1 - whatever this is
  # messages = [
  #   Email(8, "Joe Jones <jj@jj.com>", "Sub tuesday lunch", "Ayo I need a sub. 11:20 bro."),
  #   Email(7, "Person McPerson <pmp@aol.com>", "Please", "Help I have sooo much homework and I really need someone to cover my head cook shift on sunday morning")
  # ]

  # Option 2 - spring sub emails
  with open('app/springSubEmails.json', 'r') as f:
    dicts = json.loads(f.read())
  messages = [Email(d['id'], d['From'], d['subject'], d['body'], d['contentType'], d['timestamp']) for d in dicts]

  # Option 3 - tricky message
  # messages = [
  #   Email(1, "Hacker <h@h.h>", "", "I need a sub 3:20 on wednesday and thursday and 5:20 on friday")
  # ]

  actions = []
  for message in messages:
    newActions = parseEmail(message)
    if newActions:
      actions.extend(newActions)
  
  logger.info('\nEmails parsed.')
  logger.debug('Actions: ' + str(actions))