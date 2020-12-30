from datetime import datetime
from queue import Queue
from typing import Optional

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, CallbackContext

from pytelelogger.levels import TeleLoggerLevel
from pytelelogger.types import PathType
from pytelelogger.threaded import threaded


class TeleLogger:
    def __init__(self, token: str, user_name: str, file: Optional[PathType] = None,
                 level: int = TeleLoggerLevel.WARNING.value, *args, **kwargs) -> None:
        self.__updater = Updater(token, *args, **kwargs)
        self.__level = level

        # get and configure dispatcher
        self.__dp = self.__updater.dispatcher
        self.__dp.add_handler(CommandHandler('start', self.__start))

        self.__user_name = user_name
        self.__chat_id = None
        self.__fstream = None if file is None else open(file, 'w', encoding='utf-8')
        self.__log_queue = Queue()

        self.__updater.start_polling()

    def __del__(self):
        try:
            self.__fstream.close()
        except AttributeError:
            pass

    def __start(self, update: Update, context: CallbackContext):
        if self.__user_name == update.effective_chat.username:
            self.__chat_id = update.effective_chat.id

            context.bot.send_message(chat_id=self.__chat_id, text='I\'m ready!')

            self.__resend_logs()

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level):
        if not TeleLoggerLevel.has_value(level):
            raise ValueError('Unknown logging level')

        self.__level = level

    @staticmethod
    def __create_log(level: str, message: str) -> str:
        return f'{level}\n{datetime.now().strftime("%d:%b:%Y %H:%M:%S")}\n{message}\n'

    def __send_log(self, level: str, message: str):
        log = self.__create_log(level, message)

        try:
            self.__updater.bot.send_message(chat_id=self.__chat_id, text=log)
        except BadRequest:
            print('put log in queue')
            self.__log_queue.put(log)

        if self.__fstream is not None:
            self.__fstream.write(log)

    def debug(self, message: str) -> None:
        self.__send_log(TeleLoggerLevel.DEBUG.name, message)

    def info(self, message: str) -> None:
        self.__send_log(TeleLoggerLevel.INFO.name, message)

    def warning(self, message: str) -> None:
        self.__send_log(TeleLoggerLevel.WARNING.name, message)

    def error(self, message: str) -> None:
        self.__send_log(TeleLoggerLevel.ERROR.name, message)

    def critical(self, message: str) -> None:
        self.__send_log(TeleLoggerLevel.CRITICAL.name, message)

    @threaded
    def __resend_logs(self):
        while True:
            while not self.__log_queue.empty():
                log = 'I\'ve got a missed log for you!\n\n' + self.__log_queue.get()
                is_send = False

                while not is_send:
                    try:
                        self.__updater.bot.send_message(chat_id=self.__chat_id, text=log)
                        is_send = True
                    except BadRequest:
                        pass
