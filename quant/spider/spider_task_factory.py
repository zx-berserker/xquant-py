# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.libs.multi_thread.xtask import XTaskFactory
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.spider.spider_task import KDataSpiderTask, ShareholderSpiderTask, StockInfoSpiderTask
from quant.spider.east_money.shareholder_info import ShareholderInfo
from quant.tool.baostock import BaoStock


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
        
        
        