# -*- encoding:utf-8 -*-
"""
date: 2020/8/23
author: Berserker
"""

from abc import ABC
from abc import abstractmethod
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum


class Factor(ABC):

    def __init__(self):
        self.conditions = {}
        self.parameters = None
        pass

    def add_condition(self, key, value):
        if key is None or value is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "Parameter is invalid !")
        if key in self.conditions.keys():
            raise XException(ErrorCodeEnum.CODE_EXIST, "Key already existed !")
        self.conditions[key] = value

    def remove_condition(self, key):
        if key not in self.conditions.keys():
            return
        self.conditions.pop(key)

    def condition_prepare(self, key, *args, **kwargs):
        if key not in self.conditions.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "key is invalid !")
        self.conditions[key].prepare(*args, **kwargs)

    def condition_judge(self, key, *args, **kwargs):
        if key not in self.conditions.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "key is invalid !")
        return self.conditions[key].judge(*args, **kwargs)

    def condition_get_ret_data(self, key):
        if key not in self.conditions.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "key is invalid !")
        return self.conditions[key].get_ret_data()

    @abstractmethod
    def _prepare(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def estimate(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

