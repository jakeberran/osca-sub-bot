# A graphical user interface for operating the sub bot.

# https://github.com/TomSchimansky/CustomTkinter/wiki

import tkinter as tk
import webbrowser
import customtkinter as ctk
from tkinter import ttk
from helpers.db import getDB, overwriteDB
from classes.FunctionWithAppendedArguments import FunctionWithAppendedArguments
from mainFuncs import readParseAndHandle, getCurrentSubRequests, updateSubRequests, writeAndSend
from decouple import config
from datetime import datetime
import dotenv
import os

# create main window
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

def button_function():
    print("button pressed")

root = ctk.CTk(fg_color='gray')
root.geometry("600x600")

root.title("Sub Bot")

# tab control
tabview = ctk.CTkTabview(root)
tabview.pack(padx=0, pady=0)

tab_home = tabview.add("Home")
tab_settings = tabview.add("Settings")
tab_shifts = tabview.add("Shifts")
tab_help = tabview.add('Help')
tabview.set("Home")

# tabs for the home tab old/new sub requests
home_tabview = ctk.CTkTabview(tab_home)
home_tabview.pack(padx=20, pady=20)

tab_old = home_tabview.add("Old")
tab_current = home_tabview.add("Current")

tab_old_table_container = ctk.CTkFrame(tab_old)
tab_current_table_container = ctk.CTkFrame(tab_current)
tab_old_table_container.pack()
tab_current_table_container.pack()

def removeIndexAndReload(idx = None):
  subRequestsList = getCurrentSubRequests()
  if isinstance(idx, int):
    del subRequestsList[idx]
  else:
    tk.messagebox.showerror('Error', 'Something went wrong removing a sub request.')
  updateSubRequests(subRequestsList)
  
  loadList(getCurrentSubRequests(), 'new')

def addSubRequest(newRequest):
  subRequestsList = getCurrentSubRequests()

  subRequestsList.append({
      "shift": {
        "datetime": newRequest['datetime'].get(),
        "isLead": newRequest['isLead'].get(),
        "isSpecial": newRequest['isSpecial'].get()
      },
      "sender": {
        "name": '',
        "email": newRequest['email'].get(),
        "datetime": datetime.now().isoformat()
      },
      "isNew": True,
      "isBoosted": False,
      "timeCreated": int(datetime.now().timestamp() * 1000)
    })
  try:
    subRequestsList.sort(key=lambda x: datetime.fromisoformat(x['shift']['datetime']))

    updateSubRequests(subRequestsList)
  
    loadList(getCurrentSubRequests(), 'new')
  except:
    tk.messagebox.showerror('Error', 'Check your datetime format.')

# Loading the list of requests
def loadList(subRequests, which='old'):
  if which == 'old':
    table_master = tab_old_table_container
  elif which == 'new':
    table_master = tab_current_table_container
    for widget in table_master.winfo_children(): # clear out the table first
      widget.destroy()

  table = ctk.CTkFrame(table_master)

  # Table headers
  ctk.CTkLabel(table, text='Email').grid(row=0, column=0, padx=10, pady=5)
  ctk.CTkLabel(table, text='Datetime').grid(row=0, column=1, padx=10, pady=5)
  ctk.CTkLabel(table, text='Lead?').grid(row=0, column=2, padx=10, pady=5)
  ctk.CTkLabel(table, text='Special?').grid(row=0, column=3, padx=10, pady=5)

  for i, subRequest in enumerate(subRequests):
    email = subRequest['sender']['email']
    datetime = subRequest['shift']['datetime']
    isLead = subRequest['shift']['isLead']
    isSpecial = subRequest['shift']['isSpecial']

    label_email = ctk.CTkLabel(table, text=email)
    label_email.grid(row=i+1, column=0, padx=10, pady=5)

    label_datetime = ctk.CTkLabel(table, text=datetime)
    label_datetime.grid(row=i+1, column=1, padx=10, pady=5)

    label_isLead = ctk.CTkLabel(table, text=str(isLead))
    label_isLead.grid(row=i+1, column=2, padx=10, pady=5)

    label_isSpecial = ctk.CTkLabel(table, text=str(isSpecial))
    label_isSpecial.grid(row=i+1, column=3, padx=10, pady=5)

    if which == 'new':
      ctk.CTkButton(table, text='-', fg_color='red', width=15, height=15, text_color='black', command=FunctionWithAppendedArguments(removeIndexAndReload, i)).grid(row=i+1, column=4, padx=10, pady=5)

    # TODO add are you sure you want to delete button
    # last row will have a green + button? but have a row of padding between
  
  if which == 'new':
    newRequest = {
      'email': ctk.StringVar(tab_shifts, 'person@oberlin.edu'),
      'datetime': ctk.StringVar(tab_shifts, '2023-01-01T16:20:00'),
      'isLead': ctk.BooleanVar(tab_shifts, False),
      'isSpecial': ctk.BooleanVar(tab_shifts, False)
    }
    entry_email = ctk.CTkEntry(table, textvariable=newRequest['email'])
    entry_email.grid(row=len(subRequests)+1, column=0, padx=10)

    entry_datetime = ctk.CTkEntry(table, textvariable=newRequest['datetime'])
    entry_datetime.grid(row=len(subRequests)+1, column=1, padx=10)

    entry_isLead = ctk.CTkCheckBox(table, variable=newRequest['isLead'], onvalue=True, offvalue=False, text='', width=20, height=20)
    entry_isLead.grid(row=len(subRequests)+1, column=2)

    entry_isSpecial = ctk.CTkCheckBox(table, variable=newRequest['isSpecial'], onvalue=True, offvalue=False, text='', width=20, height=20)
    entry_isSpecial.grid(row=len(subRequests)+1, column=3)

    ctk.CTkButton(table, text='+', fg_color='green', width=15, height=15, text_color='white', command=FunctionWithAppendedArguments(addSubRequest, newRequest)).grid(row=len(subRequests)+1, column=4, padx=10, pady=5)

  table.pack()

# Initially, load the old list of sub requests
loadList(getCurrentSubRequests(), which='old')

# Process New Emails button
def processNewEmails():
  # readParseAndHandle()
  loadList(getCurrentSubRequests(), which='new')
  home_tabview.set("Current")

def saveList():
  return

def sendRealEmail():
  writeAndSend(config('TESTING', cast=bool)) # TODO change to false
  tk.messagebox.showinfo('Sub Bot', 'Email sent!')


# Home tab bottom buttons
homeButtons = ctk.CTkFrame(tab_home)
button_processNewEmails = ctk.CTkButton(homeButtons, text="Process New Emails", command=processNewEmails)
button_sendRealEmail = ctk.CTkButton(homeButtons, text="Send Real Email", command=sendRealEmail)
button_processNewEmails.grid(row=0, column=0, padx=20, pady=20)
button_sendRealEmail.grid(row=0, column=1, padx=20, pady=20)
homeButtons.pack()

'''
=============SETTINGS TAB================
'''

settings = [
  {
    'title': 'Bot Email Address',
    'varname': 'EMAIL_USERNAME',
    'hidden': False
  },
  {
    'title': 'Bot Email Password',
    'varname': 'EMAIL_PASSWORD',
    'hidden': True
  },
  {
    'title': 'IMAP Server',
    'varname': 'IMAP_SERVER',
    'hidden': False
  },
  {
    'title': 'SMTP Server',
    'varname': 'SMTP_SERVER',
    'hidden': False
  },
  {
    'title': '"To" Email (Testing)',
    'varname': 'TEST_TO_EMAIL',
    'hidden': False
  },
  {
    'title': '"To" Email (Real)',
    'varname': 'REAL_TO_EMAIL',
    'hidden': False
  },
  {
    'title': 'Database (JSON) Path',
    'varname': 'DATABASE_PATH',
    'hidden': False
  },
  {
    'title': 'Last hour defaulting to PM',
    'varname': 'LAST_PM_HOUR',
    'hidden': False
  },
  {
    'title': 'Testing',
    'varname': 'TESTING',
    'hidden': False
  },
]

initialSettings = {}
updatedSettings = {}

# Toggle showing a password field
def toggleShow(obj):
  if obj.cget('show') == '*':
    obj.configure(show='')
  else:
    obj.configure(show='*')

def loadSettings():
  for i, s in enumerate(settings):
    label = ctk.CTkLabel(tab_settings, text=s['title'], justify=ctk.RIGHT)
    
    # Cast to boolean or int when appropriate
    if s['varname'] in ['TESTING']:
      c = bool
    elif s['varname'] in ['LAST_PM_HOUR']:
      c = int
    else:
      c = str
    
    initial_value = config(s['varname'], cast=c)
    initialSettings[s['varname']] = initial_value

    # For strings, do an entry
    if isinstance(initial_value, str):
      updatedSettings[s['varname']] = ctk.StringVar(tab_settings, initial_value)
      entry = ctk.CTkEntry(tab_settings, textvariable=updatedSettings[s['varname']], width=200, justify=ctk.LEFT)
      entryJustification = ctk.E

      if s['hidden']:
        entry.configure(width=170, show='*')
        entryJustification = ctk.W
        toggleButton = ctk.CTkButton(tab_settings, width=25, height=25, text='*', command=FunctionWithAppendedArguments(toggleShow, entry))
        toggleButton.grid(row=i+1, column=1, sticky=ctk.E)

    # For booleans, a switch
    elif isinstance(initial_value, bool):
      updatedSettings[s['varname']] = ctk.BooleanVar(tab_settings, initial_value)
      entry = ctk.CTkSwitch(tab_settings, text='', variable=updatedSettings[s['varname']], onvalue=True, offvalue=False, width=200)
    
    elif isinstance(initial_value, int):
      updatedSettings[s['varname']] = ctk.IntVar(tab_settings, initial_value)
      sliderValue = ctk.CTkLabel(tab_settings, width=25, height=25, anchor=ctk.E, text=initial_value)
      sliderValue.grid(row=i+1, column=1, sticky=ctk.E)
      entry = ctk.CTkSlider(tab_settings, from_=6, to=11, width=170, number_of_steps=5, variable=updatedSettings[s['varname']], command=lambda val: sliderValue.configure(text=int(val)))
      entryJustification = ctk.W
      

    label.grid(row=i+1, column=0, padx=5, pady=5, sticky=ctk.E)
    entry.grid(row=i+1, column=1, padx=0, pady=5, sticky=entryJustification)

loadSettings()

# Buttons at bottom of settings
def revertSettings():
  for k in updatedSettings.keys():
    # print(f"{k}: {updatedSettings[k].get()}") # for testing
    updatedSettings[k].set(initialSettings[k])
    loadSettings()

def saveSettings():
  # List out the settings for debugging
  for k in updatedSettings.keys():
    print(f"{k}: {updatedSettings[k].get()}")

  # update the stored settings
  dotenv_file = dotenv.find_dotenv()
  dotenv.load_dotenv(dotenv_file)
  for k in updatedSettings.keys():
    # Set in environment first
    os.environ[k] = str(updatedSettings[k].get())
    # Then update the env file
    dotenv.set_key(dotenv_file, k, os.environ[k])

  # update the initial settings
  for k in initialSettings.keys():
    initialSettings[k] = (updatedSettings[k].get())

  tk.messagebox.showinfo('Sub Bot', 'Settings saved.')
  loadSettings()
  

settings_buttonToolbar = ctk.CTkFrame(tab_settings)

ctk.CTkButton(settings_buttonToolbar, text='Revert', command=revertSettings).grid(row=0, column=0, padx=10, pady=20)
ctk.CTkButton(settings_buttonToolbar, text='Save', command=saveSettings).grid(row=0, column=1, padx=10, pady=20)

settings_buttonToolbar.grid(columnspan=2)




'''
=============SHIFTS TAB================
'''
ctk.CTkLabel(tab_shifts, text='Specify the start times of shifts.').pack()

shifts = getDB('app/shifts.json')
shiftsRenaming = {} # todo do this

shifts_tabview = ctk.CTkTabview(tab_shifts)
shifts_tabview.pack(padx=20, pady=20)

tab_byType = shifts_tabview.add("By Type")
tab_byMeal = shifts_tabview.add("By Meal")
tab_byAttribute = shifts_tabview.add("By Attribute")

# TODO write this 1/16
def addShiftTime(tab, listbox, byWhat, listName):
  # add to list
  answer = tk.simpledialog.askstring('Add Shift Time', 'Enter a time in the form HH:MM AM/PM', parent=root)
  shifts[byWhat][listName].append(answer)
  print(datetime.strptime(answer, '%I:%M %p'))
  try:
    shifts[byWhat][listName].sort(key=lambda x: datetime.strptime(x, '%I:%M %p'))
  except:
    tk.messagebox.showerror('Error', 'Could not sort times. Make sure the format is HH:MM AM/PM.')
    
  # reload
  overwriteDB(shifts, 'app/shifts.json')
  loadShifts(byWhat, tab)
  return

def removeShiftTime(tab, listbox, byWhat, listName):
  # remove from shifts variable
  for index in listbox.curselection():
    del shifts[byWhat][listName][index]

  # reload
  overwriteDB(shifts, 'app/shifts.json')
  loadShifts(byWhat, tab)
  return

def loadShifts(byWhat, tab):
  shifts = getDB('app/shifts.json')

  for i, listName in enumerate(shifts[byWhat].keys()):
    # sort times
    shifts[byWhat][listName].sort(key=lambda x: datetime.strptime(x, '%I:%M %p'))

    container = ctk.CTkFrame(tab, height=4)
    subcontainer = ctk.CTkFrame(container, height=4)
    ctk.CTkLabel(container, text=listName).pack()
    
    scrollbar = ctk.CTkScrollbar(subcontainer, height=3)
    if len(shifts[byWhat][listName]) > 3:
      scrollbar.pack(side = ctk.RIGHT, fill=ctk.Y)

    listbox = tk.Listbox(subcontainer, height=3, yscrollcommand=scrollbar.set)
    # for time in shifts[byWhat][listName]:
    listbox.insert('end', *shifts[byWhat][listName])

    listbox.pack(side= ctk.LEFT, fill=ctk.BOTH)
    scrollbar.configure(command = listbox.yview)

    buttons = ctk.CTkFrame(container)
    ctk.CTkButton(
      buttons, text='+', fg_color='green', text_color='white', width=20, height=20,
      command=FunctionWithAppendedArguments(addShiftTime, tab, listbox, byWhat, listName)
    ).grid(row=0, column=1, padx='10', pady=10)
    ctk.CTkButton(
      buttons, text='-', fg_color='red', text_color='black', width=20, height=20,
      command=FunctionWithAppendedArguments(removeShiftTime, tab, listbox, byWhat, listName)
    ).grid(row=0, column=0, padx=10, pady=10)
    
    subcontainer.pack()
    buttons.pack()
    container.grid(row=i//2, column=i%2)

loadShifts('byType', tab_byType)
loadShifts('byMeal', tab_byMeal)
loadShifts('byAttribute', tab_byAttribute)

'''
=============HELP TAB================
'''
ctk.CTkButton(tab_help, text='View Repository on GitHub', command=lambda: webbrowser.open_new_tab('https://github.com/jakeberran/osca-sub-bot')).pack(padx=20, pady=20)

# run the main loop
root.mainloop()