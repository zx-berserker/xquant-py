# -*- encoding:utf-8 -*-
"""
date: 2020/11/2
author: Berserker
"""

from abc import ABC, abstractmethod
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum
from multiprocessing import Process


class XProcessBase(ABC):

    @staticmethod
    def process_main(self_obj):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def join(self, timeout=None):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def start(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def terminate(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def get_exit_code(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def get_ident(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def is_alive(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")


class XProcess(XProcessBase):

    def __init__(self):
        self._process = Process(target=self.process_main, args=(self,))

    def join(self, timeout=None):
        self._process.join(timeout)

    def start(self):
        self._process.start()

    def terminate(self):
        self._process.terminate()

    def get_exit_code(self):
        return self._process.exitcode

    def get_ident(self):
        return self._process.ident

    def is_alive(self):
        return self._process.is_alive()



