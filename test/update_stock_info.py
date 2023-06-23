# -*- encoding:utf-8 -*-
"""
date: 2023/06/23
author: Berserker
"""
from quant.libs.enums import StockTypeEnum
from quant.tool.database.base import SQLAlchemy
from quant.models.stock import Stock
from quant.models.stock_info import StockInfo
from quant.tool.database.database_task_factoty import CacheFileWriterTaskFactory
from quant.spider.spider_task_factory import StockInfoSpiderTaskFactory
from quant.tool.database.updater import Updater, MultiProcessUpdater
from quant.spider.baostock.query_stock_info import QueryStockInfo

def main_update_stock_info(start_id=1, end_id=None, year=2022,  quarter=None):
    SQLAlchemy.create_all()
    with SQLAlchemy.session_context() as session:
        data_list = session.query(Stock).filter(Stock._stock_type==StockTypeEnum.STOCK_SHARES.value).all()
    # print(data_list)
    begin = None if start_id is None else start_id - 1
    end = None if end_id is None else end_id - 1
    stock_list = data_list[begin:end]
    file_path = 'C:/WorkSpace/Cache'
    # file_path = "F:/WorkSpace/DataBase/Cache"
    file_base_name = 'stock_info-q'+ str(quarter) +'.json'
    print(file_base_name)
    flush_count = 50
    slice_capacity = 3000
    update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, stock_list, flush_count, slice_capacity)
    spider_factory = StockInfoSpiderTaskFactory(year, quarter)
    updater = Updater(stock_list, update_task_factory, spider_factory)
    Updater.spider_thread_pool_capacity = 1
    Updater.update_thread_pool_capacity = 1
    with QueryStockInfo.login_context():
        updater.start()
        updater.join()
        
        
if __name__ == "__main__":
    main_update_stock_info(quarter=1)
    # main_update_stock_info(quarter=2)
    main_update_stock_info(quarter=3)
    main_update_stock_info(quarter=4)
