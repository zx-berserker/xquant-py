# -*- encoding:utf-8 -*-
"""
date: 2020/11/2
author: Berserker
"""
from src.libs.multi_process.xjob import XJob, XJobFactory


class UpdateJob(XJob):
    name = 'UpdateJob'

    def __init__(self, param, spider_task_factory, update_task_factory):
        self.spider_task_factory = spider_task_factory
        self.update_task_factory = update_task_factory
        self.param = param

    def __repr__(self):
        return "<UpdateJob id:%d param:%s>" % (id(self), self.param)

    def do(self):
        spider_task = self.spider_task_factory.get_task(self.param)
        spider_task.executive()
        data = spider_task.result()
        if data:
            update_task = self.update_task_factory.get_task(data)
            update_task.executive()


class UpdateJobFactory(XJobFactory):
    name = 'UpdateJobFactory'

    def __init__(self, update_task_factory, spider_task_factory):
        self.update_task_factory = update_task_factory
        self.spider_task_factory = spider_task_factory
        super(UpdateJobFactory, self).__init__(UpdateJob)

    def get_job(self, param):
        if param:
            return self.job_cls(param, self.spider_task_factory, self.update_task_factory)
        return None

    def env_prepare(self):
        self.update_task_factory.env_prepare()
        self.spider_task_factory.env_prepare()

    def env_release(self):
        self.update_task_factory.env_release()
        self.spider_task_factory.env_release()