# Create necessary files if they don't exist
import os.path

# Check whether the specified path exists or not
for dir in ['app', 'app/data']:
  if not os.path.exists(dir):
    os.makedirs(dir)

necessaryFiles = {
  'envPath': {
    'path': '.env',
    'default': """EMAIL_USERNAME=''
EMAIL_PASSWORD=''
IMAP_SERVER='imap.gmail.com'
SMTP_SERVER='smtp.gmail.com'
TEST_TO_EMAIL=''
REAL_TO_EMAIL=''
DATABASE_PATH='app/data/testDatabase.json'
TESTING='True'
LAST_PM_HOUR=8"""
  },
  'debuggingLogPath': {
    'path': 'app/debugging.log',
    'default': ''
  },
  'topIdLogPath': {
    'path': 'app/topIdLog.csv',
    'default': ''
  },
  'databasePath': {
    'path': 'app/data/database.json',
    'default': """{
  "lastIdProcessed": 0,

  "subRequests": [
    
  ]
}"""
  },
  'testDatabasePath': {
    'path': 'app/data/testDatabase.json',
    'default': """{
  "lastIdProcessed": 0,

  "subRequests": [
    
  ]
}"""
  },
  'shiftsPath': {
    'path': 'app/data/shifts.json',
    'default': """{
  "byType": {
    "breakfast crew": [
      "08:20 AM"
    ],
    "pre-crew": [
      "11:50 AM",
      "05:50 PM"
    ],
    "crew": [
      "08:20 AM",
      "01:00 PM",
      "07:00 PM"
    ],
    "commando": [
      "08:30 PM"
    ],
    "cook": [
      "09:20 AM",
      "10:20 AM",
      "11:20 AM",
      "03:20 PM",
      "04:20 PM",
      "05:20 PM"
    ]
  },
  "byMeal": {
    "lunch": [
      "09:20 AM",
      "10:20 AM",
      "11:20 AM",
      "11:50 AM",
      "01:00 PM"
    ],
    "dinner": [
      "05:50 PM",
      "07:00 PM",
      "03:20 PM",
      "04:20 PM",
      "05:20 PM"
    ],
    "pizza": [
      "05:50 PM",
      "07:00 PM",
      "03:20 PM",
      "04:20 PM",
      "05:20 PM"
    ]
  },
  "byAttribute": {
    "lead": [
      "09:20 AM",
      "01:00 PM",
      "03:20 PM",
      "07:00 PM"
    ],
    "special": [
      "09:20 AM",
      "01:00 PM",
      "03:20 PM",
      "07:00 PM"
    ]
  }
}"""
  }
}

for file in necessaryFiles.keys():
  path = necessaryFiles[file]['path']
  default = necessaryFiles[file]['default']

  if not os.path.exists(path):
    with open(path, 'w+') as f:
      f.write(default)