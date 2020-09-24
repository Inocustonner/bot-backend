from RegexTemplater.RT import RT
from util import *
from flashtext import KeywordProcessor

from typing import Dict, Tuple, List
import ruamel.yaml
import logging
import json
import multiprocessing
import itertools
import os.path
import re
import pprint
import os
import shutil

log = logging.getLogger(LOGGER_NAME)
pp = pprint.PrettyPrinter(2)

yaml = ruamel.yaml.YAML()
yaml.register_class(RT)

runtime_vars = {
    "$team1": "${team1}",
    "$team2": "${team2}",
}
""" 
rts[comment] = {
        regex: str,
        rt: RT,
        SOPairs: [(section, outcome)]
}
"""
rts = {}
loaded_from_backup = False
CONF_FILE = "rts.yml"
BACKUP_FILE_PREFIX = "~backup."


def ensure_fullstring_match(regex: str) -> str:
    if not regex.endswith("$"):
        regex += "$"
    if not regex.startswith("^"):
        regex = "^" + regex
    return regex


def format_SO(so: Tuple[str, str]) -> Tuple[str, str]:
    section, outcome = so
    if section:
        section = r"\s*".join(ensure_fullstring_match(section).split())
    outcome = r"\s*".join(ensure_fullstring_match(outcome).split())
    return (section, outcome)


def add_determinator(comment: str, dt_regex: str, dt_vars: Dict[str, str],
                     SOPairs: List[Tuple[str, str]]) -> dict:
    global rts
    if comment == "":
        return json_error(3, "Empty type is not allowed")
    if len(SOPairs) == 0:
        return json_error(4, "At least should be 1 pair of determinators")
    i = 0
    for i, pair in enumerate(SOPairs):
        SOPairs[i] = format_SO(pair)

    dt_regex = ensure_fullstring_match(dt_regex)
    log.debug("\n\t".join([
        "RTS: adding - {",
        f"comment: {comment}",
        f"regex: {dt_regex}",
        f"vars: {dt_vars}",
        f"SOPairs: {pp.pformat(SOPairs)}"
        "}",
    ]))
    try:
        rt = RT(dt_regex, dt_vars, True)
        rts[comment] = {"regex": dt_regex, "rt": rt, "SOPairs": SOPairs}
    except Exception as e:
        log.error(f_last_error(logging.ERROR))
        return json_error(2, str(e))
    save_rts()
    return json_success()


def remove_determinator(comment: str) -> dict:
    log.debug(f"RTS: Removing rt with key='{comment}'")
    if rts.pop(comment, False):
        return json_success()
    else:
        return json_error(2, "key doesn't exists")


# ONLY FOR FRONT-END bcs returns formatted version of rts
def get_determinators() -> str:
    global rts

    def default(o):
        if type(o) is RT:
            return o.revars

    new_rts = {}
    for comment, body in rts.items():
        new_rts[comment] = body.copy()
        new_rts[comment]["SOPairs"] = list(
            map(lambda pair: {
                "section": pair[0],
                "outcome": pair[1]
            }, new_rts[comment]["SOPairs"]))
    return (json.dumps(new_rts,
                       default=default).replace('"rt":', '"vars":').replace(
                           '"^', '"').replace('$"', '"'))  # for front end


def format_out(o: str) -> str:
    o = o.replace('\\', '\\' * 2)
    return f"`{o}`"


def apply_determinator(outcome: str) -> str:
    global rts

    # Add caching !!!
    def __apply(rts_item: Tuple[str, Dict]) -> Tuple[str, str]:
        comment, rts_body = rts_item
        vrs = rts_body["rt"].apply(outcome)
        SOPairs = rts_body["SOPairs"].copy()
        for i, pair in enumerate(SOPairs):
            section, bkoutcome = pair
            for key, value in vrs.items():
                if (runtime_var := runtime_vars.get(value, None)):
                    vrs[key] = runtime_var
                bkoutcome = bkoutcome.replace(key, vrs[key])
                section = section.replace(key, vrs[key])
            SOPairs[i] = (format_out(section), format_out(bkoutcome))
        return SOPairs

    def __not_match(rts_item: Tuple[str, Dict]) -> bool:
        _, rts_body = rts_item
        return not rts_body["rt"].compiled.fullmatch(outcome)

    log.debug(f"RTS: applying to {outcome}")
    result = tuple()
    item = next(itertools.dropwhile(__not_match, rts.items()), None)
    if not item:
        log.debug(
            f"RTS: coulndn'apply for {outcome}, appropriate regex was not found"
        )
        return json_error_str(1, "Not found")
    # we sure it matches
    SOPairs = __apply(item)

    log.debug(f"RTS: For {outcome} returning - {SOPairs}")
    # replace \( with \\\\(
    # section = re.sub(r'(?<=[^\\])\\(?=[\w().])', '\\\\', section)
    # bkoutcome = re.sub(r'(?<=[^\\])\\(?=[\w().])', '\\\\', bkoutcome)
    return json.dumps(SOPairs)


def save_rts(fpath: str = ""):
    global rts
    global loaded_from_backup
    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             CONF_FILE)
    fbackup = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           BACKUP_FILE_PREFIX + CONF_FILE)
    # create copy in case something fails
    if os.path.exists(fpath) and not loaded_from_backup and len(rts):
        shutil.copyfile(fpath, fbackup)
    log.info(f"Saving rts to '{fpath}'")
    try:
        with open(fpath, "wb") as fstream:
            yaml.dump(rts, fstream)
    except Exception as e:
        log.error(f_last_error(logging.ERROR))
        os.remove(fpath)
        shutil.copyfile(fbackup, fpath)
        log.info(f"Restoring from backup {fbackup}")


def load_rts(fpath: str = ""):
    def create_rts():
        global rts
        log.info(f"Creating empty rts")
        rts = {}

    def __load_rts(path: str) -> bool:
        global rts
        log.info(f"Loading rts from '{path}'")
        with open(path, "rb") as fstream:
            rts = yaml.load(fstream)
        return bool(rts)

    if not fpath:
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             CONF_FILE)
    fbackup = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           BACKUP_FILE_PREFIX + CONF_FILE)
    if os.path.exists(fpath) and __load_rts(fpath):
        return

    # if failed to load from CONF_FILE and backup exists try to load backup
    if os.path.exists(fbackup) and __load_rts(fbackup):
        global loaded_from_backup
        loaded_from_backup = True
        return
    create_rts()
