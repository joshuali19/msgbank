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
    @ output:
    - g.message_db: a database storing messages
    '''
    try:
        # returns a database
        return g.message_db
    except:
        # connect to a database
        with sqlite3.connect(DB_NAME) as conn:
            g.message_db = conn
            
            # create a table if it doesn't exist
            cursor = conn.cursor()
            query = '''
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    message TEXT);
                    '''
            cursor.execute(query)
            # return the database
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
    # obtain the request and the information
    message = request.form['message']
    handle = request.form['user']
    
    # get the table, and insert it into the table
    with get_message_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (id, username, message) VALUES ((SELECT COUNT(*) FROM messages) + 1, ?, ?)", (handle, message))
        conn.commit() # save changes
    # return message and handle
    return message, handle
    
def random_messages(n):
    '''
    picks at most n random messages from the message database.
    @ input:
    - n (int): how many messages to display
    @ output:
    - msgs (list): list of random messages
    '''
    # get the database
    with get_message_db() as conn:
        cursor = conn.cursor()
        # select the random username and message
        cursor.execute("SELECT username, message FROM messages ORDER BY RANDOM() LIMIT {0};".format(n))
        msgs = cursor.fetchall()
        # return list
        return msgs
    
### stuff from last class
app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html') # default submit.html display
    else: # if someone posts
        try:
            # insert the message to the database
            msg, hndl = insert_message(request)
            # display submit.html with conditions
            return render_template('submit.html', name = hndl, message = msg)
        except:
            # return an error
            return render_template('submit.html', error = True)

@app.route('/view/')
def view():
    try:
        # get 5 random messages
        msgs = random_messages(5)
        # display it
        return render_template('view.html', msgs = msgs)
    except:
        # return an error
        return render_template('view.html', error = True)
