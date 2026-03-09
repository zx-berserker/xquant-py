# -*- coding:utf-8 -*-
"""
date: 2022/12/1
author: Berserker
"""
from quant.models import Shareholder, FloatShareholder, Stock, KDataDaily, KDataWeekly, KDataMonthly, KDataHourly, Product, Exchange
from quant.models import Product, Exchange, QuoteDaily, QuoteHourly, QuoteMonthly, QuoteWeekly, TdxMarket
from quant.libs.enums import StockTypeEnum, QuotePeriodEnum
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.spider.east_money.shareholder_info import ShareholderInfo
from quant.spider.proxy import ProxyPool
from quant.spider.east_money import QuotePeriodEnum as EastQuotePeriodEnum, ProductQuery
from quant.spider.tdx import QuotePeriodEnum as TdxQuotePeriodEnum, TdxQuery
from quant.spider.spider_task_factory import ShareholderSpiderTaskFactory, KDataSpiderTaskFactory, StockInfoSpiderTaskFactory, ProductQuoteSpiderTaskFactory, HKStockFinancialInfoSpiderTaskFactory, TdxQuoteSpiderTaskTaskFactory
from quant.tool.database.database_task_factoty import BulkUpdateTaskFactory, CoerUpdateTaskFactory, CacheFileWriterTaskFactory
from quant.tool.database.updater import Updater, MultiProcessUpdater
from quant.tool.database.base import SQLAlchemy
from config.secure import CACHE_FILE_PATH
import numpy as np
from quant.models import StockInfo
from quant.libs.log import XLog
from config import root_dir



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
    flush_count = 100
    slice_capacity = 1000
    update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, stock_list, flush_count, slice_capacity)
    spider_factory = KDataSpiderTaskFactory(freq_type, start_date)
    updater = Updater(stock_list, update_task_factory, spider_factory)
    Updater.spider_thread_pool_capacity = 1
    Updater.update_thread_pool_capacity = 3
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



def update_stock_product_quote(period_type:QuotePeriodEnum=QuotePeriodEnum.DAILY, start_date:str='20060101', end_date:str="20500101", symbol:str=None, limit=10000):
    cls_type = QuoteDaily
    east_period_type = EastQuotePeriodEnum.DAILY
    if period_type == QuotePeriodEnum.MONTHLY:
        east_period_type = EastQuotePeriodEnum.MONTHLY
        cls_type = QuoteMonthly
    elif period_type == QuotePeriodEnum.HOURLY:
        east_period_type = EastQuotePeriodEnum.HOURLY
        cls_type = QuoteHourly
    elif period_type == QuotePeriodEnum.WEEKLY:
        east_period_type = EastQuotePeriodEnum.WEEKLY
        cls_type = QuoteWeekly
    query_list = []
    with SQLAlchemy.session_context() as session:
        exg_list = session.query(Exchange).filter((Exchange.code == "SH") |
                                                  (Exchange.code == "SZ") |
                                                  (Exchange.code == "HK") |
                                                  (Exchange.code == "GI") |
                                                  (Exchange.code == "HKI")).all()
        if symbol:
            is_done = True
            str_list = symbol.split(".")
            for exg in exg_list:
                prod_list = exg.products
                if is_done:
                    if exg.east_money_code != str_list[0]:
                        continue
                    for num in range(0, len(prod_list)):
                        if prod_list[num].code == str_list[1]:
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
    file_base_name = '' + period_type.name + '.json'
    flush_count = 1
    slice_capacity = 1000
    error = None
    XLog.info("update_stock_product_quote start.")
    if not ProductQuery.proxy_pool:
        ProductQuery.proxy_pool = ProxyPool()
        ProductQuery.proxy_pool.start()
    ProductQuery.read_temp_cookies()
    for query in query_list:
        exg = query["exhange"]
        data_list = query["products"]
        preflex = "%s_%s-%s(%s)-" % (start_date, end_date, exg.code, exg.east_money_code)
        update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, data_list, flush_count, slice_capacity, file_prefix_base_name=preflex)
        spider_factory = ProductQuoteSpiderTaskFactory(east_period_type, start_date, end_date, limit, prepare_type=ProductQuery.PrepareTypeEnum.SESSION_PROXY)
        param_list = spider_factory.task_param_list_generator(exg, data_list)
        Updater.spider_thread_pool_capacity = 1
        Updater.update_thread_pool_capacity = 1
        Updater.sleep_uniform_max = 3
        Updater.sleep_uniform_min = 1
        updater = Updater(param_list, update_task_factory, spider_factory)
        updater.start()
        error = updater.join()
        if error:
            XLog.error(preflex + " error break!")
            break
        XLog.info(preflex + "finish")

    ProductQuery.save_temp_cookies()
    ProductQuery.proxy_pool.stop()
    ProductQuery.proxy_pool.join()
    ProductQuery.proxy_pool = None
    XLog.info("update_stock_product_quote stop.")


def update_future_product_quote(period_type:QuotePeriodEnum=QuotePeriodEnum.DAILY, start_date:str='20060101', end_date:str="20500101", market_code:str=None, future_code:str=None, count=100):
    cls_type = QuoteDaily
    tdx_period_type = TdxQuotePeriodEnum.DAILY
    if period_type == QuotePeriodEnum.MONTHLY:
        cls_type = QuoteMonthly
        tdx_period_type = TdxQuotePeriodEnum.MONTHLY
    elif period_type == QuotePeriodEnum.HOURLY:
        cls_type = QuoteHourly
        tdx_period_type = TdxQuotePeriodEnum.HOURLY
    elif period_type == QuotePeriodEnum.WEEKLY:
        cls_type = QuoteWeekly
        tdx_period_type = TdxQuotePeriodEnum.WEEKLY
    query_list = []
    with SQLAlchemy.session_context() as session:
        market_list = session.query(TdxMarket).filter((TdxMarket.sname == "QS") |
                                                  (TdxMarket.sname == "CZ") |
                                                  (TdxMarket.sname == "QG") |
                                                  (TdxMarket.sname == "QZ") | 
                                                  (TdxMarket.sname == "QD")).all()
        if market_code and future_code:
            is_done = True
            for market in market_list:
                prod_list = market.products
                if is_done:
                    if market.code != market_code:
                        continue
                    for num in range(0, len(prod_list)):
                        if prod_list[num].code == future_code:
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
    file_base_name = '' + period_type.name + '.json'
    flush_count = 1
    slice_capacity = 1000
    XLog.info("update_future_product_quote start.")
    for query in query_list:
        market = query["market"]
        data_list = query["products"]
        preflex = "%s_%s-%s(%s)-" % (start_date, end_date, market.sname, market.code)
        update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, data_list, flush_count, slice_capacity, file_prefix_base_name=preflex)
        spider_factory = TdxQuoteSpiderTaskTaskFactory(tdx_period_type, start_date, end_date, count)
        param_list = spider_factory.task_param_list_generator(market, data_list)
        Updater.spider_thread_pool_capacity = 1
        Updater.update_thread_pool_capacity = 1
        Updater.sleep_uniform_max = 2
        Updater.sleep_uniform_min = 1
        updater = Updater(param_list, update_task_factory, spider_factory)
        updater.start()
        error = updater.join()
        if error:
            XLog.error(preflex + " error break!")
            return
        XLog.info(preflex + "finish")
    
    XLog.info("update_future_product_quote end.")



def update_hk_stock_financial_info():
    with SQLAlchemy.session_context() as session:
        product_list = session.query(Product).filter(Product.exchange_id == 9).all()
    file_path = root_dir + '/config'
    file_base_name = 'hk_stock_financial_info.json'
    flush_count = 1
    slice_capacity = 10000
    update_task_factory = CacheFileWriterTaskFactory(file_path, file_base_name, product_list, flush_count, slice_capacity)
    spider_factory = HKStockFinancialInfoSpiderTaskFactory(prepare_type=ProductQuery.PrepareTypeEnum.SESSION)
    updater = Updater(product_list, update_task_factory, spider_factory)
    Updater.spider_thread_pool_capacity = 1
    Updater.update_thread_pool_capacity = 1
    Updater.sleep_uniform_max = 5
    Updater.sleep_uniform_min = 1
    updater.start()
    error = updater.join()
    if error:
        XLog.error("hk_stock_financial_info error break!")
        return
    XLog.info("hk_stock_financial_info finish")
    
    XLog.info("end.")
    

if __name__ == "__main__":
    # update_stock_product_quote(period_type=QuotePeriodEnum.DAILY, start_date="20260224", end_date="20260224", limit=10000, symbol="1.601011")
    update_stock_product_quote(period_type=QuotePeriodEnum.DAILY, start_date="20260225", end_date="20260308", limit=10000, symbol="116.01313")

    update_stock_product_quote(period_type=QuotePeriodEnum.HOURLY, start_date="20260214", end_date="20260308", limit=10000)
    update_stock_product_quote(period_type=QuotePeriodEnum.WEEKLY, start_date="20260214", end_date="20260308", limit=10000)
    update_stock_product_quote(period_type=QuotePeriodEnum.MONTHLY, start_date="20260201", end_date="20260301", limit=10000)
    # update_hk_stock_financial_info()
    update_future_product_quote(period_type=QuotePeriodEnum.DAILY, start_date="20260309", end_date="20260309")
    update_future_product_quote(period_type=QuotePeriodEnum.HOURLY, start_date="20260309", end_date="20260309")
    update_future_product_quote(period_type=QuotePeriodEnum.WEEKLY, start_date="20260309", end_date="20260309")
    update_future_product_quote(period_type=QuotePeriodEnum.MONTHLY, start_date="20260309", end_date="20260309")

    
    ##
    pass
    