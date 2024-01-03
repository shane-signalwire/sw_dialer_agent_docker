#!/usr/bin/env python3
# Author: Shane Harrell

from signalwire.voice_response import *
import sqlite3
from flask import Flask, request, render_template
import ngrok
import os

listener = ngrok.forward(5000,authtoken_from_env=True)
os.environ['NGROK_TUNNEL_ADDRESS'] = listener.url()
ngrok_tunnel_url = os.environ['NGROK_TUNNEL_ADDRESS']

# TODO:  I need to do something with this in the UI
print (f"The NGROK TUNNEL URL is {ngrok_tunnel_url}")

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

cursor.execute(survey_questions_table)
cursor.execute(survey_answers_table)
cursor.execute(survey_user_table)
db.commit()


# Importing Sub-Route
# Attempting to keep the code more neat and modular
import ui
import ai

app = Flask(__name__)

# User Interface Route(s)
app.add_url_rule('/', view_func=ui.index, methods=['GET'])
app.add_url_rule('/', view_func=ui.add_to_queue, methods=['POST'])
app.add_url_rule('/logs', view_func=ui.logs, methods=['POST'])

# AI Agent
app.add_url_rule('/ai', view_func=ai.ai_prompt, methods=['POST'])
app.add_url_rule('/lookup_caller', view_func=ai.lookup_caller, methods=['POST'])
app.add_url_rule('/create_user', view_func=ai.create_user_record, methods=['POST'])
app.add_url_rule('/question_and_answer', view_func=ai.question_and_answer, methods=['POST'])


if __name__ == '__main__':
    app.run(host='0.0.0.0')