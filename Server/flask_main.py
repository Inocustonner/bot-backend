from dataManager.dataManager import init_manager, store_data, dump_props
from util import json_error_str, f_last_error
from Determinator.Determinator import *

from flask import Flask, request
from time import sleep
import traceback
import logging

app = Flask("bot-backend")
log = None
# Queue for interprocess communication
command_queue = None

jsonify = json.dumps

@app.route('/api/determinators/apply', methods=["POST"])
def determinators_apply():
    """ Edit determinators """
    try:
        data = json.loads(request.get_data().decode('utf8'))
        log.debug(f'Got: {data}')
        for key, values in data.items():
            ret = add_determinator(key, values['regex'], values['vars'], list(map(lambda obj: tuple(obj.values()), values['SOPairs'])))
            if (ret.get('error')): return ret, 400
        return ret
    except Exception as e:
        return json_error_str(-1, str(e)), 400

@app.route('/api/determinators/remove', methods=["POST"])
def determinators_remove():
    comment = json.loads(request.get_data().decode('utf8'))['type']
    ret = remove_determinator(comment)
    code = 400 if ret.get('error') else 200
    return jsonify(ret), code

@app.route('/api/determinators/get_determinators')
def determinators_get():
    return get_determinators()

# Recives via query outcome, parses and return Section and Outcome for bk
@app.route('/api/determinators/determine')
def determine():
    return apply_determinator(request.args.get('outcome'))

@app.route('/api/')
def index():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return f"DEV SERVER:\n{ip}"

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
    
def start_flask(host='localhost', port=5050):
    global log
    log = logging.getLogger('bot-backend')
    log.info(f'Flask is started on {host}:{port}')
    try:
        load_rts()
        app.run(host, port)
    finally:
        # on flask exit
        save_rts()
        dump_props()
