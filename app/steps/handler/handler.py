# Handles actions passed in by parser
import time

from classes.Action import Action

from helpers.db import getDB, overwriteDB
from helpers.shifts import shiftInfoToDatetime, isOver
import logging
logger = logging.getLogger('handler')

def handleActions(databasePath, actions = [], reverse=False):
  logger.info('========== HANDLING ACTIONS ==========')

  if reverse:
    actions.reverse()

  # add actions that will be done every time
  actions.insert(0, Action('resetStatuses'))
  actions.append(Action('deleteOld'))

  requestsAdded = 0
  requestsDeleted = 0
  requestsBoosted = 0
  requestsOver = 0

  for action in actions:
    data = getDB(databasePath)
    subRequests = data['subRequests']

# ADD
    if action.actionType == 'add':
      logger.debug('Processing add action...\n\t' + str(action))
      newRequest = action.data

      # try to match the subrequest with identical email and datetime (these should be unique)
      match = next((x for x in subRequests if (
        x['sender']['email'] == newRequest['sender']['email'] and shiftInfoToDatetime(x['shift']) == shiftInfoToDatetime(newRequest['shift'])
      )), False)

      # see if this is indeed a new request
      if match == False:
        newRequest['isNew'] = True
        newRequest['isBoosted'] = False
        newRequest['timeCreated'] = round(time.time() * 1000)
        # set other things here

        if not isOver(newRequest['shift']):
          subRequests.append(newRequest)
          requestsAdded += 1
        else:
          logger.warning('\t\u26A0 Prevented adding a sub request for the past.')
      else:
        logger.warning('\t\u26A0 Prevented adding a duplicate sub request.')

    
    elif action.actionType == 'delete' or action.actionType == 'boost':
      logger.debug('Processing delete/boost action...')
      requestInfo = action.data

      # match the subrequest with identical email and datetime (these should be unique)
      matchIndex = None
      for i, req in enumerate(subRequests):
        if req['sender']['email'] == requestInfo['sender']['email'] and shiftInfoToDatetime(req['shift']) == shiftInfoToDatetime(requestInfo['shift']):
          matchIndex = i
          break
      

      if matchIndex != None:
        logger.debug('\tMatch found.')
# DELETE
        if action.actionType == 'delete':
          subRequests.pop(matchIndex)
          requestsDeleted += 1
      
# BOOST      
        else: # boost
          if subRequests[matchIndex]['isBoosted'] == False:
            subRequests[matchIndex]['isBoosted'] = True
            requestsBoosted += 1
          else:
            # this should never happen
            logger.warning('\t\uFE0F Prevented boosting a boosted sub request.')
      else:
        logger.warning('\t\u26A0 No match found for delete/boost.')

    # delete all the requests that are in the past
    elif action.actionType == 'deleteOld':
      for i in range(len(subRequests)):
        r = subRequests[i]
        if isOver(r['shift']):
          subRequests[i] = False # workaround because simply deleting will mess with the for loop
          requestsOver += 1
      data['subRequests'] = list(filter(lambda req : req != False, subRequests)) # for some reason, can't just use subRequests

    # Set isNew and isBoosted to false for all requests
    elif action.actionType == 'resetStatuses':
      for r in subRequests:
        r['isNew'] = False
        r['isBoosted'] = False

    else:
      logger.error(f'Invalid action type passed into handleActions: {action}')
      break

    overwriteDB(data, databasePath)
    time.sleep(0.01) # in case immediately putting the file down and reading it again is bad?

  logger.info(f'Processed actions:\n\t{requestsAdded} additions\n\t{requestsBoosted} boosts\n\t{requestsDeleted} deleted due to coverage\n\t{requestsOver} stale requests deleted.')

  return
    

  

  # modify it with the actions passed in

  # rewrite it to that file

# For testing
if __name__ == '__main__':
  import json 
  from decouple import config

  logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

  actions = []
  with open('app/actionsAug19.json', 'r') as f:
    actionsDict = json.loads(f.read())
  for a in actionsDict:
    actions.append(Action(a['actionType'], a['data']))

  handleActions(config('DATABASE_PATH'), actions, True)