from RegexTemplater.RT import RT
from util import json_success, json_error, LOGGER_NAME
from flashtext import KeywordProcessor

from typing import Dict, Tuple
import ruamel.yaml
import logging
import json
import multiprocessing
import itertools
import os.path

log = logging.getLogger(LOGGER_NAME)

yaml = ruamel.yaml.YAML()
yaml.register_class(RT)

runtime_vars = {
    "$team1": "${team1}",
    "$team2": "${team2}",
}
""" 
rts = {
    [regex: RT]
}
"""
rts = {}
CONF_FILE = 'rts.yml'

def add_determinator(comment: str, dt_regex: str, dt_vars: Dict[str, str], section: str, bkoutcome: str) -> dict:
    if rts.get(dt_regex):
        return json_error(1, 'determinator with given regex already exists')
    else:
        try:
            rt = RT(dt_regex, dt_vars)
            rts[comment] = {
                'regex': dt_regex,
                'rt': rt,
                'section': section,
                'outcome': bkoutcome
            }
        except Exception as e:
            return json_error(2, str(e))
        return json_success()

def remove_determinator(comment: str) -> dict:
    if rts.pop(comment, False):
        return json_success()
    else: 
        return json_error(2, "key doesn't exists")

def get_determinators() -> str:
    def default(o):
        if type(o) is RT:
            return o.revars
    return json.dumps(rts, default=default)

def apply_determinator(outcome: str) -> dict:
    # Add caching !!!
    def __apply(rts_item: Tuple[str, Dict]) -> Tuple[str, str]: 
        comment, rts_body = rts_item
        vrs = rts_body['rt'].apply(outcome)
        kp = KeywordProcessor()
        for key, value in vrs.items():
            if (runtime_var := runtime_vars.get(value, None)):
                vrs[key] = runtime_var
            kp.add_keyword(key, vrs[key])

        return kp.replace_keywords(rts_body['section']), kp.replace_keywords(rts_body['outcome'])

    def __not_match(rts_item: Tuple[str, Dict]) -> bool:
        _, rts_body = rts_item
        return not rts_body['rt'].compiled.fullmatch(outcome)
    
    result = tuple()
    item = next(itertools.dropwhile(__not_match, rts.items()), None)
    if not item:
        return json_error(1, "Not found")
    # we sure it matches
    section, bkoutcome = __apply(item)
    return json.dumps({'section': section, 'outcome': bkoutcome})

def save_rts(fpath: str=""):
    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONF_FILE)
    with open(fpath, 'wb') as fstream:
        yaml.dump(rts, fstream)
        
def load_rts(fpath: str=""):    
    global rts
    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONF_FILE)
    with open(fpath, 'rb') as fstream:
        rts = yaml.load(fstream)