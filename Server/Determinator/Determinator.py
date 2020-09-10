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
import re
import pprint

log = logging.getLogger(LOGGER_NAME)
pp = pprint.PrettyPrinter(2)

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

def ensure_fullstring_match(regex: str) -> str:
    if not regex.endswith('$'):
        regex += '$'
    if not regex.startswith('^'):
        regex = '^' + regex
    return regex

def add_determinator(comment: str, dt_regex: str, dt_vars: Dict[str, str],
                     section: str, bkoutcome: str) -> dict:
    global rts
    dt_regex = ensure_fullstring_match(dt_regex)

    if section:
        section = ensure_fullstring_match(section)
    bkoutcome = ensure_fullstring_match(bkoutcome)

    log.debug('\n\t'.join(['RTS: adding - {', 
                          f'comment: {comment}',
                          f'regex: {dt_regex}', 
                          f'vars: {dt_vars}',
                          f'section: {section}', 
                          f'bkoutcome: {bkoutcome}',
                          '}']))
    try:
        rt = RT(dt_regex, dt_vars, True)
        rts[comment] = {
            'regex': dt_regex,
            'rt': rt,
            'section': section,
            'outcome': bkoutcome
        }
        log.debug(f'New rts \n{pp.pformat(rts)}')
    except Exception as e:
        return json_error(2, str(e))
    return json_success()


def remove_determinator(comment: str) -> dict:
    log.debug(f'RTS: Removing rt with key=\'{comment}\'')
    if rts.pop(comment, False):
        return json_success()
    else:
        return json_error(2, "key doesn't exists")


def get_determinators() -> str:
    global rts
    def default(o):
        if type(o) is RT:
            return o.revars
    return json.dumps(rts, default=default).replace('"rt":', '"vars":') # for front end


def apply_determinator(outcome: str) -> str:
    # Add caching !!!
    def __apply(rts_item: Tuple[str, Dict]) -> Tuple[str, str]:
        comment, rts_body = rts_item
        vrs = rts_body['rt'].apply(outcome)
        kp = KeywordProcessor()
        for key, value in vrs.items():
            if (runtime_var := runtime_vars.get(value, None)):
                vrs[key] = runtime_var
            kp.add_keyword(key, vrs[key])

        return kp.replace_keywords(rts_body['section']), kp.replace_keywords(
            rts_body['outcome'])

    def __not_match(rts_item: Tuple[str, Dict]) -> bool:
        _, rts_body = rts_item
        return not rts_body['rt'].compiled.fullmatch(outcome)

    log.debug(f'RTS: applying to {outcome}')
    result = tuple()
    item = next(itertools.dropwhile(__not_match, rts.items()), None)
    if not item:
        log.debug(f'RTS: coulndn\'apply for {outcome}, appropriate regex was not found')
        return json_error(1, "Not found")
    # we sure it matches
    section, bkoutcome = __apply(item)
    log.debug(f'RTS: For {outcome} returning - ({section}, {bkoutcome})')
        # replace \( with \\\\(
    # section = re.sub(r'(?<=[^\\])\\(?=[\w().])', '\\\\', section)
    # bkoutcome = re.sub(r'(?<=[^\\])\\(?=[\w().])', '\\\\', bkoutcome)
    section = section.replace('\\', '\\' * 2)
    bkoutcome = bkoutcome.replace('\\', '\\' * 2)
    return json.dumps({'section': f'`{section}`', 'outcome': f'`{bkoutcome}`'})


def save_rts(fpath: str = ""):
    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             CONF_FILE)
    log.info(f"Saving rts to '{fpath}'")
    with open(fpath, 'wb') as fstream:
        yaml.dump(rts, fstream)


def load_rts(fpath: str = ""):
    global rts
    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             CONF_FILE)
    if os.path.exists(fpath):
        log.info(f"Loading rts from '{fpath}'")
        with open(fpath, 'rb') as fstream:
            rts = yaml.load(fstream)
    else:
        log.info(f"Creating empty rts")
        rts = {}