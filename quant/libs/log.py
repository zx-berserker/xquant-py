# -*- coding:utf-8 -*-
"""
date: 2026/01/17
author: Berserker
"""
import logging
from logging.handlers import TimedRotatingFileHandler
from queue import Queue, Empty
from config.settings import GlobeConfig
import os
import threading

class XLog:
    if GlobeConfig.is_log_file:
        logger = logging.getLogger(GlobeConfig.logger_name)
        logger.setLevel(logging.INFO)
        _file_handler = TimedRotatingFileHandler(os.path.join(GlobeConfig.log_file_path, GlobeConfig.log_file_name), when="midnight", backupCount=7)
        _file_handler.suffix = "%Y-%m-%d.log"
        _file_handler.encoding = "utf-8"
        _file_handler.setLevel(logging.INFO)
        _formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        _file_handler.setFormatter(_formatter)
        logger.addHandler(_file_handler)
    if GlobeConfig.is_fastapi_server:
        _fastapi_queue = Queue(20)
        _fastapi_queue_mutex = threading.Lock()

    @classmethod
    def print(cls, *objects):
        message = f'[{GlobeConfig.logger_name}]:'
        for obj in objects:
            message += '%s' % (obj)
        print(message)

    @classmethod
    def log(cls, *objects):
        message = f'[{GlobeConfig.logger_name}]:'
        for obj in objects:
            message += '%s' % (obj)
        if GlobeConfig.is_log_file:
            cls.logger.info(message)
            cls._file_handler.flush()

    @classmethod
    def info(cls, *objects):
        message = f'[{GlobeConfig.logger_name}]<INFO>:'
        for obj in objects:
            message += '%s' % (obj)
        if GlobeConfig.is_log_file:
            cls.logger.info(message)
            cls._file_handler.flush()
        if GlobeConfig.is_print:
            print(message)
        if GlobeConfig.is_fastapi_server:
            with cls._fastapi_queue_mutex:
                if cls._fastapi_queue.full():
                    cls._fastapi_queue.get_nowait()
                cls._fastapi_queue.put_nowait('%s' % message)

    @classmethod
    def error(cls, *objects):
        message = f'[{GlobeConfig.logger_name}]<ERROR>:'
        for obj in objects:
            message += '%s' % (obj)        
        if GlobeConfig.is_log_file:
            cls.logger.error(message)
            cls._file_handler.flush()
        if GlobeConfig.is_print:
            print(message)
        if GlobeConfig.is_fastapi_server:
            with cls._fastapi_queue_mutex:
                if cls._fastapi_queue.full():
                    cls._fastapi_queue.get_nowait()
                cls._fastapi_queue.put_nowait('%s' % message)

    @classmethod
    def fastapi_get(cls,timeout=3):
        if GlobeConfig.is_fastapi_server:
            try:
                data = cls._fastapi_queue.get(timeout=timeout)
            except:
                return None
            return data
        return None