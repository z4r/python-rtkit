import logging
from flask.app import Flask
from flask.globals import request
from flask.helpers import make_response
from rtkit.parser import RTParser


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
logging.root.addHandler(NullHandler())

app = Flask(__name__)


@app.route('/ticket/new', methods=['POST'])
def create_tkt():
    form = dict(RTParser.parse(request.form.get('content', ''), RTParser.decode)[0])
    if form['Queue'] == '2':
        body = 'RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# Could not create ticket. Queue not set\n\n'
    elif form['Queue'] == '3':
        body = "RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# No permission to create tickets in the queue '___Admin'\n\n"
    else:
        body = 'RT/3.8.10 200 Ok\n\n# Ticket 1 created.\n\n'
    response = make_response(body, 200)
    return response


@app.route('/ticket/<tid>', methods=['GET', 'POST'])
def readupdate_tkt(tid):
    if request.method == 'GET':
        if tid == '2':
            body = 'RT/3.8.10 200 Ok\n\n# Ticket 2 does not exist.\n\n\n'
        elif tid == '3':
            body = 'RT/3.8.10 401 Credentials required\n'
        else:
            body = '''RT/3.8.10 200 Ok

id: ticket/1
Queue: General
Owner: Nobody
Creator: pyrtkit
Subject: pyrt-create4
Status: open
Priority: 5
InitialPriority: 0
FinalPriority: 0
Requestors:
Cc:
AdminCc:
Created: Sun Jul 03 10:48:57 2011
Starts: Not set
Started: Not set
Due: Not set
Resolved: Not set
Told: Wed Jul 06 12:58:00 2011
LastUpdated: Thu Jul 07 14:42:32 2011
TimeEstimated: 0
TimeWorked: 25 minutes
TimeLeft: 0


'''
    else:
        form = dict(RTParser.parse(request.form.get('content', ''), RTParser.decode)[0])
        if form['Queue'] == '3':
            body = 'RT/3.8.10 409 Syntax Error\n\n# queue: You may not create requests in that queue.\n\n'
        else:
            body = ''
    response = make_response(body, 200)
    return response
