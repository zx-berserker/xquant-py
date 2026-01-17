# -*- coding:utf-8 -*-
"""
date: 2026/01/16
author: Berserker
"""
from queue import Queue, Empty
from quant.libs.multi_thread import XThread, XTask
from quant.update import update_product_quote
from quant.spider.east_money import QuotePeriodEnum
import time

class UpdateWorkerTask(XTask):
    update_state = 'Update State'

    def __init__(self, period:QuotePeriodEnum, start_time=None, end_time=None, limit=1000):
        super(UpdateWorkerTask, self).__init__()
        self.period = period
        self.start_time = start_time
        self.end_time = end_time
        self.limit = limit

    def task_main(self):
        UpdateWorkerTask.update_state = "Update State: running."
        update_product_quote(self.period, self.start_time, self.end_time, limit=self.limit)
        UpdateWorkerTask.update_state = "Update State: finished."
    




class ServerWorker(XThread):
    worker_task_queue = Queue()


    def __init__(self):
        super(ServerWorker,self).__init__("ServerWorker")

    def thread_main(self):
        while True:
            task:XTask = ServerWorker.worker_task_queue.get()
            task.executive()


