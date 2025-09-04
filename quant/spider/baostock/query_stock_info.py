# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from quant.tool.baostock import BaoStock
import baostock as bs
import pandas as pd
import time
from enum import Enum
from contextlib import contextmanager


class QueryStockInfo(object):

    class FreqTypeEnum(Enum):
        FREQ_HOURLY = '60'
        FREQ_DAILY = 'd'
        FREQ_WEEKLY = 'w'
        FREQ_MONTHLY = 'm'

    @staticmethod
    @contextmanager
    def login_context():
        BaoStock.login()
        yield
        BaoStock.logout()

    @staticmethod
    @BaoStock.connector
    def query_all_stock_code(date=None):
        """
        :param date: YYYY-MM-DD
        :return: (pandas.DataFrame)
            code: 证券代码
            tradeStatus: 交易状态(1：正常交易 0：停牌）
            code_name: 证券名称
        """
        if date is None:
            date = time.strftime("%Y-%m-%d", time.localtime())
        ret = bs.query_all_stock(date)
        data_list = []
        while (ret.error_code == '0') and ret.next():
            data_list.append(ret.get_row_data())

        data_df = pd.DataFrame(data_list, columns=ret.fields)
        return data_df

    @staticmethod
    @BaoStock.connector
    def query_stock_info(code=None, name=None):
        """
        :param code: 证券代码
        :param name: 证券名称
        :return: (pandas.DataFrame)
            code: 证券代码
            code_name: 证券名称
            ipoDate: 上市日期
            outDate: 退市日期
            type: 证券类型，其中 1：股票，2：指数,3：其它
            status: 上市状态，其中 1：上市，0：退市
        """
        ret = None
        if code is not None:
            ret = bs.query_stock_basic(code=code)
        elif name is not None:
            ret = bs.query_stock_basic(code_name=name)
        data_list = []
        while (ret.error_code == '0') and ret.next():
            data_list.append(ret.get_row_data())

        data_df = pd.DataFrame(data_list, columns=ret.fields)
        return data_df

    @staticmethod
    @BaoStock.connector
    def query_k_data(code, start_date='2006-01-01',end_date=None, freq_type=FreqTypeEnum.FREQ_DAILY, adjust_flag='3'):
        """
        :param code: 股票代码
        :param start_date: 开始日期 格式“YYYY-MM-DD”
        :param end_date: 结束日期（包含），格式“YYYY-MM-DD”，为空时取最近一个交易日
        :param freq_type: 数据类型 d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k
        :param adjust_flag: 复权类型 3:不复权、1:后复权、2:前复权
        :return: (pandas.DataFrame)
            date: 交易所行情日期
            code: 证券代码
            open: 开盘价
            high: 最高价
            low: 最低价
            close: 收盘价
            preclose: 前收盘价
            volume: 成交量（累计 单位：股）
            amount: 成交额（单位：人民币元）
            turn: 换手率
            pctChg: 涨跌幅（百分比）
            peTTM: 滚动市盈率
            pbMRQ: 市净率
            psTTM: 滚动市销率
            pcfNcfTTM: 滚动市现率
        """
        fields_str = "date,code,open,high,low,close,volume,amount,turn,pctChg,preclose,peTTM,pbMRQ,psTTM,pcfNcfTTM"
        if freq_type == QueryStockInfo.FreqTypeEnum.FREQ_WEEKLY or freq_type == QueryStockInfo.FreqTypeEnum.FREQ_MONTHLY:
            fields_str = "date,code,open,high,low,close,volume,amount,turn,pctChg"
        elif freq_type == QueryStockInfo.FreqTypeEnum.FREQ_HOURLY:
            fields_str = "time,code,open,high,low,close,volume,amount"
        ret = bs.query_history_k_data_plus(
            code,
            fields_str,
            start_date=start_date,
            end_date=end_date,
            frequency=freq_type.value,
            adjustflag=adjust_flag
        )
        data_list = []
        while (ret.error_code == '0') and ret.next():
            data_list.append(ret.get_row_data())

        data_df = pd.DataFrame(data_list, columns=ret.fields)
        return data_df

    @staticmethod
    @BaoStock.connector
    def query_stock_profit_data(code="sh.600000", year=None, quarter=None):
        """
        Args:
            code (sting): 股票代码
            year (num): 年  空时默认当前年
            quarter (num): 季度(1 2 3 4) 空时默认当前季度
        """
        ret = bs.query_profit_data(code, year, quarter)
        data_list = []
        while (ret.error_code == '0') and ret.next():
            data_list.append(ret.get_row_data())     
        data_df = pd.DataFrame(data_list, columns=ret.fields)
        return data_df
    
    
