# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.libs.multi_thread.xtask import XTaskFactory
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.spider.spider_task import KDataSpiderTask, ShareholderSpiderTask, StockInfoSpiderTask, ProductQuoteSpiderTask, QuotePeriodEnum
from quant.spider.east_money.shareholder_info import ShareholderInfo
from quant.tool.baostock import BaoStock
from quant.models.exchange import Exchange
from quant.spider.east_money import ProductQuery


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
        return self.task_cls(param.product, param.symbol, self._period_type, self._start_date, self._end_date, self._limit)



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
        
        
        