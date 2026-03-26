# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""
import os, sys
sys.path.append(os.getcwd())

from quant.tool.database.base import SQLAlchemy
from quant.models.block import Block
from quant.models.many_to_many_table import stock_block_table
from quant.models.k_data_daily import KDataDaily
from sqlalchemy import func
from operator import and_
from quant.tool.database.data_models.block import BlockData
from quant.tool.file_writer import FileWriterTaskFactory
from quant.models.stock import Stock
from quant.models.stock_info import StockInfo
from quant.models import Product, Exchange, QuoteDaily, QuoteHourly, QuoteMonthly, QuoteWeekly, TdxMarket
from quant.libs.enums import StockTypeEnum, QuotePeriodEnum
from sqlalchemy import delete
import pandas as pd
from datetime import timedelta, datetime


def query_test():
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Exchange).all()
        # for block in block_list:
        #     # query_block_avg(block, session)
        #     data_list = BlockData.query_block_data(session, block)
        #     return data_list
        return block_list


def query_block_avg(block, session):
    print(block.stocks)
    for stock in block.stocks:
        print(stock.k_data_daily[0])
    data_list = session.query(
        KDataDaily.date,
        func.avg(KDataDaily.close)
    ).filter(and_(
        KDataDaily.stock_id == stock_block_table.c.stock_id,
        block.id == stock_block_table.c.block_id
    )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
    print(data_list)



def query_yearly_net_profit():
    with SQLAlchemy.session_context() as session:
        data_list = session.query(
            Stock.name,
            func.sum(StockInfo.net_profit)
        ).filter(
            Stock.id == StockInfo.stock_id,
        ).group_by(StockInfo.stock_id).all()
    for data in data_list:
        if data[1] > 0:
            print(data[0])

def sql_delete():
    with SQLAlchemy.session_context() as session:


        stmt = delete(QuoteDaily).where(QuoteDaily.product_id == 8582)
        result = session.execute(stmt)
        session.commit()
        print(f"delete QuoteDaily data: {result.rowcount}")
        stmt = delete(QuoteWeekly).where(QuoteWeekly.product_id == 8582)
        result = session.execute(stmt)
        session.commit()
        print(f"delete QuoteWeekly data: {result.rowcount}")
        stmt = delete(QuoteMonthly).where(QuoteMonthly.product_id == 8582)
        result = session.execute(stmt)
        session.commit()
        print(f"delete QuoteMonthly data: {result.rowcount}")
        stmt = delete(QuoteHourly).where(QuoteHourly.product_id == 8582)
        result = session.execute(stmt)
        session.commit()
        print(f"delete QuoteHourly data: {result.rowcount}")


        stmt = delete(Product).where(Product.id == 8582)
        result = session.execute(stmt)
        session.commit()
        print(f"delete QuoteDaily data: {result.rowcount}")
        print(f"delete quote data success")


def sql_delete_quote():
    with SQLAlchemy.session_context() as session:
        exg_list = session.query(Exchange).filter((Exchange.code == "SH") |
                                                  (Exchange.code == "SZ") |
                                                  (Exchange.code == "HK") |
                                                  (Exchange.code == "GI") |
                                                  (Exchange.code == "HKI")).all()
        for exg in exg_list:
            product_list = exg.products
            for product in product_list:
                stmt = delete(QuoteDaily).where((QuoteDaily.product_id == product.id) &
                                                (QuoteDaily.time>"2026-03-15"))
                result = session.execute(stmt)
                session.commit()
                print(product)
                print(f"delete QuoteDaily data: {result.rowcount}")

                stmt = delete(QuoteWeekly).where((QuoteWeekly.product_id == product.id) &
                                                (QuoteWeekly.time>"2026-03-08"))
                result = session.execute(stmt)
                session.commit()
                print(product)
                print(f"delete QuoteWeekly data: {result.rowcount}")

def sql_delete_quote_future():
    with SQLAlchemy.session_context() as session:
        market_list = session.query(TdxMarket).filter((TdxMarket.sname == "QS") |
                                          (TdxMarket.sname == "CZ") |
                                          (TdxMarket.sname == "QG") |
                                          (TdxMarket.sname == "QZ") | 
                                          (TdxMarket.sname == "QD")).all()
        for mrk in market_list:
            if mrk.id != 20:
                print(mrk)
                continue
            print(mrk)
            product_list = mrk.products
            for prod in product_list:
                print(prod)
                # stmt = delete(QuoteHourly).where((QuoteHourly.product_id == prod.id) &
                #                                 (QuoteHourly.time>="2026-03-16 00:00:00") &
                #                                 (QuoteHourly.time<="2026-03-20 23:59:00") &
                #                                 (QuoteHourly.id>4839544))
                # result = session.execute(stmt)
                # print(result.rowcount)
                # session.commit()


def future_quote_hourly_update_v2():
    product_id = None
    is_done = True
    with SQLAlchemy.session_context() as session:
        data_list = session.query(QuoteHourly).filter(
            (QuoteHourly.product_id == 61) &
            (QuoteHourly.time >= "2026-03-13 00:00:00") &
            (QuoteHourly.time <= "2026-03-23 15:00:00")
        ).all()
        i=0
        while i < len(data_list):
            print(data_list[i].time)
                
            if data_list[i].time.hour == 22:
                temp = i-7
                time_base = data_list[temp].time
                print("time Base: %s" % time_base)
                time = datetime(time_base.year, time_base.month, time_base.day, 22)
                data_list[i].time = time
                print(data_list[i])
                session.commit()
            if data_list[i].time.hour == 23:
                temp = i-8
                time_base = data_list[temp].time
                print("time Base: %s" % time_base)
                time = datetime(time_base.year, time_base.month, time_base.day, 23)
                data_list[i].time = time
                print(data_list[i])
                session.commit()
            i += 1        


def future_quote_hourly_update():
    product_id = None
    is_done = True
    with SQLAlchemy.session_context() as session:
        market_list = session.query(TdxMarket).filter((TdxMarket.sname == "QS") |
                                        #   (TdxMarket.sname == "CZ") |
                                          (TdxMarket.sname == "QG") |
                                          (TdxMarket.sname == "QZ") | 
                                          (TdxMarket.sname == "QD")).all()

        for mrk in market_list:
            product_list = mrk.products
            for prod in product_list:
                if is_done and product_id:
                    if prod.id == product_id:
                        is_done = False
                    continue
                data_list:list[QuoteHourly] = prod.quote_hourly
                i=0
                
                while i < len(data_list):
                    print(data_list[i].time)
                        
                    if data_list[i].time.hour == 22:
                        temp = i-7
                        time_base = data_list[temp].time
                        print("time Base: %s" % time_base)
                        time = datetime(time_base.year, time_base.month, time_base.day, 22)
                        data_list[i].time = time
                        print(data_list[i])
                        # session.commit()
                    if data_list[i].time.hour == 23:
                        temp = i-8
                        time_base = data_list[temp].time
                        print("time Base: %s" % time_base)
                        time = datetime(time_base.year, time_base.month, time_base.day, 23)
                        data_list[i].time = time
                        print(data_list[i])
                        # session.commit()

                    i += 1
                    # session.commit() 4831759
                # for data in data_list:
                #     data.time
                # def data_time_fix(data:str):
                #     value = pd.to_datetime(data, format='%Y-%m-%d %H:%M')
                #     if (value.hour>19) and ((value.hour<23) or ((value.hour==23) and (value.minute<=59))):
                #         days = 1
                #         while True:
                #             temp_time_str = (value - timedelta(days=days)).strftime('%Y-%m-%d')
                #             temp_time_end = temp_time_str + " 16:00"
                #             tmep_time_start = temp_time_str + " 09:00"
                #             temp_df = data_df[(data_df['datetime']>tmep_time_start) & (data_df['datetime']<temp_time_end)]
                #             if len(temp_df) == 0:
                #                 temp_df_2 = data_df[data_df['datetime']<tmep_time_start]
                #                 if len(temp_df_2) > 0:
                #                     days += 1
                #                     continue
                #                 else:
                #                     return (value - timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
                #             else:
                #                 ret_str = "%s %02d:%02d" % (temp_time_str, value.hour, value.minute)
                #                 return  ret_str
                #     else:
                #         return data



                # data_df.loc[:,'datetime'] = data_df['datetime'].apply(data_time_fix)

if __name__ == '__main__':
    future_quote_hourly_update_v2()
    # sql_delete()
    # # SQLAlchemy.create_all()
    # block_list = query_test()
    # print(block_list)
    pass