from typing import List, Dict

from pytelelogger.levels import TeleLoggerLevel
from pytelelogger.types import PathType


class TeleLoggerDefaults:
    level: int = TeleLoggerLevel.WARNING.value

    mode: str = 'multi'

    paths: Dict[str, PathType] = {
        'debug': 'debug.txt',
        'info': 'info.txt',
        'warning': 'warning.txt',
        'error': 'error.txt',
        'critical': 'critical.txt',
    }

    greeting: str = 'I\'m ready!'
    missed: str = 'I\'ve got a missed log for you!'

    dtf: str = '%d/%b/%Y %H:%M:%S'

    emojis: Dict[str, str] = {
        'debug': '⚙',
        'info': 'ℹ',
        'warning': '⚠',
        'error': '❌',
        'critical': '🔴',
    }
