from signalwire.voice_response import *
from flask import Flask, request, render_template
import sqlite3
import os
import logging
from flask_socketio import SocketIO,emit

ngrok_tunnel_url = os.environ['NGROK_URL']

def ai_prompt():
    ## AI SURVEY AGENT ##
    swml_web_hook_base_url = ngrok_tunnel_url
    swml_ai_prompt = '''Your name is John.  Your job is to survey the caller with polling questions retrieved from a database.
    
    ### How to follow up on questions answered and protocols to follow                   
        Stay on focus and on protocol.
        You are not capable of troubleshooting or diagnosing problems.
        Execute functions when appropriate
        Only allow answers to be on a numerical scale from 1 to 10.
        Never make up questions.  All questions should be provided by the database.
    
    ### Step 1
        Introduce yourself as John and let the user know you will be conducting a political poll with them.  Inform the user that you will be asking a series of questions, and the responses should be on a scale between 1 and 10, with 10 being high, and 1 being low.
        
    ### Step 2
        Ask the caller to provide their phone number for verication.  The phone number must be 10 digits in length to be valid.

    #### Step 2.1
        Use the callers phone number to look up their in the database using the lookup_caller function.

    #### Step 2.2
        Greet the customer by their first name and let them know that you will be starting the polling questions.
    
    ### Step 3
        Ask the caller the first question when it is returned.
        Always use the provided question_and_answer function to record each answer when given by the user, and retrieve the next question.  Send the question asked in the question argument, and the answer in the answer argument. 
        Repeat this process until there are no questions remaining.
    '''

    swml = {}
    swml['sections'] = {
        'main': [{
            'ai': {
                'languages': [
                    {
                        "engine": "elevenlabs",
                        "fillers": [
                            "ok",
                            "thanks"
                        ],
                        "name": "English",
                        "code": "en-US",
                        "voice": "josh"
                    }
                ],
                'params': {
                    'confidence': 0.6,
                    'barge_confidence': 0.1,
                    'top_p': 0.3,
                    'temperature': 1.0,
                    'openai_gcloud_version': "gcloud_speech_v2_async",
                    'swaig_allow_swml': True,
                    'conscience': True
                },
                'prompt': {
                    'text': swml_ai_prompt
                },
                'SWAIG': {
                    'functions': [
                        {
                            'function': 'lookup_caller',
                            'purpose': 'lookup the caller in the database to verify they exist already',
                            'web_hook_url': f"{swml_web_hook_base_url}/lookup_caller",
                            'argument': {
                                'type': 'object',
                                'properties': {
                                    'phone_number': {
                                        'type': 'string',
                                        'description': 'the callers phone_number'
                                    }
                                }
                            }
                        },
                        {
                            'function': 'question_and_answer',
                            'purpose': 'record the answer and get the next question for the survey',
                            'web_hook_url': f"{swml_web_hook_base_url}/question_and_answer",
                            'argument': {
                                'type': 'object',
                                'properties': {
                                    'answer': {
                                        'type': 'string',
                                        'description': 'the callers answer to the question'
                                    },
                                    'question': {
                                        'type': 'string',
                                        'description': 'the question that was asked by SurveyBot'
                                    }
                                }
                            }
                        },
                        {
                            'function': 'create_user_record',
                            'purpose': 'submit the payment for the caller',
                            'web_hook_url': f"{swml_web_hook_base_url}/create_user",
                            'argument': {
                                'type': 'object',
                                'properties': {
                                    'first_name': {
                                        'type': 'string',
                                        'description': 'the callers fist name'
                                    },
                                    'last_name': {
                                        'type': 'string',
                                        'description': 'the callers last name'
                                    },
                                    'age': {
                                        'type': 'string',
                                        'description': 'the callers age'
                                    },
                                    'phone_number': {
                                        'type': 'string',
                                        'description': 'the callers phone_number'
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }]
    }

    return (swml)

def lookup_caller():
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    swml = {}

    # Does this user already exist in the database
    # Don't create a new user if they do
    phone_number = request.json['argument']['parsed'][0]['phone_number']
    phone_number =  phone_number

    rows = cursor.execute(
        "SELECT id, first_name, last_name from dialto where to_num like ? limit 1",
        ('%' + phone_number,)
    ).fetchall()

    if len(rows) > 0:
        for row in rows:
            global user_id
            user_id = row[0]
            first_name = row[1]
            last_name = row[2]

            add_questions_to_user(user_id)       # Add any new questions to the caller's survey
            question = get_a_question(user_id)   # Get the first/next question for the caller

            if question != "0":
                swml['response'] = f"The callers name is {first_name} {last_name}.  The the first question is {question}"
                print (f"SWML: {swml}")
            else:
                swml['response'] = f"The user, {first_name} {last_name} already exists and they have already answered all of the questions in the survey.  Let the caller know they have already answered all of the questions and disconnect the call."
    else:
        swml['response'] = "The user does not exist, start with Step 2"

    db.close()
    print (f"{swml}")
    return swml

def question_and_answer(socketio):
    swml = {}
    global question_id
    cur_user_id=user_id
    cur_question_id=question_id
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    answer = request.json['argument']['parsed'][0]['answer']

    cursor.execute(
        "UPDATE survey_answers SET answer = ? WHERE user_id = ? AND id = ?",
        (answer, user_id, question_id)
    )
    db.commit()

    rows = cursor.execute(
        "SELECT question, id from survey_answers where user_id = ? and answer is NULL order by id limit 1",
        (user_id,)
    ).fetchall()

    if len(rows) > 0:
        for row in rows:
            question = row[0]
            question_id = row[1]
            swml['response'] = f"Success.  The answer has been recorded.  the next question is {question}"
                #socketio.emit('update_charts', {'update': [{'y':result_v["ans_count"] ,'x':result_v["ans"],'group':result_k}], 'traces': [0]}, namespace='/')
            print(f"{swml}")
    else:
        swml['response'] = f"Success.  The answer has been recorded.  There are no more questions in the survey.  Please hang up the call"
        print (f"{swml}")
    res_row = cursor.execute("SELECT question, answer FROM survey_answers WHERE user_id=? and id=?", (cur_user_id, cur_question_id,)).fetchone()
    if len(res_row) > 0:
       socketio.emit('update_chart',{'thing':res_row[0],'answer':res_row[1]}, namespace='/')

    db.close()
    return swml

def get_a_question(user_id):
    global question_id
    response = ""

    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT question, id from survey_answers where user_id = ? and answer is NULL order by id limit 1",
        (user_id,)
    ).fetchall()

    if len(rows) > 0:
        for row in rows:
            question = row[0]
            question_id = row[1]
            response = question
    else:
        response = "0"

    db.close()
    return (response)

def add_questions_to_user(user_id):
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    rows = cursor.execute(
        "select id, question from survey_questions"
    ).fetchall()
    for row in rows:
        survey_question_id = row[0]
        survey_question = row[1]
        cursor.execute(
            "INSERT INTO survey_answers (user_id, question_id, question) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT id from survey_answers where user_id = ? and question_id = ?)",
            (user_id, survey_question_id, survey_question, user_id, survey_question_id,)
        )

    db.commit()
    db.close()
    return

def test_ws(socketio):
    socketio.emit('update_chart',{'thing':'test chart 1','answer':10}, namespace='/')
    return "ok"
