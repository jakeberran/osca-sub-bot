# A graphical user interface for operating the sub bot.

# https://github.com/TomSchimansky/CustomTkinter/wiki

import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from helpers.db import getDB, overwriteDB
from classes.FunctionWithAppendedArguments import FunctionWithAppendedArguments
from mainFuncs import readParseAndHandle, getCurrentSubRequests, updateSubRequests, writeAndSend
from decouple import config
import dotenv
import os

# create main window
ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

def button_function():
    print("button pressed")

root = ctk.CTk(fg_color='gray')
root.geometry("500x500")

root.title("Sub Bot")

# tab control
tabview = ctk.CTkTabview(root)
tabview.pack(padx=0, pady=0)

tab_home = tabview.add("Home")
tab_settings = tabview.add("Settings")
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
  print(idx)
  subRequestsList = getCurrentSubRequests()
  if isinstance(idx, int):
    del subRequestsList[idx]
  updateSubRequests(subRequestsList)
  
  loadList(getCurrentSubRequests(), 'new')

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
  return
  # writeAndSend(True) # TODO change to false

# Home tab bottom buttons
homeButtons = ctk.CTkFrame(tab_home)
button_processNewEmails = ctk.CTkButton(homeButtons, text="Process New Emails", command=processNewEmails)
button_sendRealEmail = ctk.CTkButton(homeButtons, text="Send Real Email", command=sendRealEmail())
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

for i, s in enumerate(settings):
  label = ctk.CTkLabel(tab_settings, text=s['title'], justify=ctk.RIGHT)
  
  # Cast to boolean when appropriate
  if s['varname'] in ['TESTING']:
    initial_value = config(s['varname'], cast=bool)
  else:
    initial_value = config(s['varname'], cast=str)

  # For strings, do an entry
  if isinstance(initial_value, str):
    initialSettings[s['varname']] = initial_value
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
    initialSettings[s['varname']] = initial_value
    updatedSettings[s['varname']] = ctk.BooleanVar(tab_settings, initial_value)
    entry = ctk.CTkSwitch(tab_settings, text='', variable=updatedSettings[s['varname']], onvalue=True, offvalue=False, width=200)

  label.grid(row=i+1, column=0, padx=5, pady=5, sticky=ctk.E)
  entry.grid(row=i+1, column=1, padx=0, pady=5, sticky=entryJustification)

# Buttons at bottom of settings
def revertSettings():
  for k in updatedSettings.keys():
    updatedSettings[k].set(initialSettings[k])

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
  

settings_buttonToolbar = ctk.CTkFrame(tab_settings)

ctk.CTkButton(settings_buttonToolbar, text='Revert', command=revertSettings).grid(row=0, column=0, padx=10, pady=20)
ctk.CTkButton(settings_buttonToolbar, text='Save', command=saveSettings).grid(row=0, column=1, padx=10, pady=20)

settings_buttonToolbar.grid(columnspan=2)

'''
=============HELP TAB================
'''
ttk.Label(tab_help, text="This is the help tab").grid(column=0, row=0, padx=30, pady=30)

# run the main loop
root.mainloop()