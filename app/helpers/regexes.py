# Regular expressions for parser.py

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



# Time ranges; "3:20 and 4:20"
timeRangeConnectorForSplit = 'to|-|and|through' # for the splitting
timeRangeConnector = f' ?({timeRangeConnectorForSplit}) ?' # the real one

# TIME REGEXES
standardTime = '((1[0-2]|0?[1-9])(:|\\.)([0-5][0-9]) ?([AaPp]\\.?[Mm]\\.?)?)'
atTime = '((at (1[0-2]|0?[1-9]))(?!:) ?([AaPp]\\.?[Mm]\\.?)?)'
hourOnlyTime = '((1[0-2]|0?[1-9]) ?([AaPp]\\.?[Mm]\\.?))'
singleTime = f'({standardTime}|{atTime}|{hourOnlyTime})'

singleTime = f'(?<!{singleTime}{timeRangeConnector}){singleTime}(?!{timeRangeConnector}{singleTime})'

timeRange = f'((1[0-2]|0?[1-9])((:|\\.)([0-5][0-9]))? ?([AaPp]\\.?[Mm]\\.?)?){timeRangeConnector}((1[0-2]|0?[1-9])((:|\\.)([0-5][0-9]))? ?([AaPp]\\.?[Mm]\\.?)?)'