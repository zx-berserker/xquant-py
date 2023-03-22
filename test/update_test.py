# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
import os, sys
sys.path.append(os.getcwd())

from quant.models import Shareholder, FloatShareholder, Stock, KDataDaily, KDataWeekly, KDataMonthly, KDataHourly
from quant.libs.enums import StockTypeEnum
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.spider.east_money.shareholder_info import ShareholderInfo
from quant.spider.spider_task_factory import ShareholderSpiderTaskFactory, KDataSpiderTaskFactory, StockInfoSpiderTaskFactory
from quant.tool.database.database_task_factoty import BulkUpdateTaskFactory, CoerUpdateTaskFactory, CacheFileWriterTaskFactory
from quant.tool.database.updater import Updater, MultiProcessUpdater
from quant.tool.database.base import SQLAlchemy
import numpy as np
from quant.models import StockInfo


def main_update_shareholder():
    SQLAlchemy.create_all()
    update_task_factory = BulkUpdateTaskFactory(Shareholder)
    spider_factory = ShareholderSpiderTaskFactory(ShareholderInfo.QueryTypeEnum.QUERY_SHARE_HOLDER)
    updater = Updater(update_task_factory, spider_factory)
    # factory = ShareholderSpiderTaskFactory(ShareholderInfo.QueryTypeEnum.QUERY_FLOAT_SHARE_HOLDER, interval_time=5)
    # updater = Updater(FloatShareholder, factory)
    updater.start()
    updater.join()


def main_update_k_data(start_id=1, end_id=None, freq_type=QueryStockInfo.FreqTypeEnum.FREQ_DAILY,
                       start_date='2022-11-5', is_mult=True):
    SQLAlchemy.create_all()
    cls_type = KDataDaily
    if freq_type == QueryStockInfo.FreqTypeEnum.FREQ_MONTHLY:
        cls_type = KDataMonthly
    elif freq_type == QueryStockInfo.FreqTypeEnum.FREQ_HOURLY:
        cls_type = KDataHourly
    elif freq_type == QueryStockInfo.FreqTypeEnum.FREQ_WEEKLY:
        cls_type == KDataWeekly
    begin = None if start_id is None else start_id - 1
    end = None if end_id is None else end_id - 1
    with SQLAlchemy.session_context() as session:
        data_list = session.query(Stock).all()
    stock_list = data_list[begin:end]
    if is_mult:
        update_task_factory = BulkUpdateTaskFactory(cls_type)
        spider_factory = KDataSpiderTaskFactory(freq_type, start_date)
        updater = MultiProcessUpdater(stock_list, update_task_factory, spider_factory)
        with QueryStockInfo.login_context():
            updater.start()
            updater.join()
    else:
        update_task_factory = CoerUpdateTaskFactory(cls_type)
        spider_factory = KDataSpiderTaskFactory(freq_type, start_date)
        updater = Updater(stock_list, update_task_factory, spider_factory)
        updater.start()
        updater.join()


def main_update_stock_info(start_id=0):
    SQLAlchemy.create_all()
    with SQLAlchemy.session_context() as session:
        data_list = session.query(Stock).all()
    stock_list = data_list[start_id:]
    update_task_factory = BulkUpdateTaskFactory(StockInfo)
    spider_factory = StockInfoSpiderTaskFactory(year=2022)
    updater = MultiProcessUpdater(stock_list, update_task_factory, spider_factory)
    with QueryStockInfo.login_context():
        updater.start()
        updater.join()


def main_get_k_data_cache(start_id=None, end_id=None,
                          freq_type=QueryStockInfo.FreqTypeEnum.FREQ_DAILY, start_date='2022-11-5'):
    if freq_type == QueryStockInfo.FreqTypeEnum.FREQ_MONTHLY:
        cls_type = KDataMonthly
    elif freq_type == QueryStockInfo.FreqTypeEnum.FREQ_HOURLY:
        cls_type = KDataHourly
    elif freq_type == QueryStockInfo.FreqTypeEnum.FREQ_WEEKLY:
        cls_type == KDataWeekly
    
    with SQLAlchemy.session_context() as session:
        data_list = session.query(Stock).all()
    begin = None if start_id is None else start_id - 1
    end = None if end_id is None else end_id - 1
    stock_list = data_list[begin:end]
    file_path = 'F:/WorkSpace/DataBase/Cache'
    file_base_name = '' + freq_type.value + '.json'
    flush_count = 50
    slice_capacity = 1000
    update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, stock_list, flush_count, slice_capacity)
    spider_factory = KDataSpiderTaskFactory(freq_type, start_date)
    updater = Updater(stock_list, update_task_factory, spider_factory)
    Updater.spider_thread_pool_capacity = 1
    Updater.update_thread_pool_capacity = 1
    with QueryStockInfo.login_context():
        updater.start()
        updater.join()
    
    
def main_get_stock_info_cache(start_id=None, end_id=None, year=2022, quarter=3):
    SQLAlchemy.create_all()
    with SQLAlchemy.session_context() as session:
        data_list = session.query(Stock).all()
    begin = None if start_id is None else start_id - 1
    end = None if end_id is None else end_id - 1
    stock_list = data_list[begin:end]
    file_path = 'F:/WorkSpace/DataBase/Cache'
    file_base_name = 'stock_info' + '.json'
    flush_count = 100
    slice_capacity = 1000
    update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, stock_list, flush_count, slice_capacity)
    spider_factory = StockInfoSpiderTaskFactory(year, quarter)
    updater = Updater(stock_list, update_task_factory, spider_factory)
    Updater.spider_thread_pool_capacity = 1
    Updater.update_thread_pool_capacity = 3

    updater.start()
    updater.join()
    
    
if __name__ == '__main__':
    main_get_k_data_cache(1, None, QueryStockInfo.FreqTypeEnum.FREQ_DAILY, '2023-03-05')
    # main_get_stock_info_cache(1)
    # main_update_k_data(start_id=155, end_id=None, start_date='2022-11-24', is_mult=True)
    pass
