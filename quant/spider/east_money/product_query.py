# -*- coding:utf-8 -*-
"""
date: 2025/11/21
author: Berserker
"""

import re
from functools import lru_cache
from typing import Tuple, Dict
import json
import pandas as pd
import requests
from .lib.future import futures_hist_separate_char_and_numbers_em
from .lib.enum import QuotePeriodEnum
import time
import random
from enum import Enum

class ProductQuery(object):
    quote_url_base = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    product_url_base = "https://push2.eastmoney.com/api/qt/clist/get"
    stock_url_params = {
       "np": "1",
       "fltt": "1",
       "invt": "2",
       "pn": "1",
       "po": "1",
       "dect": "1",
       "pz": "20",
       "fields": "f12,f14",
       "fid": "f3",
       "fs": "",
    }
    class StockUrlFsEnum(Enum):
        SH_STOCK_A = "m:1+t:2+f:!2,m:1+t:23+f:!2",
        SZ_STOCK_A = "m:0+t:6+f:!2,m:0+t:80+f:!2",
        HK_STOCK = "m:116+t:3,m:116+t:4",
        SH_STOCK_ETF =  "b:MK0839",
        SZ_STOCK_ETF = "b:MK0840",
        HK_STOCK_ETF = "b:MK0838",
        NEW_STOCK_A = "m:0+f:8,m:1+f:8",
        HK_STOCK_GGT = "b:MK0146,b:MK0144",

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36"
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    ]

    Cookie = "qgqp_b_id=62e88c2810b2f67ce5ad3d27f8d50180; st_nvi=eqhQa5wNEhFs5Vt8-7XVo7cc1; st_si=74782850947529; st_asi=delete; nid=0079606ee4b07ac33ed6c7ca3ed27448; nid_create_time=1763303835067; gvi=H83Ghdne9iRb51_cVy5uzc7a8; gvi_create_time=1763303835067; fullscreengg=1; fullscreengg2=1; wsc_checkuser_ok=1; st_pvi=53849561874186; st_sp=2025-11-12%2000%3A51%3A05; st_inirUrl=https%3A%2F%2Fquote.eastmoney.com%2Fcenter%2F; st_sn=24; st_psi=20251116233737782-113200301321-8630809259"

    sleep_time = 3
    @classmethod
    def get_future_product(cls) -> pd.DataFrame:
        url = "https://futsse-static.eastmoney.com/redis"
        params = {"msgid": "gnweb"}
        r = requests.get(url, params=params)
        data_json = r.json()
        all_exchange_symbol_list = []
        for item in data_json:
            params = {"msgid": str(item["mktid"])}
            r = requests.get(url, params=params)
            inner_data_json = r.json()
            for num in range(1, len(inner_data_json) + 1):
                params = {"msgid": str(item["mktid"]) + f"_{num}"}
                r = requests.get(url, params=params)
                r_data_json = r.json()
                all_exchange_symbol_list.extend(r_data_json)
                if len(r_data_json) > 0:
                    (char, number) = futures_hist_separate_char_and_numbers_em(r_data_json[0]["name"])
                    fi_name = char + "加权"
                    fi_code = r_data_json[0]["vcode"] + "fi"
                    fi_mktid = 159
                    all_exchange_symbol_list.append({
                        "code": fi_code,
                        "mktid": 159,
                        "mktname": "期货指数加权",
                        "mktshort": "FI",
                        "name": fi_name,
                        "vcode": fi_code,
                        "vname": fi_name,
                    })
        temp_df = pd.DataFrame(all_exchange_symbol_list)
        temp_df = temp_df[["code", "name", "mktname", "mktid", "mktshort"]]
        temp_df.columns = ["code", "name", "ex_name", "ex_east_money_code", "ex_code"]
        return  temp_df 
    
    
    @classmethod
    def get_stock_next(cls, fs:StockUrlFsEnum, index:int=0, size:int=20):
        """Use: 
            for data_df in get_stock_next(...):
                pass 
        Args:
            fs (str): eastmoney fs (eg: )
            index (int, optional): 
            size (int, optional): 

        Yields:
            _type_: DateFrame
        """
        cls.stock_url_params["pz"] = size
        cls.stock_url_params["fs"] = fs.value
        headers = {
                "User-Agent": random.choice(cls.user_agent_list),
                "Connection": "close",
                "Cookie": cls.Cookie,
        }
        r = requests.get(cls.product_url_base, headers=headers, timeout=10, params=cls.stock_url_params)
        data_json = r.json()
        total = data_json["data"]["total"]
        loop = - int(-total // size)
        for num in range(1, loop+1):
            if(num <= index):
                continue
            cls.stock_url_params["pn"] = num
            r = requests.get(cls.product_url_base, headers=headers, timeout=10, params=cls.stock_url_params)
            data_json = r.json()
            if data_json["data"]["diff"]:
                temp_df = pd.DataFrame(data_json["data"]["diff"])
                temp_df = temp_df[["f12", "f14"]]
                temp_df.columns = ["code", "name"]
                yield temp_df
            print("get_stock_next: num:%d" % (num))
            time.sleep(cls.sleep_time)
        

    @classmethod 
    def _get_stock(cls, fs:StockUrlFsEnum, size:int=20) -> pd.DataFrame:
        data_list = []
        cls.stock_url_params["pz"] = size
        cls.stock_url_params["fs"] = fs.value
        r = requests.get(cls.product_url_base, timeout=15, params=cls.stock_url_params)
        data_json = r.json()
        total = data_json["data"]["total"]
        loop = - int(-total // size)
        for num in range(1, loop+1):
            cls.stock_url_params["pn"] = num
            r = requests.get(cls.product_url_base, timeout=15, params=cls.stock_url_params)
            data_json = r.json()
            if data_json["data"]["diff"]:
                data_list.extend(data_json["data"]["diff"])
            time.sleep(cls.sleep_time)
        temp_df = pd.DataFrame(data_list)
        temp_df = temp_df[["f12", "f14"]]
        temp_df.columns = ["code", "name"]
        return temp_df
    
    @classmethod
    def get_sh_stock_a(cls) -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.SH_STOCK_A)
    
    @classmethod
    def get_sz_stock_a(cls) -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.SZ_STOCK_A)
    
    @classmethod
    def get_hk_stock(cls) -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.HK_STOCK)
    
    @classmethod
    def get_sh_stock_etf(cls)  -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.SH_STOCK_ETF)

    @classmethod
    def get_sz_stock_etf(cls)  -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.SZ_STOCK_ETF)

    @classmethod
    def get_hk_stock_etf(cls)  -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.HK_STOCK_ETF)

    @classmethod
    def get_new_stock_a(cls)  -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.NEW_STOCK_A)
    
    @classmethod
    def get_hk_stock_ggt(cls)  -> pd.DataFrame:
        return cls._get_stock(cls.StockUrlFsEnum.HK_STOCK_GGT)
    
    @classmethod
    def get_exchange(cls) -> pd.DataFrame:
        url = "https://futsse-static.eastmoney.com/redis"
        params = {"msgid": "gnweb"}
        r = requests.get(url, params=params)
        data_json = r.json()
        exchg_list = []
        for item in data_json:
            exchg_list.append({
                "name": item["mktname"],
                "code": item["mktshort"],
                "east_money_code": item["mktid"],
            })
        exchg_list.extend([
            {
                "name": "上海证券交易所",
                "code": "SH",
                "east_money_code": 1,
            },
            {
                "name": "深证证券交易所",
                "code": "SZ",
                "east_money_code": 0,
            },
            {
                "name": "香港证券交易所",
                "code": "HK",
                "east_money_code": 116,
            },
            {
                "name": "期货指数加权",
                "code": "FI",
                "east_money_code": 159,
            },
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
        temp_df = pd.DataFrame(exchg_list)
        return temp_df
    

    @classmethod
    def get_product_quote(cls,
        symbol:str = "0.600000", 
        period:QuotePeriodEnum=QuotePeriodEnum.DAILY, 
        start_date:str="20060101", 
        end_date:str="20500101",
        limit:int = 10000
    ) -> pd.DataFrame:
        params = {
            "secid": symbol,
            "klt": period.value,
            "fqt": "1",
            "lmt": str(limit),
            "end": end_date,
            "iscca": "1",
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "forcect": "1",
        }
        headers = {
                "User-Agent": random.choice(cls.user_agent_list),
                "Connection": "close",
                "Cookie": cls.Cookie,
        }
        r = requests.get(cls.quote_url_base, headers=headers, timeout=15, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame([item.split(",") for item in data_json["data"]["klines"]])
        if temp_df.empty: return temp_df
        temp_df.columns = [
            "time",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount",
            "-",
            "pct_chg",
            "-",
            "turn",
            "_",
            "hold",
            "_",
        ]
        temp_df = temp_df[
            [
                "time",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "amount",
                "pct_chg",
                "turn",
                "hold",
            ]
        ]
        temp_df.index = pd.to_datetime(temp_df["time"])
        temp_df = temp_df[start_date:end_date]
        temp_df.reset_index(drop=True, inplace=True)
        temp_df["open"] = pd.to_numeric(temp_df["open"], errors="coerce")
        temp_df["close"] = pd.to_numeric(temp_df["close"], errors="coerce")
        temp_df["high"] = pd.to_numeric(temp_df["high"], errors="coerce")
        temp_df["low"] = pd.to_numeric(temp_df["low"], errors="coerce")
        temp_df["volume"] = pd.to_numeric(temp_df["volume"], errors="coerce")
        temp_df["amount"] = pd.to_numeric(temp_df["amount"], errors="coerce")
        temp_df["pct_chg"] = pd.to_numeric(temp_df["pct_chg"], errors="coerce")
        temp_df["turn"] = pd.to_numeric(temp_df["turn"], errors="coerce")
        temp_df["hold"] = pd.to_numeric(temp_df["hold"], errors="coerce")
        return temp_df