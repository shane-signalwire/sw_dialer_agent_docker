#!/usr/bin/env python3
# Author: Shane Harrell

from datetime import date,timedelta
import sys,os
import logging
import sqlite3
import time
from signalwire.rest import Client as signalwire_client

from flask import Flask
from flask import request
from flask import render_template


#from signalwire.voice_response import *
#from twilio.twiml.messaging_response import Message, MessagingResponse


# TODO:
# Insert into DB
# Edit an entry
# Remove an Entry


calendar = Flask(__name__)

@calendar.route('/')
def my_form():
    return render_template('my-form.html')


@calendar.route('/', methods=['POST'])
def my_form_post():
    response=""

    # Connect to DB
    db = sqlite3.connect("calendar.db")
    cursor = db.cursor()

    date_ = request.form.get("date")
    time_ = request.form.get("time")
    desc =  request.form.get("desc")

    cursor.execute(
        "INSERT INTO cal (date, time, text) VALUES (?, ?, ?)",
        (date_, time_, desc,)
    )

    db.commit()
    db.close()
    response = (f"{response} A new entry has been added for {date_} at {time_}")
    return response
    #sys.exit()


today = date.today()
tomorrow = today + timedelta(1)

# Connect to DB
db = sqlite3.connect("calendar.db")
cursor = db.cursor()

def send_text(text):
    '''Sends an SMS Text Message via SignalWire API'''
    signalwire_space = "shane-harrell.signalwire.com"
    project_id = "0fd6cfc3-ac8c-4b6f-9bc3-57048cf6a7f3"
    api_token = "PTa7de9a82bb8711f22472d05174633af2db1317e2e23298aa"
    from_num = "+12136576969"
    #to_num_list = [ "+14403346366", "+14402275604" ]
    text_body = text
    
    for to_num in to_num_list:
        client = signalwire_client(project_id, api_token, signalwire_space_url = signalwire_space)
        message = client.messages.create (
          to = to_num,
          from_= from_num,
          body=text_body
     )


def exact_date(date_):
    rows = cursor.execute(
        "SELECT id, date, time, text from cal where date = ? order by time asc",
    (date_,)
    ).fetchall()

    output = ""
    for row in rows:
        date_ = row[1]
        time_ = row[2]
        text = row[3]

        output = output + "\n  " + time_ + ": " + text
    output =  (f"=============================\n{date_}{output}\n")
    return (output)

def tags(tag):
    rows = cursor.execute(
      "SELECT id, date, time, text from cal where tags = ? order by date asc",
      (tag,)
    ).fetchall()
   
    output = ""
    for row in rows:
        date_ = row[1]
        time_ = row[2]
        text = row[3]

        output = output + "\n  " + date_ + "\n\t" + time_ + ": " + text
    #print ("=============================")
    final_output =  (f"{tag}: {output}\n")
    return (final_output)

if len(sys.argv) > 1:
    opt = sys.argv[1]

    if (opt == "--date"):
      date_ = sys.argv[2]
      r = exact_date(date_)
      final_output =  (f"{r}")
      print (final_output)
      #send_text(final_output)
      sys.exit()

    elif (opt == "--tag"):
      final_output = "=============================\n"
      t = sys.argv[2]
      tl = t.split(',')
      for tag in tl: 
        output = tags(tag) + "\n"
        #print ("=============================")
        final_output = (f"{final_output}{output}")
      print (final_output)
      sys.exit()



######################
# Get rows for today #
######################
rows = cursor.execute(
    "SELECT id, date, time, text from cal where date = ? order by time asc",
    (today,)
).fetchall()

output = ""
for row in rows:
    date_ = row[1]
    time_ = row[2]
    text = row[3]

    output = output + "\n  " + time_ + ": " + text
final_output = (f"=============================\nToday -- {date_}{output}\n")

#########################
# Get rows for tomorrow #
#########################
rows = cursor.execute(
    "SELECT id, date, time, text from cal where date = ? order by time asc",
    (tomorrow,)
).fetchall()

output = ""
for row in rows:
    date_ = row[1]
    time_ = row[2]
    text = row[3]

    output = output + "\n  " + time_ + ": " + text
final_output =  (f"{final_output}\nTomorrow -- {date_}{output}\n=============================")
print (final_output)
#send_text (final_output)



if __name__ == '__main__':
    calendar.run()