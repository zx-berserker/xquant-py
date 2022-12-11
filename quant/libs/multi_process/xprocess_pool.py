# -*- encoding:utf-8 -*-
"""
date: 2020/11/3
author: Berserker
"""

from quant.libs.multi_process.xprocess import XProcess
from time import sleep
from quant.tool.function_tool import get_fn_arg_count
from multiprocessing import cpu_count, Queue


class XPoolProcess(XProcess):
    sleep_for = 0.5

    def __init__(self, param_queue, job_manager, error_callback=None):
        super(XPoolProcess, self).__init__()
        self.param_queue = param_queue
        self.job_manager = job_manager
        self.error_callback = error_callback

    @staticmethod
    def process_main(self_obj):
        self_obj.job_manager.env_prepare()
        while True:
            param = self_obj.param_queue.get()
            if param is None:
                break
            job = self_obj.job_manager.get_job(param)
            if job is None:
                continue
            try:
                ret = job.do()
                job_done_callback = self_obj.job_manager.get_done_callback(job)
                if job_done_callback:
                    num = get_fn_arg_count(job_done_callback)
                    if num:
                        job_done_callback(ret)
                    else:
                        job_done_callback()
            except Exception as e:
                if self_obj.error_callback:
                    self_obj.error_callback(job, e)
        self_obj.job_manager.env_release()


class XProcessPool:
    process_num = cpu_count() - 1
    queue_capacity = 16

    def __init__(self, job_manager):
        self.param_queue = Queue(self.queue_capacity)
        self.job_manager = job_manager
        self.process_list = [XPoolProcess(self.param_queue, self.job_manager, XProcessPool.error_callback) for i in
                             range(self.process_num)]

    @staticmethod
    def error_callback(job, e):
        print("Error!!! job:%s exception:%s" % (job, str(e)))

    def put_param(self, param):
        self.param_queue.put(param)

    def start(self):
        for process in self.process_list:
            process.start()

    def join(self):
        for process in self.process_list:
            process.join()

    def release(self):
        for i  in range(self.process_num):
            self.put_param(None)

