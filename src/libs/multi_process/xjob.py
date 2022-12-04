# -*- encoding:utf-8 -*-
"""
date: 2020/11/2
author: Berserker
"""
from abc import ABC, abstractmethod
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum
from src.tool.object_dict import Dict


class XJob(ABC):
    name = 'XJob'

    @abstractmethod
    def do(self):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @staticmethod
    def done_callback(*args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")


class XJobFactory(ABC):
    name = 'XJobFactory'

    def __init__(self, job_cls):
        self.job_cls = job_cls

    @abstractmethod
    def get_job(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    def env_prepare(self):
        pass

    def env_release(self):
        pass


class XJobManager(object):

    def __init__(self):
        self.factory_dict = {}
        self.done_callback_dict = {}

    def register_factory(self, job_factory_obj):
        if job_factory_obj.name in self.factory_dict.keys():
            raise XException(ErrorCodeEnum.CODE_EXIST, "job_factory already exist !")
        self.factory_dict[job_factory_obj.name] = job_factory_obj

    def get_job(self, param_dict):
        if XProcessPoolParam.key_tuple[0] not in param_dict.keys():
            return None
        if XProcessPoolParam.key_tuple[1] not in param_dict.keys():
            return None
        factory_name = param_dict[XProcessPoolParam.key_tuple[0]]
        if factory_name not in self.factory_dict.keys():
            return None
        factory = self.factory_dict[factory_name]
        param = param_dict[XProcessPoolParam.key_tuple[1]]
        if isinstance(param, dict):
            job_param = Dict(param)
        else:
            job_param = param
        return factory.get_job(job_param)

    def register_done_callback(self, job_cls):
        if job_cls.name in self.done_callback_dict.keys():
            raise XException(ErrorCodeEnum.CODE_EXIST, "job_done_callback already exist !")
        self.done_callback_dict[job_cls.name] = job_cls.done_callback

    def get_done_callback(self, job):
        if job.name not in self.done_callback_dict.keys():
            return None
        return self.done_callback_dict[job.name]

    def env_prepare(self):
        for factory in self.factory_dict.values():
            factory.env_prepare()

    def env_release(self):
        for factory in self.factory_dict.values():
            factory.env_release()


class XProcessPoolParam(object):
    key_tuple = ('factory_name', 'param')

    def __init__(self, factory_name, param_obj):
        self.factory_name = factory_name
        if hasattr(param_obj, '__dict__'):
            self.param = param_obj.__dict__
        else:
            self.param = param_obj

