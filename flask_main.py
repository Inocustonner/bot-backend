from flask import Flask
app = Flask("mybackend")
from time import sleep
from flask import request
import logging

# Queue for interprocess communication
command_queue = None

@app.route('/api/')
def index():
    return "hi"

# GET IS FOR TESTING PURPOSES
@app.route('/api/send_info', methods=['POST'])
def send_info():
    print(request.get_data())
    command_queue.put({'cmd': 'sendall', 'data': request.get_data().decode('utf8')})
    return '123'

def flask_init(queue):
    global command_queue
    command_queue = queue

    # set flask logging to error only
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)