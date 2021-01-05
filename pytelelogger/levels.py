from enum import Enum, unique


@unique
class TeleLoggerLevel(Enum):
    """
    Logging levels for TeleLogger.
    """

    DEBUG = 0
    INFO = 1
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    @staticmethod
    def has_value(value: int) -> bool:
        """
        Check if provided int is valid logging level. For example, 10 is invalid level, but 3 is valid.
        
        :param value: value to be checked
        
        :return: True if value is valid logging level, False otherwise.
        """

        return value in [v.value for v in TeleLoggerLevel.__members__.values()]
