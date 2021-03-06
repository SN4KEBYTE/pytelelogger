from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Optional, TextIO, Dict

import yaml
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher

from pytelelogger.defaults import TeleLoggerDefaults
from pytelelogger.levels import TeleLoggerLevel
from pytelelogger._threaded import threaded
from pytelelogger._types import PathType


class TeleLogger:
    def __init__(self, cfg_path: PathType, *args, **kwargs) -> None:
        """
        Initialize the class with some values.

        :param cfg_path: path to TeleLogger configuration file (.yaml or .yml).
        :param args: variable length additional argument list for Updater object.
        :param kwargs: arbitrary additional keyword arguments for Updater object.

        :return: None.
        """

        self.__cfg_path: PathType = cfg_path

        with open(self.__cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)

        self.__updater: Updater = Updater(cfg['token'], *args, **kwargs)
        self.__dp: Dispatcher = self.__updater.dispatcher
        self.__dp.add_handler(CommandHandler('start', self.__start))

        self.__username: str = cfg['username']
        self.__project: str = cfg['project'].replace(' ', '')
        self.__level: int = cfg.get('level', TeleLoggerDefaults.level)

        self.__mode: str = cfg.get('mode', TeleLoggerDefaults.mode)
        self.__paths: Dict[str, PathType] = cfg.get('paths', TeleLoggerDefaults.paths)
        self.__fstream: Dict[str, TextIO] = {k: open(v, 'w', encoding='utf-8') for k, v in self.__paths.items()}

        self.__greeting: str = cfg.get('greeting', TeleLoggerDefaults.greeting)
        self.__dtf: str = cfg.get('dtf', TeleLoggerDefaults.dtf)
        self.__emojis: Dict[str, str] = cfg.get('emojis', TeleLoggerDefaults.emojis)

        self.__chat_id: Optional[int] = cfg.get('chat_id')
        self.__log_queue: Queue = Queue()

        self.__updater.start_polling()

    def __del__(self) -> None:
        """
        Destructor for TeleLogger object. It stops the polling and closes all file streams.

        :return: None.
        """

        self.stop(True)

    def __start(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /start command. It uses provided Telegram username to get needed chat_id.

        :param update: object representing an incoming update.
        :param context: context object passed to the callback called by dispatcher.

        :return: None.
        """

        if self.__username == update.effective_chat.username:
            if self.__chat_id is None:
                self.__chat_id = update.effective_chat.id

                with open(self.__cfg_path, 'a') as f:
                    f.write(f'\n\nchat_id: {self.__chat_id}')

            context.bot.send_message(chat_id=self.__chat_id, text=self.__greeting)

    def stop(self, force=False):
        self.__updater.stop()

        if not force:
            try:
                self.__handler.join()
            except AttributeError:
                pass

        for k in self.__fstream:
            try:
                self.__fstream[k].close()
            except AttributeError:
                pass

    @property
    def level(self) -> int:
        """
        Get current logging level.
        
        :return: current logging level.
        """

        return self.__level

    @level.setter
    def level(self, level: int) -> None:
        """
        Set logging level.
        
        :param level: new logging level.
        
        :return: None.
        
        :raises: ValueError if provided level is < 0 or > 5.
        """

        if not TeleLoggerLevel.has_value(level):
            raise ValueError('Unknown logging level')

        self.__level = level

    def __create_tg_log(self, level: str, message: str) -> str:
        """
        Creates formatted log string for Telegram.

        :param level: logging level.
        :param message: message to be used in log.

        :return: formatted log.
        """

        return f'{self.__project}\n\n{self.__emojis[level]}{level.upper()}\n{datetime.now().strftime(self.__dtf)}\n\n' \
               f'{message}\n\n{self.__generate_hashtags(level)}'

    def __create_file_log(self, level: str, message: str) -> str:
        """
        Creates formatted log string for writing to file.

        :param level: logging level.
        :param message: message to be used in log.

        :return: formatted log.
        """

        return f'[{level.upper()}:{datetime.now().strftime(self.__dtf)}] {message}'

    def __record_log(self, level: str, message: str) -> None:
        """
        Send message with log and write log to file.

        :param level: logging level.
        :param message: message to be used in log.

        :return: None.
        """

        lvl: str = level.lower()
        log: str = self.__create_file_log(lvl, message)

        try:
            self.__fstream[lvl if self.__mode == 'multi' else 'debug'].write(log)
        except KeyError:
            pass

        if TeleLoggerLevel.__members__[level].value >= self.__level:
            tg_log: str = self.__create_tg_log(lvl, message)

            try:
                self.__updater.bot.send_message(chat_id=self.__chat_id, text=tg_log)
            except BadRequest:
                self.__log_queue.put(tg_log)
                self.__handler: Thread = self.__resend_logs()

    def debug(self, message: str) -> None:
        """
        Record debug log.
        
        :param message: message to be used in log.
        
        :return: None. 
        """

        self.__record_log(TeleLoggerLevel.DEBUG.name, message)

    def info(self, message: str) -> None:
        """
        Record info log.
        
        :param message: message to be used in log.
        
        :return: None.
        """

        self.__record_log(TeleLoggerLevel.INFO.name, message)

    def warning(self, message: str) -> None:
        """
        Record warning log.
        
        :param message: message to be used in log.
        
        :return: None.
        """

        self.__record_log(TeleLoggerLevel.WARNING.name, message)

    def error(self, message: str) -> None:
        """
        Record error log.
        
        :param message: message to be used in log.
        
        :return: None.
        """

        self.__record_log(TeleLoggerLevel.ERROR.name, message)

    def critical(self, message: str) -> None:
        """
        Record critical log.
        
        :param message: message to be used in log.
        
        :return: None.
        """

        self.__record_log(TeleLoggerLevel.CRITICAL.name, message)

    def __generate_hashtags(self, level: str) -> str:
        """
        Generate some hashtags to make search in Telegram dialog easier.
        
        :param level: logging level.
        
        :return: list of 3 hashtags: #project, #project_level, #level
        """

        return '\n'.join(['#' + h for h in [self.__project, self.__project + '_' + level, level]])

    @threaded(daemon=True)
    def __resend_logs(self) -> Thread:
        """
        This method tries to resend all logs whose sending was messed up. Runs in separate thread.
        
        :return: None. 
        """

        while not self.__log_queue.empty():
            log: str = self.__log_queue.get()
            is_send: bool = False

            while not is_send:
                try:
                    self.__updater.bot.send_message(chat_id=self.__chat_id, text=log)
                    is_send = True
                except BadRequest:
                    pass
