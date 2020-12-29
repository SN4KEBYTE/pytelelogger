from enum import Enum


class TeleLoggerLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    @staticmethod
    def has_value(item):
        return item in [v.value for v in TeleLoggerLevel.__members__.values()]
