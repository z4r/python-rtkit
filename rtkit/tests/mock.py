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
    if form['Queue'] == 'ERR':
        body = 'RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# Could not create ticket. Queue not set\n\n'
    elif form['Queue'] == 'NOPERM':
        body = "RT/3.8.10 200 Ok\n\n# Could not create ticket.\n# No permission to create tickets in the queue '___Admin'\n\n"
    else:
        body = 'RT/3.8.10 200 Ok\n\n# Ticket 1 created.\n\n'
    response = make_response(body, 200)
    return response
