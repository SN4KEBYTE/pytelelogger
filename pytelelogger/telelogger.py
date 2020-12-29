from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from pytelelogger.types import PathType
from pytelelogger.levels import TeleLoggerLevel


class TeleLogger:
    def __init__(self, token: str, user_name: str, file: Optional[PathType] = None,
                 level: int = TeleLoggerLevel.WARNING.value, *args, **kwargs) -> None:
        self.__updater = Updater(token, *args, **kwargs)
        self.level = level

        # get and configure dispatcher
        self.__dp = self.__updater.dispatcher
        self.__dp.add_handler(CommandHandler('start', self.__start))

        self.__user_name = user_name
        self.__chat_id = None
        self.__fstream = None if file is None else open(file, 'w', encoding='utf-8')

        self.__updater.start_polling()

    def __del__(self):
        try:
            self.__fstream.close()
        except AttributeError:
            pass

    def __start(self, update: Update, context: CallbackContext):
        if self.__user_name == update.effective_chat.username:
            self.__chat_id = update.effective_chat.id

            context.bot.send_message(chat_id=self.__chat_id, text='Welcome, master.')

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level):
        if not TeleLoggerLevel.has_value(level):
            raise ValueError('Unknown logging level')

        self.__level = level

    def __create_log(self, level: str, message: str) -> str:
        log = f'{level.upper()} {datetime.now().strftime("%d:%b:%Y %H:%M:%S")}\n{message}\n'

        if self.__fstream is not None:
            self.__fstream.write(log)

        return log

    def debug(self, message: str) -> None:
        log = self.__create_log('debug', message)

        self.__updater.bot.send_message(chat_id=self.__chat_id, text=log)

    def info(self, message: str) -> None:
        log = self.__create_log('info', message)

    def warning(self, message: str) -> None:
        log = self.__create_log('warning', message)

    def error(self, message: str) -> None:
        log = self.__create_log('error', message)

    def critical(self, message: str) -> None:
        log = self.__create_log('critical', message)
