from  flask_main import *
import connectionManager
import multiprocessing
from util import create_logger
from ruamel.yaml import YAML
import os

yaml = YAML()

CONFIG_FILE_NAME = "conf.yml"
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
config = {}

def ensure_config():
    global config
    config = {
        "wsserver_addr": "localhost:5757",
        "server_addr": "localhost:5050"
    }
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_stream:
            config.update(yaml.load(config_stream))
    else:
        with open(CONFIG_FILE_PATH, 'w') as config_stream:
            yaml.dump(config, config_stream)

def main():
    ensure_config()
    wsserver_ip, wsserver_port = config["wsserver_addr"].split(':')
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=connectionManager.init, args=(queue, wsserver_ip, int(wsserver_port)))
    proc.start()

    create_logger()
    flask_init(queue)
    start_flask()

if __name__ == "__main__":
    main()
