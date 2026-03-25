# -*- coding:utf-8 -*-
"""
date: 2026/01/16
author: Berserker
"""
from queue import Queue, Empty
from quant.libs.multi_thread import XThread, XTask
from quant.update import update_stock_product_quote, update_future_product_quote
from quant.libs.enums import QuotePeriodEnum
import time
from quant.libs.log import XLog
from .event import QuoteUpdateEvent, EventQueue


class StockUpdateWorkerTask(XTask):
    update_state = 'Update State'

    def __init__(self, period:QuotePeriodEnum, start_time=None, end_time=None, limit=1000):
        super(StockUpdateWorkerTask, self).__init__('StockUpdateWorkerTask')
        self.period = period
        self.start_time = start_time
        self.end_time = end_time
        self.limit = limit

    def task_main(self):
        StockUpdateWorkerTask.update_state = "StockUpdateWorkerTask State: running."
        update_stock_product_quote(self.period, self.start_time, self.end_time, limit=self.limit)
        # update_future_product_quote(self.period, self.start_time, self.end_time)
        StockUpdateWorkerTask.update_state = "StockUpdateWorkerTask State: finished."
    

class FutureUpdateWorkerTask(XTask):
    update_state = 'Update State'

    def __init__(self, period:QuotePeriodEnum, start_time=None, end_time=None, limit=1000):
        super(FutureUpdateWorkerTask, self).__init__('FutureUpdateWorkerTask')
        self.period = period
        self.start_time = start_time
        self.end_time = end_time
        self.limit = limit

    def task_main(self):
        FutureUpdateWorkerTask.update_state = "FutureUpdateWorkerTask State: running."
        # update_stock_product_quote(self.period, self.start_time, self.end_time, limit=self.limit)
        update_future_product_quote(self.period, self.start_time, self.end_time)
        FutureUpdateWorkerTask.update_state = "FutureUpdateWorkerTask State: finished."


class WorkerBass(XThread):
    _is_running = True

    def __init__(self, id:str="WorkerBass"):
        super(WorkerBass,self).__init__(id)



class ServerWebWorker(WorkerBass):
    _worker_task_queue = Queue()
    _is_future_update = False
    def __init__(self):
        super(ServerWebWorker,self).__init__("ServerWebWorker")

    @classmethod
    def future_update(cls):
        cls._is_future_update =  True

    @classmethod
    def put_task(cls, task:XTask):
        cls._worker_task_queue.put(task)

    def thread_main(self):
        while WorkerBass._is_running:
            try:
                task:XTask = ServerWebWorker._worker_task_queue.get(timeout=10)
                if task.name == 'FutureUpdateWorkerTask':
                    if ServerWebWorker._is_future_update:
                        task.executive()
                    else:
                        ServerWebWorker._worker_task_queue.put(task)
                        time.sleep(10)
                else:
                        task.executive()
            except:
                ServerWebWorker._is_future_update = False
                pass



class ServerXLogEventWorker(WorkerBass):

    def __init__(self):
        super(ServerXLogEventWorker, self).__init__("ServerXLogEventWorker")

    def thread_main(self):
        while WorkerBass._is_running:
            if not EventQueue.is_available():
                time.sleep(5)
                continue
            message = XLog.fastapi_get()
            if message:
                event = QuoteUpdateEvent(message)
                EventQueue.put_event(event)


class ServerWorkerController:
    
    _worker_list:list[WorkerBass.__class__] = [ServerWebWorker, ServerXLogEventWorker]
    _worker_obj_list = []

    @classmethod
    def start(cls):
        for worker_cls in cls._worker_list:
            worker = worker_cls()
            worker.start()
            cls._worker_obj_list.append(worker)

    @classmethod
    def stop(cls):
        WorkerBass._is_running = False
