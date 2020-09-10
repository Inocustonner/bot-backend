import os
from ruamel.yaml import YAML
from datetime import date
import time
from threading import Lock
from util import json_error_str, LOGGER_NAME
import logging
import json
# from typing import Dict
PROPS_FILE_NAME = "props.yaml"
log = logging.getLogger(LOGGER_NAME)
yaml = YAML()

class Props:
  props = {'sections': {}}
  dirv = ""

def init_manager(dirv: str):
  Props.dirv = os.path.relpath(dirv)
  props_file_path = os.path.join(Props.dirv, PROPS_FILE_NAME)
  if not os.path.exists(dirv):
    os.makedirs(dirv)
  if os.path.exists(props_file_path):
    with open(props_file_path, 'r') as f:
      Props.props = yaml.load(f)

def dump_props():
  props_file_path = os.path.join(Props.dirv, PROPS_FILE_NAME)
  with open(props_file_path, 'w') as f:
    yaml.dump(Props.props, f)

def store_data(sec: str, key: str, data: bytes) -> str:
  if not sec.isalnum():
    raise ValueError("Invalid 'dirv' name, contains prohibitet symbols")
  sec_path = os.path.join(Props.dirv, sec) # section path
  if not os.path.exists(sec_path):
    os.mkdir(sec_path)

  # key = date.fromtimestamp(time.time()).isoformat() + "_" + key
  key_name = date.fromtimestamp(time.time()).isoformat() + "_" + key.replace('/', '!')
  with Lock():
    if sec not in Props.props['sections']:
      Props.props['sections'][sec] = []
    if key_name not in Props.props['sections'][sec]:
      Props.props['sections'][sec].append(key_name)
      log.info(f'Key "{key}" <> {sec}')

      with open(os.path.join(sec_path, key_name), 'wb') as f:
        f.write(data)
      return json.dumps({"success": {"key": key_name}})
    else:
      return json_error_str(1, "Key already exists")