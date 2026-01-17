# -*- coding:utf-8 -*-
"""
date: 2026/01/17
author: Berserker
"""
import logging
from logging.handlers import TimedRotatingFileHandler
from config.secure import LOG_FILE_PATH
from queue import Queue, Empty
from config.settings import GlobeConfig
import os
import threading

class XLog:
    logger = logging.getLogger("xquant_logger")
    _file_handler = TimedRotatingFileHandler(os.path.join(LOG_FILE_PATH, "xquant.log"), when="midnight", backupCount=7)
    _file_handler.suffix = "%Y-%m-%d.log"
    _file_handler.encoding = "utf-8"
    _file_handler.setLevel(logging.INFO)
    _formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    _file_handler.setFormatter(_formatter)
    logger.addHandler(_file_handler)
    _fastapi_queue = Queue(20)
    _fastapi_queue_mutex = threading.Lock()

    @classmethod
    def info(cls, message):
        if GlobeConfig.is_log_file:
            cls.logger.info(message)
        else:
            print(message)
        if GlobeConfig.is_fastapi_server:
            with cls._fastapi_queue_mutex:
                if cls._fastapi_queue.full():
                    cls._fastapi_queue.get_nowait()
                cls._fastapi_queue.put_nowait(message)

    @classmethod
    def error(cls, message):
        if GlobeConfig.is_log_file:
            cls.logger.error(message)
        else:
            print(message)
        if GlobeConfig.is_fastapi_server:
            with cls._fastapi_queue_mutex:
                if cls._fastapi_queue.full():
                    cls._fastapi_queue.get_nowait()
                cls._fastapi_queue.put_nowait(message)

    @classmethod
    def fastapi_get(cls,timeout=3):
        return cls._fastapi_queue.get(timeout=timeout)