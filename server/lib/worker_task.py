# -*- coding:utf-8 -*-
"""
date: 2026/04/04
author: Berserker
"""
from quant.libs.multi_thread import XTask
# from quant.update import update_stock_product_quote, update_future_product_quote
from quant.libs.enums import QuotePeriodEnum
import time
from quant.libs.log import XLog
from quant.tool.database.updater import Updater
from quant.tool.database.base import SQLAlchemy
from config.secure import CACHE_FILE_PATH
from quant.models import Exchange, TdxMarket
from quant.spider.tdx import QuotePeriodEnum as TdxQuotePeriodEnum, TdxQuery
from quant.spider.spider_task_factory import  TdxQuoteSpiderTaskTaskFactory
from quant.tool.database.database_task_factoty import CacheFileWriterTaskFactory



class WorkerTaskBase(XTask):
    update_state = 'Update State'
    is_active = True
    def __init__(self, name='WorkerTaskBase'):
        super(WorkerTaskBase, self).__init__(name)
    
    def exit(self):
        pass


class StockUpdateWorkerTask(WorkerTaskBase):
    update_state = 'Update State'
    is_active = True 

    def __init__(self, period:QuotePeriodEnum, start_time=None, end_time=None, limit=100, tdx_code:str=None, exchange_code=None):
        super(StockUpdateWorkerTask, self).__init__('StockUpdateWorkerTask')
        TdxQuery.is_active = True
        self.period = period
        self.start_time = start_time
        self.end_time = end_time
        self.limit = limit
        self.tdx_code = tdx_code
        self.exchange_code = exchange_code
        self.updater:Updater = None

    def exit(self):
        self.updater.exit()
        TdxQuery.is_active = False

    def task_main(self):
        StockUpdateWorkerTask.update_state = "StockUpdateWorkerTask State: running."
        tdx_period_type = TdxQuotePeriodEnum[self.period.name]
        query_list = []
        with SQLAlchemy.session_context() as session:
            exg_list = session.query(Exchange).filter((Exchange.code == "SH") |
                                                      (Exchange.code == "SZ") |
                                                      (Exchange.code == "HK") |
                                                      (Exchange.code == "GI") |
                                                      (Exchange.code == "HKI")).all()
            if self.tdx_code and self.exchange_code:
                is_done = True
                # str_list = symbol.split(".")
                for exg in exg_list:
                    prod_list = exg.products
                    if is_done:
                        if exg.code != self.exchange_code:
                            continue
                        for num in range(0, len(prod_list)):
                            if prod_list[num].tdx_code == self.tdx_code:
                                is_done = False
                                prod_list = prod_list[num+1:]
                                break
                    if is_done == False:
                        if len(prod_list) > 0:
                            query_list.append({
                                "exhange": exg,
                                "products": prod_list
                            })
            else:    
                for exg in exg_list:
                    prod_list = exg.products
                    query_list.append({
                        "exhange": exg,
                        "products": prod_list
                    })


        file_path = CACHE_FILE_PATH
        file_base_name = '' + self.period.name + '.json'
        flush_count = 1
        slice_capacity = 1000
        error = None
        XLog.info("update_stock_product_quote start.")

        for query in query_list:
            exg = query["exhange"]
            data_list = query["products"]
            preflex = "%s_%s-%s(%s)-" % (self.start_time, self.end_time, exg.code, exg.east_money_code)
            update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, data_list, flush_count, slice_capacity, file_prefix_base_name=preflex)
            spider_factory = TdxQuoteSpiderTaskTaskFactory(tdx_period_type, self.start_time, self.end_time, self.limit)
            param_list = spider_factory.task_param_list_generator(None, data_list)
            Updater.spider_thread_pool_capacity = 1
            Updater.update_thread_pool_capacity = 3
            Updater.sleep_uniform_max = 0.5
            Updater.sleep_uniform_min = 0
            self.updater = Updater(param_list, update_task_factory, spider_factory)
            self.updater.start()
            error = self.updater.join()
            if error:
                XLog.error(preflex + " error break!")
                break
            XLog.info(preflex + "finish")

        XLog.info("update_stock_product_quote stop.")
        StockUpdateWorkerTask.update_state = "StockUpdateWorkerTask State: finished."
    


class FutureUpdateWorkerTask(XTask):
    update_state = 'Update State'
    is_active = True 

    def __init__(self, period:QuotePeriodEnum, start_time=None, end_time=None, limit=100, market_code:str=None, future_code:str=None):
        super(FutureUpdateWorkerTask, self).__init__('FutureUpdateWorkerTask')
        TdxQuery.is_active = True
        self.period:QuotePeriodEnum = period
        self.start_time = start_time
        self.end_time = end_time
        self.limit = limit
        self.market_code = market_code
        self.future_code = future_code
        self.updater:Updater = None

    def exit(self):
        self.updater.exit()
        TdxQuery.is_active = False

    def task_main(self):
        FutureUpdateWorkerTask.update_state = "FutureUpdateWorkerTask State: running."
        tdx_period_type = TdxQuotePeriodEnum[self.period.name]
        query_list = []
        with SQLAlchemy.session_context() as session:
            market_list = session.query(TdxMarket).filter((TdxMarket.sname == "QS") |
                                                      (TdxMarket.sname == "CZ") |
                                                      (TdxMarket.sname == "QG") |
                                                      (TdxMarket.sname == "QZ") | 
                                                      (TdxMarket.sname == "QD")).all()
            if self.market_code and self.future_code:
                is_done = True
                for market in market_list:
                    prod_list = market.products
                    if is_done:
                        if market.code != self.market_code:
                            continue
                        for num in range(0, len(prod_list)):
                            if prod_list[num].code == self.future_code:
                                is_done = False
                                prod_list = prod_list[num+1:]
                                break
                    if is_done == False:
                        if len(prod_list) > 0:
                            query_list.append({
                                "market": market,
                                "products": prod_list
                            })
            else:    
                for market in market_list:
                    prod_list = market.products
                    query_list.append({
                        "market": market,
                        "products": prod_list
                    })


        file_path = CACHE_FILE_PATH
        file_base_name = '' + self.period.name + '.json'
        flush_count = 1
        slice_capacity = 1000
        XLog.info("update_future_product_quote start.")
        for query in query_list:
            market = query["market"]
            data_list = query["products"]
            preflex = "%s_%s-%s(%s)-" % (self.start_time, self.end_time, market.sname, market.code)
            update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, data_list, flush_count, slice_capacity, file_prefix_base_name=preflex)
            spider_factory = TdxQuoteSpiderTaskTaskFactory(tdx_period_type, self.start_time, self.end_time, self.limit)
            param_list = spider_factory.task_param_list_generator(market, data_list)
            Updater.spider_thread_pool_capacity = 1
            Updater.update_thread_pool_capacity = 1
            Updater.sleep_uniform_max = 2
            Updater.sleep_uniform_min = 1
            self.updater = Updater(param_list, update_task_factory, spider_factory)
            self.updater.start()
            error = self.updater.join()
            if error:
                XLog.error(preflex + " error break!")
                return
            XLog.info(preflex + "finish")

        XLog.info("update_future_product_quote end.")
        FutureUpdateWorkerTask.update_state = "FutureUpdateWorkerTask State: finished."



if __name__ == '__main__':
    task = FutureUpdateWorkerTask(QuotePeriodEnum.DAILY)
    task.task_main()