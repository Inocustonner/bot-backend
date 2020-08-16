import chromalog, chromalog.colorizer
from colorama import (
    Fore,
    Back,
    Style,
)
import logging
import json
import traceback

LOGGER_NAME_WS = 'bot-backend-ws'
LOGGER_NAME = 'bot-backend'

level_map = {
    'debug': '##',
    'info': '--',
    'warning': '-!',
    'error': '-*',
    'critical': '*!'
}

class BotBackendColorizer(chromalog.colorizer.GenericColorizer):
    """
    Colorize log entries.
    """
    default_color_map = {
        level_map['debug']: (Style.DIM + Fore.CYAN, Style.RESET_ALL),
        level_map['info']: (Style.BRIGHT, Style.RESET_ALL),
        'important': (Style.BRIGHT, Style.RESET_ALL),
        'success': (Fore.GREEN, Style.RESET_ALL),
        level_map['warning']: (Fore.YELLOW, Style.RESET_ALL),
        level_map['error']: (Fore.RED, Style.RESET_ALL),
        level_map['critical']: (Fore.BLACK + Back.RED + Style.DIM, Style.RESET_ALL),
    }

def create_logger(name: str='bot-backend', level: int=logging.DEBUG):
    chromalog.basicConfig(format='%(levelname)s %(message)s', level=level, colorizer=BotBackendColorizer())
    log = logging.getLogger(name)
    log.setLevel(level)
    # file handler
    # fh = logging.FileHandler(f'{name}.log')
    # fh.setLevel(level)

    # console handler
    ch = chromalog.ColorizingStreamHandler()
    ch.setLevel(level)
    # formatter
    logging.addLevelName(logging.DEBUG, level_map['debug'])
    logging.addLevelName(logging.INFO, level_map['info'])
    logging.addLevelName(logging.WARNING, level_map['warning'])
    logging.addLevelName(logging.ERROR, level_map['error'])
    logging.addLevelName(logging.CRITICAL, level_map['critical'])
    # console_formatter = chromalog.ColorizingFormatter('%(levelname)s %(message)s')
    # ch.setFormatter(console_formatter)
    # log.addHandler(ch)

def f_last_error(level: int = -1):
    if level == -1:
        s = ' ' * 3
    else:
        s = logging.getLevelName(level) + ' '
    ex = traceback.format_exc().splitlines(True)
    return s + s.join(ex)[:-1]

def json_error(code: int, reason: str) -> str:
    return json.dumps({"error": {"code": code, "reason": reason}})