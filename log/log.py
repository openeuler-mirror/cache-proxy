import os
import time
import logging
from logging import handlers

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

log_level = DEBUG

if os.getenv('CI_BUILD_DEBUG') != 'True':
    log_level = INFO


class Logger(object):
    def __init__(self, name, clevel=log_level,
                 log_file_path=None, Flevel=log_level):
        fmt = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")

        ch = logging.StreamHandler()
        ch.setLevel(clevel)
        ch.setFormatter(fmt)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(ch)
        if log_file_path:
            time_file_handler = handlers.TimedRotatingFileHandler(filename=log_file_path, when='D')
            time_file_handler.setLevel(logging.DEBUG)
            time_file_handler.setFormatter(fmt)
            self.logger.addHandler(time_file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = Logger("build", log_file_path="source_check_{0}.log".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
# Unified log format，change WARNING to WARN
logging.addLevelName(WARN, 'WARN')
