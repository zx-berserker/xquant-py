# -*- coding:utf-8 -*-
"""
date: 2025/11/16
author: Berserker
"""

from quant.models import Product, Exchange
from quant.tool.database import SQLAlchemy
from quant.spider.east_money.product_query import ProductQuery, futures_hist_separate_char_and_numbers_em
import pandas as pd
from quant.libs.enums import ProductTypeEnum
import time

def update_exchange():
    # data_df = ProductQuery.get_exchange()
    data_df = pd.DataFrame([
            {
                "name": "香港指数",
                "code": "HKI",
                "east_money_code": 124,
            },
            {
                "name": "全球指数",
                "code": "GI",
                "east_money_code": 100,
            },
    ])

    with SQLAlchemy.session_context() as session:
        for index, row in  data_df.iterrows():
            exg = Exchange(
                code=row["code"],
                name=row["name"],
                east_money_code=row["east_money_code"],
            )
            try:
                session.add(exg)
                session.commit()
            except:
                print("error:")
                print(row)

def update_future_product():
    data_df = ProductQuery.get_future_product()
    with SQLAlchemy.session_context() as session:
        for index, row in  data_df.iterrows():
            exg = session.query(Exchange).filter(
                Exchange.east_money_code == row["ex_east_money_code"] 
            ).first()
            if not exg:
                print("exg error")
                print(row)
            (char, number) = futures_hist_separate_char_and_numbers_em(row["name"])
            if number:
                continue
            prod = Product(
                code=row["code"],
                name=row["name"],
                _type=ProductTypeEnum.PRODUCT_FUTURE.value,
                exchange_id=exg.id
            )
            try:
                session.add(prod)
                session.commit()
                print(prod)
            except:
                print("try error:")
                print(row)

def _db_prouct_update(data_df:pd.DataFrame, exg:Exchange, type:ProductTypeEnum):
    with SQLAlchemy.session_context() as session:
        for index, row in  data_df.iterrows():
            prod = Product(
                code=row["code"],
                name=row["name"],
                _type=type.value,
                exchange_id=exg.id
            )
            try:
                session.add(prod)
                session.commit()
                print(prod)
            except:
                print("try error:")
                print(row)

def update_stock_product(ex_code="SH", ptype:ProductTypeEnum=ProductTypeEnum.PRODUCT_STOCK,index=0):
    data_df = None
    fs = None
    if(ex_code=="SH"):
        if ptype == ProductTypeEnum.PRODUCT_STOCK:
            #  data_df = ProductQuery.get_sh_stock_a()
            # fs = ProductQuery.stock_url_fs["sh_stock_a"]
            fs = ProductQuery.StockUrlFsEnum.SH_STOCK_A
        elif ptype == ProductTypeEnum.PRODUCT_FUND:
            # data_df = ProductQuery.get_sh_stock_etf()
            # fs = ProductQuery.stock_url_fs["sh_stock_etf"]
            fs = ProductQuery.StockUrlFsEnum.SH_STOCK_ETF
    elif(ex_code=="SZ"):
        if ptype == ProductTypeEnum.PRODUCT_STOCK:
            #  data_df = ProductQuery.get_sz_stock_a()
            # fs = ProductQuery.stock_url_fs["sz_stock_a"]
            fs = ProductQuery.StockUrlFsEnum.SZ_STOCK_A
        elif ptype == ProductTypeEnum.PRODUCT_FUND:
            # data_df = ProductQuery.get_sz_stock_etf()
            # fs = ProductQuery.stock_url_fs["sz_stock_etf"]
            fs = ProductQuery.StockUrlFsEnum.SZ_STOCK_ETF
    if(ex_code=="HK"):
        if ptype == ProductTypeEnum.PRODUCT_STOCK:
            #  data_df = ProductQuery.get_hk_stock()
            # fs = ProductQuery.stock_url_fs["hk_stock"]
            fs = ProductQuery.StockUrlFsEnum.HK_STOCK
        elif ptype == ProductTypeEnum.PRODUCT_FUND:
            # data_df = ProductQuery.get_hk_stock_etf()
            # fs = ProductQuery.stock_url_fs["hk_stock_etf"]
            fs = ProductQuery.StockUrlFsEnum.HK_STOCK_ETF
    if not fs:
        return 
    with SQLAlchemy.session_context() as session:
        exg = session.query(Exchange).filter(
            Exchange.code == ex_code
        ).first()
    
    for data_df in ProductQuery.get_stock_next(fs, index):
        _db_prouct_update(data_df, exg, ptype)


def update_product():
    data_list = [
        # {
        #     "f12": "HSI",
        #     "f13": 100,
        #     "f14": "恒生指数",
        # },
        # {
        #     "f12": "399006",
        #     "f13": 0,
        #     "f14": "创业板指",            
        # },
        # {
        #     "f12": "399001",
        #     "f13": 0,
        #     "f14": "深证成指", 
        # },
        {
            "f12": "000001",
            "f13": 1,
            "f14": "上证指数",  
        },
        {
            "f12": "000300",
            "f13": 1,
            "f14": "沪深300",
        },
        {
            "f12": "399006",
            "f13": 0,
            "f14": "创业板指",    
        },
        {
            "f12": "N225",
            "f13": 100,
            "f14": "日经225",
        },
        {
            "f12": "KS11",
            "f13": 100,
            "f14": "韩国KOSPI",
        },
        {
            "f12": "NDX",
            "f13": 100,
            "f14": "纳斯达克",
        },
        {
            "f12": "SPX",
            "f13": 100,
            "f14": "标普500",
        },
        {
            "f12": "DJIA",
            "f13": 100,
            "f14": "道琼斯", 
        },
        {
            "f12": "HSTECH",
            "f14": "恒生科技指数",   
            "f13": 124, 
        },
    ]

    with SQLAlchemy.session_context() as session:
        for data in data_list:
            exg = session.query(Exchange).filter(
                Exchange.east_money_code == data["f13"]
            ).first()
            prd = Product(
                name=data['f14'],
                code=data['f12'],
                exchange_id=exg.id,
                type=ProductTypeEnum.PRODUCT_INDEX
            )
            try:
                session.add(prd)
                session.commit()
            except:
                print(data)



if __name__ == "__main__":
    update_product()

    pass