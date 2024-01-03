from flask import render_template, request, Flask
import sqlite3
import re
import logging

def index():
    return render_template('my-form.html')

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

    return response

def add_to_queue():
    response = ""
    from_num_ = request.form.get("fnum")

    phone_num_regex = re.compile(r'^\+1\d{10}$')
    good_num = phone_num_regex.search(from_num_)

    if good_num is None:
        response = "The from number is not valid"
        return response


    numbers = str.split(request.form['dest_list'])

    # Put each number in the database for dialier pickup
    for num in numbers:
        db = sqlite3.connect("/root/database.db")
        cursor = db.cursor()

        to_num_ = num

        phone_num_regex = re.compile(r'^\+1\d{10}$')
        good_num = phone_num_regex.search(to_num_)

        if good_num is not None:
            cursor.execute(
              "INSERT INTO dialto (to_num, from_num) VALUES (?, ?)",
              (to_num_, from_num_,)
            )

            db.commit()
            db.close()
            response = response + to_num_ + " added to queue\n<br>"
        else:
            logging.info(f'{to_num_} is not a valid number')
            response =  response + to_num_ + ": is not a valid number<br>"

    return response