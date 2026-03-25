# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.libs.multi_thread.xtask import XTaskFactory, XTask
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.spider.spider_task import KDataSpiderTask, ShareholderSpiderTask, StockInfoSpiderTask, ProductQuoteSpiderTask, QuotePeriodEnum, HKStockFinancialInfoSpiderTask, TdxQuotePeriodEnum, TdxQuery, TdxQuoteSpiderTask
from quant.spider.east_money.shareholder_info import ShareholderInfo
from quant.tool.baostock import BaoStock
from quant.models import Exchange, TdxMarket, Product
from quant.spider.east_money import ProductQuery


class TdxQuoteSpiderTaskTaskFactory(XTaskFactory):

    class TaskParam:
        def __init__(self, product, market, code):
            self.product:Product = product
            self.market:str = market
            self.code:str = code
            pass

    def __init__(self, period_type:TdxQuotePeriodEnum=TdxQuotePeriodEnum.DAILY, start_time='20060101', end_time='20500101', count:int=100):
        super(TdxQuoteSpiderTaskTaskFactory, self).__init__(TdxQuoteSpiderTask)
        self.period_type = period_type
        self.start_time = start_time
        self.end_time = end_time
        self.count = count

    def task_param_list_generator(self, market:TdxMarket, product_list):
        class ParamIter():
            def __init__(self,market:TdxMarket, product_list):                    
                self.market = market
                self.data_list = product_list
                self.current = 0
            def __iter__(self):
                return self
            def __next__(self):
                if self.current < len(self.data_list):
                    product:Product = self.data_list[self.current]
                    market_code = None
                    if self.market:
                        market_code = self.market.code
                    param = TdxQuoteSpiderTaskTaskFactory.TaskParam(product, market_code, product.tdx_code)
                    self.current += 1
                    return param
                else:
                    raise StopIteration
        return ParamIter(market, product_list)
    

    def env_prepare(self):
        TdxQuery.connect()
    
    def env_release(self):
        TdxQuery.disconnect()
        
    def get_task(self, param:TaskParam):
        self.except_watch()
        task:TdxQuoteSpiderTask = self.task_cls(param.product, param.market, param.code, 
                 self.period_type, self.start_time, self.end_time, self.count)
        task.add_except_callback(self.task_except_callback)
        return task
    
    def task_except_callback(self, exception):
        self._exception = exception

    def except_watch(self):
        if self._exception:
            raise self._exception




class  HKStockFinancialInfoSpiderTaskFactory(XTaskFactory):

    def __init__(self, 
                 prepare_type:ProductQuery.PrepareTypeEnum=ProductQuery.PrepareTypeEnum.SESSION, 
                 use_mapping=False
                 ):
        super(HKStockFinancialInfoSpiderTaskFactory, self).__init__(HKStockFinancialInfoSpiderTask)
        self._prepare_type = prepare_type
        self._use_mapping = use_mapping

    def get_task(self, product):
        task:XTask = self.task_cls(product, product.code, use_mapping=self._use_mapping)
        task.add_except_callback(self.task_except_callback)
        return task

    def env_prepare(self):
        ProductQuery.prepare(self._prepare_type)

    def task_except_callback(self, exception):
        self._exception = exception

    def except_watch(self):
        if self._exception:
            raise self._exception
  


class  ProductQuoteSpiderTaskFactory(XTaskFactory):
    class TaskParam: 
        def __init__(self, product, symbol:str):
            self.product = product
            self.symbol = symbol
            pass

    def __init__(self, period_type:QuotePeriodEnum=QuotePeriodEnum.DAILY, start_date='20060101', end_date='20500101', limit:int=10000, prepare_type:ProductQuery.PrepareTypeEnum=ProductQuery.PrepareTypeEnum.SESSION_PROXY):
        super(ProductQuoteSpiderTaskFactory, self).__init__(ProductQuoteSpiderTask)
        self._period_type = period_type
        self._start_date = start_date
        self._end_date = end_date
        self._limit = limit
        self._prepare_type = prepare_type

    def task_param_list_generator(self, exchange:Exchange, product_list):
        class ParamIter():
            def __init__(self,exchange:Exchange, product_list):                    
                self.exg = exchange
                self.data_list = product_list
                self.current = 0
            def __iter__(self):
                return self
            def __next__(self):
                if self.current < len(self.data_list):
                    symbol = "%s.%s" % (self.exg.east_money_code, self.data_list[self.current].code)
                    param = ProductQuoteSpiderTaskFactory.TaskParam(self.data_list[self.current], symbol)
                    self.current += 1
                    return param
                else:
                    raise StopIteration
        return ParamIter(exchange, product_list)
    
    def env_prepare(self):
        ProductQuery.prepare(self._prepare_type)
        
    def get_task(self, param:TaskParam):
        self.except_watch()
        task = self.task_cls(param.product, param.symbol, self._period_type, self._start_date, self._end_date, self._limit)
        task.add_except_callback(self.task_except_callback)
        return task
    
    def task_except_callback(self, exception):
        self._exception = exception

    def except_watch(self):
        if self._exception:
            raise self._exception




class KDataSpiderTaskFactory(XTaskFactory):

    def __init__(self, freq_type=QueryStockInfo.FreqTypeEnum.FREQ_DAILY, start_date='2006-03-27', end_date=None):
        super(KDataSpiderTaskFactory, self).__init__(KDataSpiderTask)
        self._freq_type = freq_type
        self._start_date = start_date
        self._end_date = end_date

    def get_task(self, stock):
        return self.task_cls(stock, self._freq_type, self._start_date, self._end_date)

    def env_prepare(self):
        BaoStock.login()

    def env_release(self):
        BaoStock.logout()


class ShareholderSpiderTaskFactory(XTaskFactory):

    def __init__(self, query_type=ShareholderInfo.QueryTypeEnum.QUERY_FLOAT_SHARE_HOLDER):
        super(ShareholderSpiderTaskFactory, self).__init__(ShareholderSpiderTask)
        self._query_type = query_type

    def get_task(self, page_index):
        return self.task_cls(page_index, self._query_type)

    def env_prepare(self):
        BaoStock.login()

    def env_release(self):
        BaoStock.logout()
         

class StockInfoSpiderTaskFactory(XTaskFactory):
    
    def __init__(self, year=None, quarter=None):
        super(StockInfoSpiderTaskFactory, self).__init__(StockInfoSpiderTask)
        self.year = year
        self.quarter = quarter
        
    def get_task(self, stock):
        return self.task_cls(stock, self.year, self.quarter)

    def env_prepare(self):
        BaoStock.login()

    def env_release(self):
        BaoStock.logout()
        
        
        