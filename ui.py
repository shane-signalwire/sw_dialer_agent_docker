from flask import render_template, request, Flask, jsonify
import requests
import sqlite3
import re
import os
import base64
import json

def index():
    return render_template('index.html')

def logs():
    response=""
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT id, to_num, from_num, amd_result from dialto where amd_result is not null order by id desc limit 25"
    ).fetchall()

    response="    ID     |  Dialed Number  |  Calling Number |  AMD Result<br>+++++++++++++++++++++++++++++++++++++++<br>"
    for i, d, c, a in rows:
        response=response + str(i) + "  |  " + str(d) + "  |  " + str(c) + "  |  " + str(a) + "<br>"

    return render_template('index.html', log_result=response)

def post_index():
    response = ""

    if request.form.get("dial"):
        #from_num_ = request.form.get("fnum")
        from_num_ = os.environ['PHONE_NUMBER']
        if from_num_ == "" or from_num_ is None:
            response = "Please configure the caller ID"
            return render_template('index.html', result=response)
        to_num_ = request.form.get("tnum")
        first_name_ = request.form.get("first_name")
        last_name_ = request.form.get("last_name")

        phone_num_regex = re.compile(r'^\+(?:[0-9]){6,14}[0-9]$')
        good_from_num = phone_num_regex.search(from_num_)
        good_to_num = phone_num_regex.search(to_num_)

        if good_from_num is None:
            response = "The from number is not valid"
            return render_template('index.html', result=response)

        elif good_to_num is None:
            response = "The to number is not valid"
            return render_template('index.html', result=response)

        else:
            db = sqlite3.connect("/root/database.db")
            cursor = db.cursor()

            cursor.execute(
                "INSERT INTO dialto (to_num, from_num, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (to_num_, from_num_, first_name_, last_name_,)
            )

            db.commit()
            db.close()
        
            response =  f"<center>{first_name_} {last_name_} has been added to the poll calling queue.</center>"


    elif request.form.get("start_dialer"):
        os.system("./amd.py &")

        response = f"<center>Dialer Started!</center>"


    elif request.form.get("add_question"):
        question_ = request.form.get("question_textarea")
        db = sqlite3.connect("/root/database.db")
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO survey_questions (question) VALUES (?)",
            (question_,)
        )

        db.commit()
        db.close()

        response = f"<center> {question_} has been added to the poll</center>"

    elif request.form.get("conf_dialer"):

        # SET THE ENVIRONMENT
        os.environ['PHONE_NUMBER'] = request.form.get("fnum")
        os.environ['PROJECT_ID'] = request.form.get("swproject")
        os.environ['REST_API_TOKEN'] = request.form.get("swtoken")
        os.environ['SIGNALWIRE_SPACE'] = request.form.get("swspace")

        # TODO:  Move these into their own functions, instead of cluttering the UI code.
        # TODO:  Phone number will require +1, this should be validated before calls are made.
        phone_number = os.environ['PHONE_NUMBER'].replace('+', '%2b') # Take the phone number and URL encode.

        signalwire_space = os.environ['SIGNALWIRE_SPACE']
        project_id = os.environ['PROJECT_ID']
        rest_api_token = os.environ['REST_API_TOKEN']

        # Generate the basic auth hash.
        auth = str(project_id + ":" + rest_api_token)
        auth_bytes = auth.encode('ascii')
        base64_auth_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_auth_bytes.decode('ascii')
        http_basic_auth = base64_auth

        # Look up the number to get the SID
        query_params = "?filter_number=" + phone_number
        headers = {
            'Accept': 'applications/json',
            'Authorization': 'Basic %s' % http_basic_auth
        }
        payload = ""
        fqdn = f"https://{signalwire_space}.signalwire.com/api/relay/rest/phone_numbers{query_params}"

        response = requests.request('GET', fqdn , headers=headers, data=payload)
        output = json.loads(response.text)
        sid = (output["data"][0]["id"])

        # Update the number to the NGROK
        ngrok_tunnel_url = os.environ['NGROK_URL']
        fqdn = f"https://{signalwire_space}.signalwire.com/api/relay/rest/phone_numbers/{sid}"
        call_relay_script_url = f"{ngrok_tunnel_url}/ai"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Basic %s' % http_basic_auth
        }
        payload = json.dumps({
            "call_handler": "relay_script",
            "call_relay_script_url": call_relay_script_url

        })
        response = requests.request('PUT', fqdn, headers=headers, data=payload)

        response = "<center>Configuration Saved</center>"

    elif request.form.get("configure_dialer"):
        response= '''
<form action="/" method="POST">
<center>
Signalwire Space:    <input type="text" id="sw_space" name="swspace" size="25"><br>
SignalWire Project ID:  <input type="text" id="sw_project" name="swproject" size="25"><br>
SignalWire API Token:   <input type="text" id="sw_token" name="swtoken" size="25"><br>
Caller ID Number:    <input type="text" id="from_number" name="fnum" size="25"></center><br><br>
<input type="submit" name="conf_dialer" value="Submit">
</form>'''

    elif request.form.get("poll_participant"):
        response = '''
<form action="/" method="POST">
<center>First Name:&emsp;&emsp;&emsp;<input type="text" size="25" name="first_name"></text><br>
Last Name:&emsp;&emsp;&emsp;<input type="text" size="25" name="last_name"></text><br>
Phone Number:&emsp;<input type="text" size="25" name="tnum"></text></center><br><br>
<input type="submit" name="dial" value="Submit">
</form>'''

    elif request.form.get("poll_questions"):
        response = '''
<form action="/" method="POST">
<center>Add A Poll Question:<br>
<textarea rows="10" cols="50" name="question_textarea"></textarea></center><br><br>
<input type="submit" name="add_question" value="Submit">
</form>'''

    else:
        response = ""
        
    
    return render_template('index.html', result=response)


def initial_results():
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()
    res_rows = cursor.execute("select count(1) as answers_count, question,answer from survey_answers group by question,answer").fetchall();
    results={} 
    if len(res_rows) > 0:
        for res_row in res_rows:
            if res_row[1] not in results:
                results[res_row[1]]={"ans":[],"ans_count":[]}
        
        for res_row in res_rows:
            if res_row[1] in results:
                results[res_row[1]]["ans"].append(res_row[2])
                results[res_row[1]]["ans_count"].append(res_row[0])
    print(results)
    db.close()
    return jsonify({'results': results})
def results():
    return render_template('results.html')

def get_survey_results():
    db = sqlite3.connect("/root/database.db")
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(1) AS answers_count, question, answer FROM survey_answers GROUP BY question, answer")
    res_rows = cursor.fetchall()

    results = {}
    if len(res_rows) > 0:
        for res_row in res_rows:
            question = res_row[1]
            answer = res_row[2]
            count = res_row[0]

            if question not in results:
                results[question] = {"ans": [], "ans_count": []}

            results[question]["ans"].append(answer)
            results[question]["ans_count"].append(count)

    return jsonify({'survey_results': results})
