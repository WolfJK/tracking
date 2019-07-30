# coding: utf-8
# __author__: "James"
from __future__ import unicode_literals

import logging
from website.settings import *
import os


class Logger:
    _logger = None

    def __init__(self, LOGGER_PATH, ERROR_LOGGER_PATH, systemname, tag):
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        self.systemname = systemname
        self.tag = tag

        # set log format
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        # define normal logger
        self.logger = logging.getLogger(LOGGER_PATH)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(LOGGER_PATH)
        fh.setFormatter(fmt)
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)

        # define error logger
        self.error_logger = logging.getLogger(ERROR_LOGGER_PATH)
        self.error_logger.setLevel(logging.ERROR)
        fh = logging.FileHandler(ERROR_LOGGER_PATH)
        fh.setFormatter(fmt)
        fh.setLevel(logging.ERROR)
        self.error_logger.addHandler(fh)

        if DEBUG:
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            self.error_logger.addHandler(sh)

    def _message_wrap(self, message):
        return "[%s] [%s] %s" % (self.systemname, self.tag, message)

    def debug(self, message):
        if DEBUG:
            print self._message_wrap(message).encode('utf-8')
            self.logger.debug(self._message_wrap(message))

    def info(self, message):
        self.logger.info(self._message_wrap(message))

    def warning(self, message):
        self.logger.warning(self._message_wrap(message))

    def error(self, message):
        self.error_logger.error(self._message_wrap(message))

    def critical(self, message):
        self.error_logger.critical(self._message_wrap(message))

    @classmethod
    def getLoggerInstance(cls):
        if cls._logger == None:
            cls._logger = Logger(LOGGER_PATH, ERROR_LOGGER_PATH, LOGGER_SYSTEM_NAME, LOGGER_TAG)
        return cls._logger




