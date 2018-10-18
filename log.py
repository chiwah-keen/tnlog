# -*- coding: utf-8 -*-
"""
该日志类可以把不同级别的日志输出到不同的日志文件中
"""

import os, time, sys
import json
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

def curr_now_msec(fmt="%Y-%m-%d %H:%M:%S"):
    return time.strftime(fmt, time.localtime(float(time.time())))

class JSONEncoder(json.JSONEncoder):
    """
    指定非内置 JSON serializable 的类型应该如何转换
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class TNLog(object):

    LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}

    def init(self, logname='dq',
                        logpath='/tmp/',
                        log_level='INFO',
                        log_format='%(asctime)s\t%(filename)s:%(lineno)s\t%(levelname)s\t%(message)s',
                        log_backcount=0,
                        log_filesize=10*1024*1024
    ):

        self.__loggers = {}
        self.logname = logname
        self.log_format = log_format
        self.log_backcount = log_backcount
        self.log_filesize = log_filesize

        self.logPath = {
            'debug': os.path.join(logpath, logname + '.debug.log'),
            'info': os.path.join(logpath, logname + '.info.log'),
            'warn': os.path.join(logpath, logname + '.warn.log'),
            'error': os.path.join(logpath, logname + '.error.log'),
            #'customer': os.path.join(logpath, 'customer/' + logname + '.customer.log'),
            #'admin': os.path.join(logpath, 'admin/' + logname + '.admin.log')
        }

        log_levels = self.logPath.keys()

        self.create_handlers()

        for level in log_levels:
            logger = logging.getLogger(self.logname+'.'+level)
            logger.addHandler(self.handlers[level])
            logger.setLevel(self.LOG_LEVELS[log_level])
            self.__loggers.update({level: logger})

    def get_log_message(self, level, message):
        # frame,filename,lineNo,functionName,code,unknowField = inspect.stack()[2]
        """日志格式：[时间] [类型] [记录代码] 信息"""
        return self.log_format % dict(asctime=curr_now_msec(),
                                      levelname=level.upper(),
                                      filename=sys._getframe().f_back.f_back.f_code.co_filename,
                                      lineno=sys._getframe().f_back.f_back.f_lineno,
                                      message=message
        )

    def create_handlers(self):

        self.handlers = {}

        logLevels = self.logPath.keys()

        for level in logLevels:
            path = os.path.abspath(self.logPath[level])

            # 日志存储路径，不存在，就创建该路径
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            if level == 'customer' or level == 'admin':
                self.handlers[level] = TimedRotatingFileHandler(path, 'H', 1, backupCount=self.log_backcount)
            else:
                self.handlers[level] = RotatingFileHandler(path, maxBytes=self.log_filesize, backupCount=self.log_backcount)

            formatter = logging.Formatter(self.log_format)

            self.handlers[level].setFormatter(formatter)
            self.handlers[level].suffix = "%Y%m%d%H.log"

    def info(self, message):
        self.__loggers['info'].info(message, exc_info=0)

    def error(self, message):

        self.__loggers['error'].error(message, exc_info=0)

    def warning(self, message):
        self.__loggers['warn'].warning(message)

    def debug(self, message):
        self.__loggers['debug'].debug(message, exc_info=0)


    def createHandlers(self):
        self.handlers = {}
        logLevels = self.logPath.keys()
        for level in logLevels:
            path = os.path.abspath(self.logPath[level])
            # not exists , create dir
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if level == 'customer' or level == 'admin':
                self.handlers[level] = TimedRotatingFileHandler(path, 'M', 1, backupCount=self.log_backcount)
            else:
                self.handlers[level] = RotatingFileHandler(path, maxBytes=self.log_filesize, backupCount=self.log_backcount)
            formatter = logging.Formatter(self.log_format)
            self.handlers[level].setFormatter(formatter)
            self.handlers[level].suffix = "%Y%m%d%H%M%S.log"


LOG = TNLog()

if __name__ == "__main__":
    log = LOG
    log.init(logname="test", logpath="./", log_level="DEBUG")
    log.info({"123": "123"})
    log.info(123)
    log.debug(123)
    log.warning(123)
    log.error(123)
