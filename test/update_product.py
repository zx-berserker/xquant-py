# -*- coding:utf-8 -*-
"""
date: 2025/11/16
author: Berserker
"""

from quant.models import Product, Exchange,TdxMarket
from quant.tool.database import SQLAlchemy
from quant.spider.east_money.product_query import ProductQuery, futures_hist_separate_char_and_numbers_em
import pandas as pd
from quant.libs.enums import ProductTypeEnum
import time
from quant.spider.tdx import TdxQuery

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


def update_tdx_market():
    market_df = pd.read_csv("./quant/tool/database/file/markets.csv")
    with SQLAlchemy.session_context() as session:
        for index, row in  market_df.iterrows():
            market = TdxMarket(
                    code=row["market"],
                    name=row["name"],
                    sname=row["short_name"]
                )
            try:
                session.add(market)
                session.commit()
            except:
                print("%s %d" % (row["name"], index))
                break

def update_future_product_csv():
    future_df = pd.read_csv("./temp_future.csv")
    instrument_df = pd.read_csv("./instrument_info.csv")
    temp_list = []
    for index, row in future_df.iterrows():
        tdx_code = ''
        if '次主连' in row['name']:
            pre_tdx_code = str(row['code'][0:-1]).upper() 
            flex = 'L7'
        elif "主连" in row['name']:
            pre_tdx_code = str(row['code'][0:-1]).upper() 
            flex = 'L8'
        elif "加权" in row['name']:
            pre_tdx_code = str(row['code'][0:-2]).upper() 
            flex = 'L9'
        elif "当月连续" in row['name']:
            pre_tdx_code = str(row['code'][0:-2]).upper() 
            flex = "L0"
        elif "下月连续" in row['name']:
            pre_tdx_code = str(row['code'][0:-2]).upper() 
            flex = 'L1'
        elif "下季连续" in row['name']:
            pre_tdx_code = str(row['code'][0:-2]).upper() 
            flex = 'L2'
        elif "隔季连续" in row['name']:
            pre_tdx_code = str(row['code'][0:-2]).upper() 
            flex = 'L3'
        if pre_tdx_code == "LF":
            tdx_code = 'L-F'+ flex
        elif pre_tdx_code == "PPF":
            tdx_code = 'PP-F'+ flex
        elif pre_tdx_code == "VF":
             tdx_code = 'V-F'+ flex
        elif pre_tdx_code in ["WH", "PM", "RI", "JR"]:
            tdx_code = "*"
        else:
            tdx_code = pre_tdx_code + flex
            if tdx_code in ["TL3", "TFL3", "TSL3", "TLL3"]:
                tdx_code = '*'
        
        if tdx_code == "*":
            tdx_market_code = "*"
        elif pre_tdx_code in["SI", "LC", "PS", "PS", "PT", "PD"]:
            tdx_market_code = "66"
        else:
            tem_row = instrument_df.query("code == @tdx_code")
            tdx_market_code = tem_row['market'].item()

        temp_list.append({
            "code":row['code'],
            "name":row['name'],
            "ex_name": row['ex_name'],
            "ex_east_money_code":row['ex_east_money_code'],
            "tdx_code": tdx_code,
            "tdx_market_code": tdx_market_code,
        })
    temp_df = pd.DataFrame(temp_list)
    temp_df.to_csv('./ret_future.csv',index=False)

def update_future_product():
    future_df = pd.read_csv("./quant/tool/database/file/ret_future.csv")
    for index, row in future_df.iterrows():
        if index < 0:
            continue
        with SQLAlchemy.session_context() as session:
            product = session.query(Product).filter(
                Product.code == row['code']
            ).first()
            market = session.query(TdxMarket).filter(
                TdxMarket.code == row['tdx_market_code']
            ).first()
            if product is None:
                exg = session.query(Exchange).filter(
                    Exchange.east_money_code == row['ex_east_money_code']
                ).first()

                product = Product(
                    code = row['code'],
                    tdx_code = row['tdx_code'],
                    name = row['name'],
                    exchange_id = exg.id,
                    tdx_market_id = market.id if market is not None else None,
                    _type = ProductTypeEnum.PRODUCT_FUTURE.value
                )
                
                session.add(product)
            else:
                product.tdx_code = row['tdx_code']
                product.tdx_market_id = market.id if market is not None else None
            session.commit()
            print("%d %s" % (index, product))


def update_tdx_product():
    market_list = ['9']
    product_type = ProductTypeEnum.PRODUCT_STOCK.value
    for market in market_list:
        market_code = market
        if market_code == "31":
            product_type = ProductTypeEnum.PRODUCT_FUND.value
        elif market_code == '9':
            product_type = ProductTypeEnum.PRODUCT_INDEX.value

        product_list = TdxQuery.get_product_list(market_code)
        with SQLAlchemy.session_context() as session:
            for prod in product_list:
                code = prod['Code']
                name = prod['Name']
                print("product: %s-%s" % (code, name))
                code_list = code.split('.')
                exg_code = code_list[1]
                if exg_code == 'SZ' or exg_code == 'SH':
                    pass
                elif exg_code == 'OT' or exg_code == "HK":
                    exg_code = "HKI"
                else:
                    exg_code = "GI"
                exg = session.query(Exchange).filter(
                    Exchange.code == exg_code
                ).first()
                if exg is None:
                    continue
                product = session.query(Product).filter(
                    (Product.code == code_list[0]) &
                    (Product.exchange_id == exg.id)
                ).first()
                if product:
                    # continue
                    product.tdx_code = code
                    session.commit()
                    print("Update:")
                    print(product)
                else:
                    product = Product(
                        code=code_list[0],
                        tdx_code=code,
                        name=name,
                        exchange_id=exg.id,
                        _type = product_type
                    )
                    session.add(product)
                    session.commit()
                    print("Add Product")


        


if __name__ == "__main__":
    # update_tdx_product()
    a = pd.DataFrame()
    if type(a) == list:
        print("ok")
    pass