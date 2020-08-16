from flask import Flask
from time import sleep
from flask import request
import logging

app = Flask("bot-backend")

# Queue for interprocess communication
command_queue = None

@app.route('/api/')
def index():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip

# GET IS FOR TESTING PURPOSES
@app.route('/api/send_info', methods=['POST'])
def send_info():
    data = request.get_data().decode("utf8")
    command_queue.put({'cmd': 'sendall', 'data': data})
    return 'Success'

@app.route('/api/store_data', methods=['POST'])
def save_html():
    if (dirv := request.args.get('dir')) and (key := request.args.get('key')):
        save_data(dirv, key, request.get_data())
    
def flask_init(queue):
    global command_queue
    command_queue = queue

    # set flask logging to error only
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)