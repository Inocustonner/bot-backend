from dataManager.dataManager import init_manager, store_data, dump_props
from util import json_error, f_last_error

from flask import Flask, request
from time import sleep
import traceback
import logging

app = Flask("bot-backend")
log = None
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

""" 
    Function stores given data in the file in 'dir' with 'key' name
    @@query_params:
        dir: str - parent directory for key
        key: str - key name
        (POST:data) - data to be written as the key's value
"""
@app.route('/api/store_data', methods=['POST'])
def store_data_rout():
    if (dirv := request.args.get('dir')) and (key := request.args.get('key')):
        try:
            return store_data(dirv, key, request.get_data())
        except KeyboardInterrupt:
            raise
        except Exception as e:
            log.error("Unhandled exception:\n" + f_last_error(logging.ERROR))
            return json_error(-1, "Unhandeled exception occured")
    
def flask_init(queue):
    global command_queue
    command_queue = queue
    # set flask logging to error only
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    init_manager('data')
    
def start_flask():
    global log
    host = 'localhost'
    port = 5050
    # print()
    log = logging.getLogger('bot-backend')
    log.info(f'Flask is started on {host}:{port}')
    try:
        app.run('localhost', 5050)
    finally:
        # on flask exit
        dump_props()