# osca-sub-bot
This is an email bot that helps aggregate sub requests that are waiting to be filled. It sends out a digest with all of the remaining sub requests, each with links to pre-filled emails to contact the requester, mark the request as covered, and add the shift to your Google Calendar.

Eventually, I plan to run this in the cloud using Microsoft Azure Functions (dirt cheap!) so no one needs to worry about actually triggering the sub bot on their own computer or setting it up to run daily. The files for this are mostly in place, it just has not been thoroughly tested, or even deployed. When that happens, the following will apply.
- To manually run this Azure function, follow the instructions [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-manually-run-non-http). This will eventually have actual instructions.

## Need to set up your own?
Note: these setup instructions have not been my priority in this project, so it may not work correctly or I may have forgotten steps. Feel free to troubleshoot yourself or contact me.
1. Set up a Python virtual environment
    - Make the `osca-sub-bot` your current directory, and run `python3 -m venv .venv` to create the venv.
    - Activate the virtual environment. On Linux (and probably Mac?) this is done with `source /example/path/osca-sub-bot/.venv/bin/activate`, on Windows it is different. You will have to run this to activate the virtual environment before you want to run any of the scripts. In your bash/command prompt it should now say something like `(.venv)` at the start of each line.


2. To install the dependencies, run the following commands in order:
    - Install [pip-tools](https://github.com/jazzband/pip-tools) to use pip-compile with `pip install pip-tools`
    - Compile the requirement packages (this gets all their dependencies, etc. until you have a complete list of all dependencies) with `pip-compile -o requirements.in`
    - Now install the required packages: `pip install -r requirements.txt`

3. Add `.../osca-sub-bot/app` to your PYTHONPATH, where `...` stands for the path of the directory you have the `osca-sub-bot` folder in. Here are some [instructions](https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html#if-you-are-on-a-mac) that may help.

4. Make a new (strongly suggest new) Google account for the email bot, or you can try other sites but Gmail was the first one I could get to work. Go to Account Settings > Security, enable & set up two-factor authentication (this is not needed in itself), which will then allow you to create an "app password" (right below the two-factor authentication part of the settings). Once on the app passwords screen, choose "Other" as the app, name it whatever you want (you won't need the name for anything), and make sure to copy the generated password into your `.env` file right away because Google only shows it to you once. If you run the bot and get an error saying you can't log in, double check your password in `.env`, and also go to Gmail settings and make sure IMAP is enabled.

5. Set the environment variables. Make a copy of `example.env` and rename it `.env` and then put all the values after the equals signs (no quotes, and no comments on the same lines as key-value pairs)


Note: It shouldn't be necessary to run this on Linux or Windows Subsystem for Linux, but if you run into issues, try that or ask me about it.

## Want to work on this repository?
Follow the instructions under **"Need to set up your own?"**, and then read this primer:

Here's how `app/app.py` works. It runs the following steps from the `app/steps` folder in sequence. 
1. `reader.py` reads all the emails since the last email it read (stored as an ID number in ), updates the ID number of the latest email, and returns a list of `Email` objects, which is a custom class with basic info like from, to, subject, and body (will strip out attachments/funky stuff). This class has a bad name because the widely used `email` module has an `Email` class too.
2. `parser.py` is where all the messy stuff happens; basically it runs the subject and body of each email through a bunch of regular expressions for dates, times, meal types, "sub", etc. to convert a messy email into a neat list of `Flag` objects which each have a position (what index in the string it starts on), type (e.g. `'date'` or `'shiftType'`), value (e.g. `'08/20'` or `True`). Then, it process this list of flags and ends up with a list of `Action` objects, which will be explained next.
3. `handler.py` takes in a list of `Action` objects and for each one, performs an action on the "database" (which is just a JSON file that gets converted into a dictionary, modified, and converted back). This may be adding, deleting, or "boosting" (when there is recent activity on a request email chain, but no one has covered).
4. `writer.py` uses `jinja2` to produce HTML for the email body from the template `template.html`.
5. `sender.py` takes in basic email info and sends the email out to the `TO_EMAIL` specified in the environment variables.

## What to tell your co-op?
- It's not meant to interfere with or totally replace existing sub-requesting methods, it's meant to make sure people's requests don't get lost and provide quick ways to see them, contact the requester, and add the shift to your Google Calendar.
- The only thing you really have to know is to **make sure new sub requests are in a "fresh" email (one email can have multiple), i.e. don't bury them in email chains.** If you send a reply, it will only check to see if that reply is covering the shift from the original email in the chain.
- Write all the fun emails you want, it recognizes and handles a lot of different words/patterns in your text, which I based off of the last month of Harkness emails in spring 2022. But if you say "I don't need a sub tomorrow lunch crew", you will definitely be on the list for needing a sub tomorrow for lunch crew. And if it's ambiguous to a human it will no doubt be ambiguous to the bot. ***The simplest (not only) way to ensure it recognizes yours as a sub request is to put the word "sub" somewhere in the subject or body.***
- I hope it can accomplish three things:
  - Reduce stress for people requesting subs, and it can feel more "normalized" by going into a system that encourages shift-swapping (I notice that people often write elaborate/apologetic sub requests)
  - Incentivize requesting a sub earlier rather than at the last minute (when this is feasible)
  - Get more shifts covered, to try to get rid of "co-op saviors", one-person crews, etc.
  - Ease the burden of the workchart coordinator and missed jobs coordinator

  ### Fun Facts (about how sub emails get buried)
  - At Harkness in Spring 2022, 56 out of the last 300 emails were sub requests
  - Out of the last 200 emails, there were an average of ~13 emails per day

## Known Issues
- It can't parse things like "I need a sub 3:20 on wednesday and thursday and 5:20 on friday" without newlines, this could be solved with a more complex apparatus for "and" and list detection, or smart detection of the order the writer puts dates and meals/shifts/times in