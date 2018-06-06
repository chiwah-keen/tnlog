# -*- coding: utf-8 -*-
"""
该日志类可以把不同级别的日志输出到不同的日志文件中
"""

import ujson
import json
import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler

from mtp.util.common.datetool import curr_now_msec
from mtp.util.json_helper.json_encoder import JSONEncoder
from mtp.util.module import *


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
            'debug': os.path.join(logpath, 'debug/' + logname + '.debug.log'),
            'info': os.path.join(logpath, 'info/' + logname + '.info.log'),
            'warn': os.path.join(logpath, 'warn/' + logname + '.warn.log'),
            'error': os.path.join(logpath, 'error/' + logname + '.error.log'),
            'customer': os.path.join(logpath, 'customer/' + logname + '.customer.log'),
            'admin': os.path.join(logpath, 'admin/' + logname + '.admin.log')
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

    def out(self, _self=None, d={}, type="info"):

        if type in ["warn", "record", "admin"]:
            getattr(self, type)(_self, d)

        elif type in ["info", "debug", "error"]:
            getattr(self, type)(str(d))

        else:
            self.info(str(d))

    def info(self, message):
        message=JSONEncoder().encode(message)
        message = self.get_log_message("info", message)
        self.__loggers['info'].info(message, exc_info=0)

    def error(self, message):
        message = self.get_log_message("error", message)
        self.__loggers['error'].error(message, exc_info=1)

    def warning(self, _self, dict={}):
        self.__loggers['warn'].warning(self.info_header(_self, dict))

    def debug(self, message):
        message = self.get_log_message("debug", message)
        self.__loggers['debug'].debug(message, exc_info=0)

    def info_header(self, _self, d={}):
        """
        info日志输出
        :param _self: 应用的self句柄
        :param d: 需要打出的用户日志
        :return:
        """

        # 用户所有输入的密码，不要在日志中出现
        req_params = _self.request.arguments
        if req_params and req_params.get("password", 0) != 0:
            req_params["password"] = "xxxxxx"
        if req_params and req_params.get("_password", 0) != 0:
            req_params["_password"] = "xxxxxx"
        if req_params and req_params.get("_repassword", 0) != 0:
            req_params["_repassword"] = "xxxxxx"

        # 用户头像记录用户id，头像数据不写入LOG
        if req_params and req_params.get("imgData", 0) != 0:
            req_params["imgData"] = str(_self.current_user.get('sysuser', mdict()).get('id', ''))

        x_real_ip = _self.request.headers.get("X-Real-IP")

        log_info_common = {
            "wechat_type": str(_self.current_user.wechat.get('type', '0')),
            "wechat_id": str(_self.current_user.wechat.get('id', '')),
            "requester_id": {
                "dquser_id": str(_self.current_user.get('sysuser', mdict()).get('id', '')),
                "openid": _self.current_user.wxuser.get('openid', ''),
                "viewer_id": _self.current_user.get('viewer', mdict()).get('idcode', ''),
            },
            "useragent": _self.request.headers.get('User-Agent'),
            "referer":_self.request.headers.get("Referer"),
            "remote_ip": x_real_ip or _self.request.remote_ip,
            "req_type": _self.request.method,
            "req_uri": _self.request.uri,
            "req_params": req_params,
            "session_id": _self.get_secure_cookie("session_id"),
            "sys_user_cookie": _self.get_secure_cookie(const.SYS_USER_ID)
        }
        try:
            d.update(log_info_common)
        except Exception as e:
            d = log_info_common

        d.update({"status_code": str(_self._status_code)})

        return JSONEncoder().encode(d)

    def record(self, _self=None, dict={}):
        """
        记录customer的log信息
        :param _self: 应用的self句柄
        :param dict: 需要打印的用户日志
        :return:
        """
        if _self:
            self.__loggers['customer'].info(
                json.dumps(self.info_header(_self, dict), ensure_ascii=False),
                exc_info=0)
        else:
            self.__loggers['customer'].info(
                json.dumps(dict, cls=JSONEncoder, ensure_ascii=False),
                exc_info=0)

    # 记录admin的log信息
    def admin(self, _self, dict):

        if not _self.current_user:
            _self.current_user = mdict(_self.current_user)

        x_real_ip = _self.request.headers.get("X-Real-IP")

        log_info_common = {
            "company_id": str(_self.current_user.account.company_id) or '-1',
            "requester_id": {
                "account_id": str(_self.current_user.account.id) or '-1'
            },
            "useragent": _self.request.headers['User-Agent'],
            "referer": _self.request.headers.get("Referer"),
            "remote_ip": x_real_ip or _self.request.remote_ip,
            "req_type": _self.request.method,
            "req_uri": _self.request.uri,
            "req_params": _self.request.arguments
        }
        try:
            dict.update(log_info_common)
        except Exception as e:
            dict = log_info_common

        dict.update({"status_code": str(_self._status_code)})

        self.__loggers['admin'].info(str(dict))

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

    def out(self, _self=None, d={}, type="info"):
        if type in ["warning", "record", "admin"]:
            getattr(self, type)(_self, d)
        elif type in ["info", "debug", "critical", "error"]:
            getattr(self, type)(str(d))
        else:
            self.info(str(d))


LOG = TNLog()
