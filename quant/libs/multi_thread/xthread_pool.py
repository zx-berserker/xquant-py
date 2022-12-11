# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""

from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from .xthread import XThread
from threading import Event, RLock
from queue import Queue, Empty
from time import sleep


class XPoolThread(XThread):
    wait_timeout = 1

    def __init__(self, pool):
        super(XPoolThread, self).__init__()
        self._pool = pool
        self._task = None
        self._task_lock = RLock()
        self._is_busy = False
        self._ready_event = Event()
        self._is_exit = False

    def thread_main(self):
        while not self._is_exit:
            ret = self._ready_event.wait(timeout=self.wait_timeout)
            if not ret:
                continue
            self._is_busy = True
            self._ready_event.clear()
            with self._task_lock:
                if self._task:
                    self._task.executive()
                    # try:
                    #     self._task.executive()
                    # except Exception as e:
                    #     print(str(e))

            self._is_busy = False
            self._task = None
            self._pool.return_thread(self)

    def run(self, task):
        if not task:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'task is none !')
        with self._task_lock:
            self._task = task
        self._ready_event.set()

    def busy(self):
        return self._is_busy

    def exit(self):
        self._is_exit = True


class XThreadPool(object):

    def __init__(self, pool_size=8):
        self._threads = []
        self._thread_queue = Queue(pool_size)
        for i in range(0, pool_size):
            thread = XPoolThread(self)
            self._threads.append(thread)
            self._thread_queue.put(thread)
            thread.start()

    def borrow_thread(self, timeout=None):
        try:
            thread = self._thread_queue.get(timeout=timeout)
        except Empty:
            return None
        return thread

    def return_thread(self, thread):
        if not thread:
            return
        if thread.busy():
            return
        self._thread_queue.put(thread)

    def release(self):
        while True:
            if self._thread_queue.full():
                for thread in self._threads:
                    thread.exit()
                for thread in self._threads:
                    thread.join()
                return
            sleep(1)

