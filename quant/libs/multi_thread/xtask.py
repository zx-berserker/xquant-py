# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""

from abc import ABC, abstractmethod
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from threading import Event, RLock
from quant.tool.function_tool import get_fn_arg_count
from time import sleep


class XTaskBase(ABC):

    @abstractmethod
    def executive(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def result(self, timeout=None):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def done(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def exception(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def add_done_callback(self, fn):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def cancel(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def running(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")


class XTaskFactory(ABC):

    def __init__(self, task_cls):
        self.task_cls = task_cls
        self._is_exit = False

    @abstractmethod
    def get_task(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    def env_prepare(self):
        pass

    def env_release(self):
        pass


class XTask(XTaskBase):

    def __init__(self):
        self._result = None
        self._is_done = False
        self._exception = None
        self._is_running = False
        self._done_callback = None
        self._exe_event = Event()
        self._exe_lock = RLock()

    @abstractmethod
    def task_main(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    def executive(self):
        if self._is_done:
            return
        self._exe_lock.acquire()
        self._is_running = True
        try:
            self._result = self.task_main()
            self._exe_event.set()
        except XException as e:
            self._exception = e
            return
        except Exception as e:
            raise e
        else:
            if self._done_callback:
                num = get_fn_arg_count(self._done_callback)
                if num:
                    self._done_callback(self)
                else:
                    self._done_callback()
        finally:
            self._is_running = False
            self._is_done = True
            self._exe_lock.release()

    def result(self, timeout=None):
        ret = self._exe_event.wait(timeout=timeout)
        if ret:
            return self._result
        else:
            return None

    def done(self):
        return self._is_done

    def exception(self):
        return self._exception

    def add_done_callback(self, fn):
        if not self._is_running:
            with self._exe_lock:
                self._done_callback = fn

    def running(self):
        return self._is_running

    def cancel(self):
        if not self._is_running:
            with self._exe_lock:
                self._is_done = True

