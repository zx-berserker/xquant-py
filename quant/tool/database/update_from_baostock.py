# -*- encoding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.models.block import Block
from quant.models.strategy import Strategy
from quant.models.k_data_daily import KDataDaily
from quant.models.k_data_monthly import KDataMonthly
from quant.models.k_data_weekly import KDataWeekly
from quant.models.industry import Industry
from quant.models.stock import Stock
from quant.models.trade import Trade
from quant.tool.ini_file_reader import IniFileReader
from quant.tool.database.base import SQLAlchemy


def find_stock_industry_id(session=None, stock_code=None):
    reader = IniFileReader('./file/industry.ini')
    data_list = reader.get_ini_infos('industry')
    for obj in data_list:
        for key, value in obj.items():
            code_list = value.split(',')
            code = stock_code.split('.')[1]
            if code in code_list:
                industry = session.query(Industry).filter(Industry.code == key).first()
                return industry.id
    return None


def update_stock_table(session=None):
    stocks_df = QueryStockInfo.query_all_stock_code()
    for index in stocks_df.index:
        code = stocks_df.loc[index].values[0]
        stock_info_df = QueryStockInfo.query_stock_info(code=code)
        industry_id = None
        if stock_info_df.empty:
            continue
        if int(stock_info_df.loc[0].values[4]) == 1:
            industry_id = find_stock_industry_id(session, code)
        stock = Stock(
            code=code,
            industry_id=industry_id,
            name=stock_info_df.loc[0].values[1],
            _stock_type=int(stock_info_df.loc[0].values[4])
        )
        if session is not None:
            with SQLAlchemy.auto_commit(session):
                session.add(stock)


def check_df_value(value, default):
    return default if (value == '' or value is None) else value


def update_stock_k_data(session=None, stock=None, start_date='2006-01-01', freq_type='d'):
    if stock is None:
        print("stock is None!!!")
        return
    cls_type = KDataDaily
    if freq_type == 'w':
        cls_type = KDataWeekly
    elif freq_type == 'm':
        cls_type = KDataMonthly
    k_data_df = QueryStockInfo.query_k_data(stock.code, start_date=start_date, freq_type=freq_type)
    data_list = []
    for index in k_data_df.index:
        data_dict = {
            'date': (k_data_df.loc[index].values[0]),
            'stock_id': stock.id,
            'open': k_data_df.loc[index].values[2],
            'high': k_data_df.loc[index].values[3],
            'low': k_data_df.loc[index].values[4],
            'close': check_df_value(k_data_df.loc[index].values[5], 0.0),
            'volume': check_df_value(k_data_df.loc[index].values[6], 0),
            'amount': check_df_value(k_data_df.loc[index].values[7], 0.0),
            'turn': check_df_value(k_data_df.loc[index].values[8], 0.0),
            'pct_chg': check_df_value(k_data_df.loc[index].values[9], 0.0),
        }
        if freq_type == 'd':
            data_dict['pre_close'] = check_df_value(k_data_df.loc[index].values[10], 0.0)
            data_dict['pe_ttm'] = check_df_value(k_data_df.loc[index].values[11], 0.0)
            data_dict['pb_mrq'] = check_df_value(k_data_df.loc[index].values[12], 0.0)
            data_dict['ps_ttm'] = check_df_value(k_data_df.loc[index].values[13], 0.0)
            data_dict['pcf_ncf_ttm'] = check_df_value(k_data_df.loc[index].values[14], 0.0)
        data_list.append(data_dict)

    if session is not None:
        with SQLAlchemy.auto_commit(session):
            session.bulk_insert_mappings(cls_type, data_list)


def main():
    pass
