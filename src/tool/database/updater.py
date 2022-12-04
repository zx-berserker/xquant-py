# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""

from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum
from src.spider.baostock.query_stock_info import QueryStockInfo
from src.models.k_data_daily import KDataDaily
from src.models.k_data_monthly import KDataMonthly
from src.models.k_data_weekly import KDataWeekly
from src.tool.database.base import SQLAlchemy
from src.models.shareholder import Shareholder, FloatShareholder
from src.spider.spider_task_factory import ShareholderSpiderTaskFactory, ShareholderInfo
from src.libs.multi_thread.xthread import XThread
from src.libs.multi_thread.xthread_pool import XThreadPool
from src.tool.database.update_job import UpdateJobFactory
from src.libs.multi_process.xprocess_pool import XProcessPool
from src.libs.multi_process.xjob import XJobManager, XProcessPoolParam
from time import sleep


class Updater(XThread):
    update_thread_pool_capacity = 5
    spider_thread_pool_capacity = 1
    interval_sleep = 3

    def __init__(self, param_list, update_task_factory, spider_task_factory):
        super(Updater, self).__init__()
        self.param_list = param_list
        self.update_task_factory = update_task_factory
        self.spider_task_factory = spider_task_factory
        self.update_thread_pool = XThreadPool(self.update_thread_pool_capacity)
        self.spider_thread_pool = XThreadPool(self.spider_thread_pool_capacity)
        self._is_exit = False

    def thread_main(self):
        for param in self.param_list:
            spider_task = self.spider_task_factory.get_task(param)
            if not spider_task:
                continue
            thread = self.spider_thread_pool.borrow_thread()
            spider_task.add_done_callback(self.spider_task_done_callback)
            thread.run(spider_task)
            sleep(self.interval_sleep)
        self.spider_thread_pool.release()
        self.update_thread_pool.release()

    def spider_task_done_callback(self, task):
        if not task:
            return
        ret = task.result()
        stock = task.get_stock()
        update_task = self.update_task_factory.get_task(ret, stock)
        thread = self.update_thread_pool.borrow_thread()
        thread.run(update_task)


class MultiProcessUpdater(XThread):

    def __init__(self, param_list, update_task_factory, spider_task_factory):
        super(MultiProcessUpdater, self).__init__()
        self.job_factory = UpdateJobFactory(update_task_factory, spider_task_factory)
        job_manager = XJobManager()
        job_manager.register_factory(self.job_factory)
        self.process_pool = XProcessPool(job_manager)
        self.param_list = param_list

    def thread_main(self):
        self.process_pool.start()
        for param in self.param_list:
            param_dict = XProcessPoolParam(self.job_factory.name, param).__dict__
            self.process_pool.put_param(param_dict)
        self.process_pool.release()
        self.process_pool.join()

