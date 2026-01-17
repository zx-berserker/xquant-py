# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""

from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.models.k_data_daily import KDataDaily
from quant.models.k_data_monthly import KDataMonthly
from quant.models.k_data_weekly import KDataWeekly
from quant.tool.database.base import SQLAlchemy
from quant.models.shareholder import Shareholder, FloatShareholder
from quant.spider.spider_task_factory import ShareholderSpiderTaskFactory, ShareholderInfo
from quant.libs.multi_thread.xthread import XThread
from quant.libs.multi_thread.xthread_pool import XThreadPool
from quant.tool.database.update_job import UpdateJobFactory
from quant.libs.multi_process.xprocess_pool import XProcessPool
from quant.libs.multi_process.xjob import XJobManager, XProcessPoolParam
from quant.libs.multi_thread.xtask import XTaskFactory, XTask
from threading import Event
from time import sleep
import random


class Updater(XThread):
    update_thread_pool_capacity = 5
    spider_thread_pool_capacity = 1
    interval_sleep = 3
    sleep_uniform_min = 3
    sleep_uniform_max = 3

    def __init__(self, param_list, update_task_factory:XTaskFactory, spider_task_factory:XTaskFactory):
        super(Updater, self).__init__()
        self.param_list = param_list
        self.update_task_factory:XTaskFactory = update_task_factory
        self.spider_task_factory:XTaskFactory = spider_task_factory
        self.update_thread_pool = XThreadPool(self.update_thread_pool_capacity)
        self.spider_thread_pool = XThreadPool(self.spider_thread_pool_capacity)
        self._is_exit = False


    def thread_main(self):
        try:

            self.update_task_factory.env_prepare()
            self.spider_task_factory.env_prepare()
            
            for param in self.param_list:
                spider_task = self.spider_task_factory.get_task(param)
                if not spider_task:
                    continue
                thread = self.spider_thread_pool.borrow_thread()
                spider_task.add_done_callback(self.spider_task_done_callback)
                thread.run(spider_task)
                if self.sleep_uniform_max > self.sleep_uniform_min:
                    sleep(random.uniform(self.sleep_uniform_min, self.sleep_uniform_max))
                else:
                    sleep(self.interval_sleep)
        except XException as e:
            self.is_error_except = True
            print(e)
        except Exception as e:
            self.is_error_except = True
            print(e)
        
        self.spider_thread_pool.release()
        self.update_thread_pool.release()
        self.spider_task_factory.env_release()
        self.update_task_factory.env_release()



    def spider_task_done_callback(self, task:XTask):
        if not task:
            return
        ret = task.result()
        meta_data = task.get_meta_data()
        if meta_data is None:
            update_task = self.update_task_factory.get_task(ret)
        else:
            update_task = self.update_task_factory.get_task(ret, meta_data)
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

