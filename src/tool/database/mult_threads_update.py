# -*- encoding:utf-8 -*-
"""
date: 2020/8/16
author: Berserker
"""

from threading import *
from queue import Queue, Empty
from enum import Enum
from app import create_app
from src.tool.database.update_from_baostock import update_stock_k_data
from src.models.stock import Stock
from src.tool.database.base import SQLAlchemy


class KDataFreqTypeEnum(Enum):
    FREQ_DAILY = 'd'
    FREQ_WEEKLY = 'w'
    FREQ_MONTHLY = 'm'


class KDataTableUpdater(object):

    def __init__(self, start_date='2006-01-01', freq_type=KDataFreqTypeEnum.FREQ_DAILY, thread_num=3, queue_size=1024):
        self.stocks_queue = Queue(queue_size)
        self.freq_type_enum = freq_type
        self.start_date = start_date
        self.thread_num = thread_num
        self.threads_list = []
        self.is_exit = False
        self.is_complete = False
        self.count = 0

    @staticmethod
    def update_thread_main(self):
        with SQLAlchemy.session_context() as session:
            while not self.is_exit:
                stock = None
                try:
                    stock = self.stocks_queue.get(timeout=0.02)
                except Empty:
                    if self.is_complete:
                        return
                    else:
                        continue
                except Exception as e:
                    print(e.args)
                    continue
                print(stock)
                update_stock_k_data(session=session, stock=stock, start_date=self.start_date,
                                    freq_type=self.freq_type_enum.value)
                print("stock:%d finished." % stock.id)

    def start(self, start_from=0, end=None):
        self.is_exit = False
        self.is_complete = False
        if len(self.threads_list) == 0:
            for i in range(0, self.thread_num):
                self.threads_list.append(
                    Thread(target=KDataTableUpdater.update_thread_main, args=(self,))
                )

        for th in self.threads_list:
            th.start()

        stock_list = None

        with SQLAlchemy.session_context() as session:
            stock_list = session.query(Stock).all()

        for stock in stock_list:
            self.count += 1
            if self.count >= start_from:
                if end is not None and self.count >= end:
                    break
                self.stocks_queue.put(stock)

        self.is_complete = True

    def wait(self):
        for th in self.threads_list:
            th.join()

    def stop(self):
        self.is_exit = True
        self.wait()
        self.count -= self.stocks_queue.qsize()
        self.threads_list.clear()


def main():
    # updater = KDataTableUpdater(start_date='2020-08-23', freq_type=KDataFreqTypeEnum.FREQ_DAILY)
    # updater.start()
    # updater.wait()
    pass