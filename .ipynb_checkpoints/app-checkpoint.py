'''
At the command line, run 
conda activate PIC16B
export FLASK_ENV=development
flask run
'''
from flask import Flask, g, render_template, request

import sklearn as sk
import matplotlib.pyplot as plt
import numpy as np
# import pickle
import sqlite3

# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure

import io
import base64

DB_NAME = './messages_db.sqlite'
def get_message_db():
    '''
    Retrieves the message database
    '''
    try:
        return g.message_db
    except:
        with sqlite3.connect(DB_NAME) as conn:
            g.message_db = conn
            cursor = conn.cursor()
            query = '''
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    message TEXT);
                    '''
            cursor.execute(query)
            return g.message_db
    
def insert_message(request):
    '''
    inserts a message into the database
    @ input:
    - request: URL requesting data from
    @ output:
    - message (str): the message the user input
    - handle (str): the handle of the user
    '''
    message = request.form['message']
    handle = request.form['user']
    
    with get_message_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (id, username, message) VALUES ((SELECT COUNT(*) FROM messages) + 1, ?, ?)", (handle, message))
        conn.commit()
    return message, handle
    
def random_messages(n):
    '''
    picks at most n random messages from the message database.
    @ input:
    - n (int): how many messages to display
    @ output:
    - msgs (list): list of random messages
    '''
    with get_message_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, message FROM messages ORDER BY RANDOM() LIMIT {0};".format(n))
        msgs = cursor.fetchall()
        return msgs
    
### stuff from last class
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        try:
            msg, hndl = insert_message(request)
            return render_template('submit.html', name = hndl, message = msg)
        except:
            return render_template('submit.html', error = True)

@app.route('/view/')
def view():
    try:
        msgs = random_messages(5)
        return render_template('view.html', msgs = msgs)
    except:
        return render_template('view.html', error = True)
# @app.route('/ask/', methods=['POST', 'GET'])
# def ask():
#     if request.method == 'GET':
#         return render_template('ask.html')
#     else:
#         try:
#             return render_template('ask.html', name=request.form['name'], student=request.form['student'])
#         except:
#             return render_template('ask.html')
#######
