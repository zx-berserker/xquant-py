# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""

from abc import ABC, abstractmethod
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from threading import Thread


class XThreadBase(ABC):

    @abstractmethod
    def thread_main(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def join(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def start(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")


class XThread(XThreadBase):

    def __init__(self):
        self._thread = Thread(target=self.thread_main)

    def join(self, timeout=None):
        self._thread.join(timeout)

    def start(self):
        try:
            self._thread.start()
        except Exception as e:
            raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR, str(e))
