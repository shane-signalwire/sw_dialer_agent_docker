#!/usr/bin/env python3
# Author: Shane Harrell

from signalwire.voice_response import *
import sqlite3
from flask import Flask, request, render_template
#import ngrok
import os
import logging
from flask_socketio import SocketIO,emit


from pyngrok import ngrok
public_url = ngrok.connect(5000)
print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000\"".format(public_url))
os.environ['NGROK_TUNNEL_ADDRESS'] = public_url.public_url
ngrok_tunnel_url = os.environ['NGROK_TUNNEL_ADDRESS']
print(ngrok_tunnel_url)
# TODO:  I need to do something with this in the UI
# Need to make a button to auto update the agent number
#print (f"The NGROK TUNNEL URL is {ngrok_tunnel_url}")

db = sqlite3.connect("/root/database.db")
cursor = db.cursor()

# Create the survey tables if they don't exist
survey_questions_table = """ CREATE TABLE if not exists survey_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL
    );"""

survey_answers_table = """ CREATE TABLE if not exists survey_answers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT
    );"""

survey_user_table = """ CREATE TABLE if not exists user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    phone_number TEXT NOT NULL
    );"""

# Create the dialto table if it doesn't exist
dialto_table = """ CREATE TABLE if not exists dialto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_num TEXT NOT NULL,
    from_num TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    amd_result TEXT
    );"""

cursor.execute(survey_questions_table)
cursor.execute(survey_answers_table)
cursor.execute(survey_user_table)
cursor.execute(dialto_table)
db.commit()


# Importing Sub-Route
# Attempting to keep the code more neat and modular
import ui
import ai

app = Flask(__name__)
socketio = SocketIO(app)
# User Interface Route(s)
app.add_url_rule('/', view_func=ui.index, methods=['GET'])
app.add_url_rule('/', view_func=ui.post_index, methods=['POST'])
app.add_url_rule('/logs', view_func=ui.logs, methods=['POST'])
app.add_url_rule('/results', view_func=ui.results, methods=['GET'])
app.add_url_rule('/initial_results', view_func=ui.initial_results, methods=['GET','POST'])
app.add_url_rule('/get_survey_results', view_func=ui.get_survey_results, methods=['GET','POST'])
# AI Agent
app.add_url_rule('/ai', view_func=ai.ai_prompt, methods=['POST'])
app.add_url_rule('/lookup_caller', view_func=ai.lookup_caller, methods=['POST'])
app.add_url_rule('/question_and_answer', view_func=ai.question_and_answer, methods=['POST'],defaults={'socketio': socketio})
app.add_url_rule('/test_ws', view_func=ai.test_ws, methods=['GET'],defaults={'socketio': socketio})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')




if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    #from pyngrok import ngrok
    #public_url = ngrok.connect(5000)
    #print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:5000\"".format(public_url))
    #os.environ['NGROK_TUNNEL_ADDRESS'] = public_url
    socketio.run(app, host="0.0.0.0", port=5000,allow_unsafe_werkzeug=True)
