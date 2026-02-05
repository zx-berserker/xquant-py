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
from requests.cookies import cookiejar_from_dict
from quant.spider.east_money.lib.future import futures_hist_separate_char_and_numbers_em
from quant.spider.east_money.lib.enum import QuotePeriodEnum
from quant.spider.proxy import Proxy
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
import time
import random
from enum import Enum
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.common.by import By
from uuid import uuid4
from datetime import datetime
import pytz
import json
import string
from quant.libs.log import XLog
from requests.exceptions import ProxyError, ConnectionError
requests.packages.urllib3.disable_warnings()


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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/4.7.5.607",

        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36 OPR/37.0.2178.32",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.7444.163 Safari/537.36",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    cookie_list = [
        "qgqp_b_id=7a654dce469595d63c239f8a186da2c5; st_nvi=hy4CjL0maK9_L7TO8UDQF8e6f; nid=08212e030f8dcf1093e7b2706e9f2395; nid_create_time=1763618845495; gvi=mBwhlehsew6qP6zaXmWeD733a; gvi_create_time=1763618845495; fullscreengg=1; fullscreengg2=1; st_si=33817765259037; st_asi=delete; st_pvi=09053031056644; st_sp=2025-02-05%2016%3A44%3A19; st_inirUrl=https%3A%2F%2Fwww.quark.cn%2Fs; st_sn=5; st_psi=2025112211260529-113200301321-2641464082",

        "qgqp_b_id=62e88c2810b2f67ce5ad3d27f8d50180; st_nvi=kiEAwv2FW_01TCVU8vP14d6f1; nid=0079606ee4b07ac33ed6c7ca3ed27448; nid_create_time=1763643208663; gvi=F0QESwKEYZe0JoSFt4Bi32d19; gvi_create_time=1763643208663; fullscreengg=1; fullscreengg2=1; st_si=30226599063509; st_asi=delete; st_pvi=53849561874186; st_sp=2025-11-12%2000%3A51%3A05; st_inirUrl=https%3A%2F%2Fquote.eastmoney.com%2Fcenter%2F; st_sn=2; st_psi=20251122112753879-113200301321-4144009028",
        
        "qgqp_b_id=fc3523bc4cbc62c5e226579a9572bc36; mtp=1; ct=S3CBifg2nAIkVo1evwtQGvo_Dp2EGaZIVtH1S0KAQ_zU9O0E399Qa4nmsIljHyGJS_2WwuhR8t2UGf-G9gPMihf9PCql3CYlbO5Xozn6qzvLDAKWo-prokrloslNnjRogpRpmZx4bfvM1h0T0dYh87RIpWpg3LEIzyyCGof7Jpc; ut=FobyicMgeV5FJnFT189SwOKxCW_mzjtHOZ-3FmetsJQFrvewoIprkb7jrW14iVQQfHobNRD09SFMqTB0MXSyXKj2b67ZVEiXxOqa2o4kvPyqy8-81JITYTWRpgZujcX1ksq7X6UA4AOOrVSWcKkZccjnQR1n1xnP-iPwtSID9X27-8phx__44-Mc6iQzax9oW54w_55d8iuEjgMhb9NTnF3fiZNYkDWKPSZTpKo6mx1PubQdrJ5v9QCNRQEUXF4F2b_sDLtFYtOnBfn_pAyv3bA9lTDbdWd3JgHCtZVIAlPWtODi6N4S9SkQjS-C2QD4ii1k0IukEXeu92CmA7MBAX3YPQJkhLTc; pi=2891325918534546%3Bh2891325918534546%3B%E5%8D%A1%E5%8D%A1%E9%A3%8E%E8%A1%8C%3BIYwDyUx36yvoeTT03AZSwtYYMBxC5PauLf9W%2BEyAWetpGPsPPYRJEF1e%2FdbWEJhQIThgac8JFVRBzP%2Bmw%2F7nA1I2qe8x5dOMWs5KG93idcjWDsu9NSbEh0RTjjin%2BrZN5lEhbzxRZoTg%2FBP7UPEuEFHlRC3fC%2BnS8YIP5oWJUU%2FMLtkLlA5rSSZDp%2BxwvXhh6n9AWZL4%3Bd68xzLca5tBqvoAVd33Fy2bVc%2F3Fq78soovq6Dmx4PCQMcKb2ZxTCVLa0JDQ7sOMfrn%2FHfFbocnJ8NnQvd8MGGT1gKex655xxBsNYkgCcWgUa5uwVWtjqxQggzgmdQmHFFi4%2BJgPk7WaAyUIOOqjV%2BRHexNuhw%3D%3D; uidal=2891325918534546%e5%8d%a1%e5%8d%a1%e9%a3%8e%e8%a1%8c; sid=147388007; vtpst=|; st_nvi=k9EB8ozpOImfqP6H3nZ8e2ad4; nid=022fec53718dbd1096ad69ba576717db; nid_create_time=1758610260105; gvi=6nA9s-fuEz7iUiKgFFHou03c4; gvi_create_time=1758610260105; st_si=37769056008617; st_pvi=45026247283244; st_sp=2024-12-25%2016%3A29%3A24; st_inirUrl=https%3A%2F%2Fcn.bing.com%2F; st_sn=1; st_psi=202511201326586-111000300841-8018935887; st_asi=delete; websitepoptg_api_time=1763616418574; fullscreengg=1; fullscreengg2=1",
    ]

    session_cookie_dic = {
        "qgqp_b_id":  "",
        # "nid":  "",
        # "nid_create_time":  "0",
        # "gvi":  "",
        # "gvi_create_time":  "0",
        "fullscreengg":  "1",
        # "st_nvi":  "OYr0Yw962KjbKJtoHW84jbe69",
        "st_psi":  "20251124211800282-111000300841-7232565488",
        "st_asi":  "delete",
        "st_pvi":  "10082738244952",
        "st_inirUrl":  "https%3A%2F%2Fwww.eastmoney.com%2F",
    }

    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Connection": "keep-alive",
            "Cookie": "",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Sec-Ch-Ua":  '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
            # "Sec-Ch-Ua": '"Not?A_Brand";v="99", "Chromium";v="130"',
            # "Sec-Ch-Ua-Platform": "Windows",
    }

    class PrepareTypeEnum(Enum):
        DEFAULT = 1
        SESSION = 2
        PROXY = 3
        SESSION_PROXY = 4

    sleep_time = 3

    request_proxies_list = None 

    while_max_count = 20

    session = None

    prepare_type = PrepareTypeEnum.DEFAULT

    request_count = 0

    session_request_count_max = 100
   
    # session_proxy_list = None
    proxy_list = None

    proxy = None

    # session_proxy = None

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
        cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
        cls.headers["Cookie"] = random.choice(cls.cookie_list)
        current_access = random.choice(cls.access_points_list)
        r = requests.get(cls.product_url_base, headers=cls.headers, timeout=10, params=cls.stock_url_params)#, proxies=current_access)
        data_json = r.json()
        total = data_json["data"]["total"]
        loop = - int(-total // size)
        for num in range(1, loop+1):
            if(num <= index):
                continue
            cls.stock_url_params["pn"] = num
            r = requests.get(cls.product_url_base, headers=cls.headers, timeout=10, params=cls.stock_url_params)#, proxies=current_access)
            data_json = r.json()
            if data_json["data"]["diff"]:
                temp_df = pd.DataFrame(data_json["data"]["diff"])
                temp_df = temp_df[["f12", "f14"]]
                temp_df.columns = ["code", "name"]
                yield temp_df
            XLog.info("get_stock_next: num:%d" % (num))
            time.sleep(random.uniform(1,cls.sleep_time))
        

    @classmethod 
    def _get_stock(cls, fs:StockUrlFsEnum, size:int=20) -> pd.DataFrame:
        data_list = []
        cls.stock_url_params["pz"] = size
        cls.stock_url_params["fs"] = fs.value
        cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
        cls.headers["Cookie"] = random.choice(cls.cookie_list)
        r = requests.get(cls.product_url_base, timeout=15, params=cls.stock_url_params, headers=cls.headers)
        data_json = r.json()
        total = data_json["data"]["total"]
        loop = - int(-total // size)
        for num in range(1, loop+1):
            cls.stock_url_params["pn"] = num
            r = requests.get(cls.product_url_base, timeout=15, params=cls.stock_url_params, headers=cls.headers)
            data_json = r.json()
            if data_json["data"]["diff"]:
                data_list.extend(data_json["data"]["diff"])
            time.sleep(random.uniform(1,cls.sleep_time))
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
            XLog.info(type(item["mktid"]))
            exchg_list.append({
                "name": item["mktname"],
                "code": item["mktshort"],
                "east_money_code": item["mktid"],
            })
        exchg_list.extend([
            {
                "name": "上海证券交易所",
                "code": "SH",
                "east_money_code": "1",
            },
            {
                "name": "深证证券交易所",
                "code": "SZ",
                "east_money_code": "0",
            },
            {
                "name": "香港证券交易所",
                "code": "HK",
                "east_money_code": "116",
            },
            {
                "name": "期货指数加权",
                "code": "FI",
                "east_money_code": "159",
            },
            {
                "name": "香港指数",
                "code": "HKI",
                "east_money_code": "124",
            },
            {
                "name": "全球指数",
                "code": "GI",
                "east_money_code": "100",
            },
        ])
        temp_df = pd.DataFrame(exchg_list)
        return temp_df

    @classmethod
    def _proxy_prepare(cls):
        if cls.proxy_list is None or len(cls.proxy_list) <= 1:
            cls.proxy_list = Proxy.get_proxy()
            if len(cls.proxy_list) == 0:
                raise XException(ErrorCodeEnum.CODE_INVALID, "cls.session_proxy_list len 0!")

        if cls.proxy:
            try:
                cls.proxy_list.remove(cls.proxy)
            except Exception as e:
                pass
        
        cls.proxy = random.choice(cls.proxy_list)
        XLog.info("session_proxy: ", cls.proxy)


    @classmethod
    def _session_prepare(cls):
        cls.session_request_count_max = random.randint(70,101)
        cls.request_count = 0
       
        time_zone = pytz.timezone("Asia/Shanghai")
        is_first = True
        user_agent_list = cls.user_agent_list.copy()
        if cls.session:
            is_first = False
            old_user_agent = cls.headers["User-Agent"]
            cls.session.close()
            user_agent_list.remove(old_user_agent)
        
        cls.session = requests.Session()
        if cls.prepare_type == cls.PrepareTypeEnum.SESSION_PROXY:
            if cls.proxy is None: 
                cls._proxy_prepare()
            cls.session.proxies = {
                "http": cls.proxy,
                "https": cls.proxy
            }


        random.shuffle(user_agent_list)
        user_agent = random.choice(user_agent_list)

        chrom_options = ChromeOptions()

        if cls.prepare_type == cls.PrepareTypeEnum.SESSION_PROXY:
            chrom_options.add_argument(f"--proxy-server={cls.proxy}")
        chrom_options.add_argument(f'--user-agent={user_agent}')
        chrom_options.add_argument('--headless')
        chrom_options.add_argument('--no-sandbox')
        chrom_options.add_argument('--disable-dev-shm-usage')
        chrom_options.add_argument('--disable-gpu')
        chrom_options.add_argument('blink-settings=imagesEnabled=false')
        chrom_options.add_argument("--disable-blink-features=AutomationControlled")
        driver = Chrome(options=chrom_options)
        driver.delete_all_cookies()
        tz_params = {"timezoneId": "Asia/Shanghai"}
        driver.execute_cdp_cmd("Emulation.setTimezoneOverride", tz_params)
        driver.set_window_size(1280,1024)
        try:
            driver.get("https://www.eastmoney.com/")
            driver.get("https://data.eastmoney.com/center/")
            driver.get("https://js1.eastmoney.com/tg.aspx?ID=666")
            while_count = 0
            while True:
                while_count += 1
                try:
                    WebDriverWait(driver, 10, 0.5).until(Expect.presence_of_all_elements_located((By.CLASS_NAME, "quotetable")))
                except Exception as e:
                    if while_count > 2:
                        break
                    driver.refresh()
                    XLog.info("session prepare while: diver.refresh().")
                    continue

                break
            # driver.get("https://quote.eastmoney.com/unify/r/220.IFM0")
        except Exception as e:
            pass

        cookie_list = driver.get_cookies()
        cookies_dic = {}
        for item in cookie_list:
            cookies_dic[item["name"]] = item["value"]
        try:
            driver.close()
            driver.quit()
        except Exception as e:
            pass 


        cls.session_cookie_dic["qgqp_b_id"] = uuid4().hex
        cls.session_cookie_dic["st_si"] = cookies_dic["st_si"] if "st_si" in cookies_dic.keys() else "".join(random.choices(string.digits, k=14))
        cls.session_cookie_dic["st_pvi"] = cookies_dic["st_pvi"] if "st_pvi" in cookies_dic.keys() else "".join(random.choices(string.digits, k=14))
        cls.session_cookie_dic["st_sp"] = cookies_dic["st_sp"] if "st_sp" in cookies_dic.keys() else "2025-11-30%2011%3A18%3A04"
        cls.session_cookie_dic["st_sn"] = cookies_dic["st_sn"] if "st_sn" in cookies_dic.keys() else "4"
        cls.session_cookie_dic["st_psi"] = cookies_dic["st_psi"] if "st_psi" in cookies_dic.keys() else "20260204092538939-111000300841-7573842112"


        is_webreport = True

        try:
            cookies_str = f'st_nvi={cookies_dic["st_nvi"]}; st_si={cookies_dic["st_si"]}; st_pvi={cookies_dic["st_pvi"]}; st_sp={cookies_dic["st_sp"]}; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn={cookies_dic["st_sn"]}; st_psi={cookies_dic["st_psi"]}; st_asi=delete'
        except Exception as e:
            XLog.error("webreport False: ", e)
            is_webreport = False

        if is_webreport:
            
            cls.session.cookies = cookiejar_from_dict(cookies_dic)
            post_data = {
                "language": "en-US",
                "osPlatform": "Windows",
                "osversion": random.choice(["Windows 11.0"]),#, "Windows 10.0"]),
                "sourceType": "WEB",
                "timezone": "Asia/Shanghai",
                "webDeviceInfo": {
                    "audioKey": "a61464ca0f67bdaa8cf294de7b437683",
                    "canvasKey": uuid4().hex,#random.choice(["c981719e4e77cf5b910fddd8c191eb12", "e72da4da63126e50d1d5f0a1ab8d9e25", "2e0f704e44ca7960f773b2110529b207"]),
                    "fontKey": uuid4().hex,#random.choice(["db5e1106a88dc36d7c2232d56f5860b8", "3c7a7a335f3759cc33eba1f7678273a6", "eb632a995381636315e72de09b9d4800"]),
                    "screenResolution": random.choice(["1920X1080","1440X900","2560X1440"]),
                    "userAgent": user_agent,
                    "webglKey": uuid4().hex,#random.choice(["a1c5634935c4a76d244a7c9e5512e47e", "083be770488749cf1a9c9cb736743634"]),
                }
            }
            headers = cls.headers.copy()
            headers["User-Agent"] = user_agent
            headers["Content-Type"] = "application/json;charset=UTF-8"
            # headers["Cookie"] = "qgqp_b_id=b6ccb39d04cdd2d405676c56f1c00556; st_nvi=FRj1JN9GJ9pppk8KsLrVrb4aa; st_si=00488073912412; st_pvi=99466061288518; st_sp=2025-11-25%2000%3A43%3A13; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn=51; st_psi=20251125004313487-111000300841-0269590838; st_asi=delete"
            headers["Cookie"] = cookies_str 

            json_data = json.dumps(post_data)
            post_res = cls.session.post("https://anonflow2.eastmoney.com/backend/api/webreport", headers=headers, data=json_data, verify=False)
            if  post_res.status_code != 200:
                raise XException(ErrorCodeEnum.CODE_WEB_REQUEST_ERROR, "prepare session post error.")
            
            res_dic = post_res.json()
            if (not res_dic["data"]) or (not res_dic["data"]["gvi"]) or (not res_dic["data"]["nid"]):
                raise XException(ErrorCodeEnum.CODE_WEB_REQUEST_ERROR, "prepare session post error.")

            cls.session_cookie_dic["gvi_create_time"] = str(int(datetime.now().astimezone(time_zone).timestamp() * 1000))
            cls.session_cookie_dic["nid_create_time"] = str(int(datetime.now().astimezone(time_zone).timestamp() * 1000))
            cls.session_cookie_dic["gvi"] = res_dic["data"]["gvi"]
            cls.session_cookie_dic["nid"] = res_dic["data"]["nid"]
            cls.session_cookie_dic["st_nvi"] = cookies_dic["st_nvi"]
            

        cls.session.cookies = cookiejar_from_dict(cls.session_cookie_dic)
        cls.headers["User-Agent"] = user_agent
        try:
            cls.headers.pop("Cookie")
        except:
            pass
        cls.session.headers = cls.headers
        XLog.info("user-agent:", user_agent)
        XLog.info("cookies:", cls.session_cookie_dic)
    
    @classmethod   
    def prepare(cls, type:PrepareTypeEnum=PrepareTypeEnum.DEFAULT):
        cls.prepare_type = type
        while_count = 0
        if type == ProductQuery.PrepareTypeEnum.DEFAULT:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "param type invalid.")
        while True:
            while_count += 1
            try:
                if type == ProductQuery.PrepareTypeEnum.PROXY:
                    cls._proxy_prepare()
                elif type == ProductQuery.PrepareTypeEnum.SESSION:
                    cls._session_prepare()
                elif type == ProductQuery.PrepareTypeEnum.SESSION_PROXY:
                    cls._proxy_prepare()
                    cls._session_prepare()
            except (Exception, XException) as e:
                XLog.error("error prepare: %s count:%d" % (type.name, while_count))
                # if while_count > 3:
                #     raise e
                continue
            
            break

    
    @classmethod
    def _request_loop(cls, url:str, symbol:str, params:dict):
        wh_count = 0
        sleep_time_base = 5
        while(True):
            try: 
                if cls.prepare_type == ProductQuery.PrepareTypeEnum.PROXY and cls.proxy:
                    cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
                    cls.headers["Cookie"] = ""
                    current_access = {
                        "http": cls.proxy,
                        "https": cls.proxy
                    }
                    r = requests.get(url, headers=cls.headers, timeout=10, params=params, proxies=current_access, verify=False)
                elif cls.session and (cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION or cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY):
                    r = cls.session.get(url, timeout=10, params=params, verify=False)
                else: 
                    cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
                    cls.headers["Cookie"] = random.choice(cls.cookie_list)
                    r = requests.get(url, headers=cls.headers, timeout=10, params=params)
                data_json = r.json()
                return data_json
            except (ProxyError, ConnectionError) as e:
                XLog.error("%s requests.get while() except:" % (symbol))
                XLog.error(e)
                cls.prepare(cls.prepare_type)                 
            except Exception as e:
                wh_count += 1
                XLog.error("%s requests.get while(%d) except:" % (symbol, wh_count))
                XLog.error(e)
                if cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION:
                    sleep_time = random.uniform(sleep_time_base*wh_count, sleep_time_base*(wh_count+1))
                    if wh_count > cls.while_max_count or sleep_time > 120:
                        raise XException(ErrorCodeEnum.CODE_WEB_REQUEST_ERROR, "get_product_quote: web request error!")
                    time.sleep(sleep_time)
                    sleep_time_base += sleep_time
                    cls.prepare(cls.prepare_type)
                    continue
                if (cls.prepare_type == ProductQuery.PrepareTypeEnum.PROXY
                    or (cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY and wh_count > 1)):
                    cls.prepare(cls.prepare_type)
                    continue
                if cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY:
                    try:                   
                        cls._session_prepare()
                    except:
                        cls.prepare(cls.prepare_type)
                continue
        


    @classmethod
    def get_product_quote(cls,
        symbol:str = "0.600000", 
        period:QuotePeriodEnum=QuotePeriodEnum.DAILY, 
        start_date:str="20060101", 
        end_date:str="20500101",
        limit:int = 10000
    ) -> pd.DataFrame:
        
        if (cls.prepare_type == cls.PrepareTypeEnum.SESSION or  cls.prepare_type == cls.PrepareTypeEnum.SESSION_PROXY) and cls.request_count > cls.session_request_count_max:
            while True:
                try:
                    cls._session_prepare()
                except:
                    continue
                break


            
        params = {
            "secid": symbol,
            "klt": period.value,
            "fqt": "0",
            "lmt": str(limit),
            "beg": start_date,
            "end": end_date,
            "iscca": "1",
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "forcect": "1",
        }
        

        # wh_count = 0
        # sleep_time_base = 5
        # while(True):
        #     try: 
        #         if cls.prepare_type == ProductQuery.PrepareTypeEnum.PROXY and cls.proxy:
        #             cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
        #             cls.headers["Cookie"] = ""
        #             current_access = {
        #                 "http": cls.proxy,
        #                 "https": cls.proxy
        #             }
        #             r = requests.get(cls.quote_url_base, headers=cls.headers, timeout=10, params=params, proxies=current_access, verify=False)
        #         elif cls.session and (cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION or cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY):
        #             r = cls.session.get(cls.quote_url_base, timeout=10, params=params, verify=False)
        #         else: 
        #             cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
        #             cls.headers["Cookie"] = random.choice(cls.cookie_list)
        #             r = requests.get(cls.quote_url_base, headers=cls.headers, timeout=10, params=params)
        #         data_json = r.json()
        #     except (ProxyError, ConnectionError) as e:
        #         XLog.error("%s requests.get while() except:" % (symbol))
        #         XLog.error(e)
        #         cls.prepare(cls.prepare_type)
        #         continue
        #     except Exception as e:
        #         wh_count += 1
        #         XLog.error("%s requests.get while(%d) except:" % (symbol, wh_count))
        #         XLog.error(e)
        #         if cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION:
        #             sleep_time = random.uniform(sleep_time_base*wh_count, sleep_time_base*(wh_count+1))
        #             if wh_count > cls.while_max_count or sleep_time > 120:
        #                 raise XException(ErrorCodeEnum.CODE_WEB_REQUEST_ERROR, "get_product_quote: web request error!")
                
        #             time.sleep(sleep_time)
        #             sleep_time_base += sleep_time
        #             cls.prepare(cls.prepare_type)
        #             continue

        #         if (cls.prepare_type == ProductQuery.PrepareTypeEnum.PROXY
        #             or (cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY and wh_count > 1)):
        #             cls.prepare(cls.prepare_type)
        #             continue
        #         if cls.prepare_type == ProductQuery.PrepareTypeEnum.SESSION_PROXY:
        #             try:                   
        #                 cls._session_prepare()
        #             except:
        #                 cls.prepare(cls.prepare_type)
        #         continue

        #     break
        data_json = cls._request_loop(cls.quote_url_base, symbol, params)
        
        try: 
            klines = data_json["data"]["klines"]
        except:
            klines = []
        
        temp_df = pd.DataFrame([item.split(",") for item in klines])
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
        temp_df["open"] = pd.to_numeric(temp_df["open"], errors="coerce")
        temp_df["close"] = pd.to_numeric(temp_df["close"], errors="coerce")
        temp_df["high"] = pd.to_numeric(temp_df["high"], errors="coerce")
        temp_df["low"] = pd.to_numeric(temp_df["low"], errors="coerce")
        temp_df["volume"] = pd.to_numeric(temp_df["volume"], errors="coerce")
        temp_df["amount"] = pd.to_numeric(temp_df["amount"], errors="coerce")
        temp_df["pct_chg"] = pd.to_numeric(temp_df["pct_chg"], errors="coerce")
        temp_df["turn"] = pd.to_numeric(temp_df["turn"], errors="coerce")
        temp_df["hold"] = pd.to_numeric(temp_df["hold"], errors="coerce")
        
        cls.request_count += 1
        return temp_df
    
    @classmethod
    def get_hk_stock_financial_info(cls, symbol:str, use_mapping=False) -> pd.DataFrame:
        if cls.prepare_type == cls.PrepareTypeEnum.SESSION and cls.request_count > cls.session_request_count_max:
            cls._session_prepare()

        url = 'https://datacenter.eastmoney.com/securities/api/data/v1/get'
        params = {
            'reportName': 'RPT_CUSTOM_HKF10_FN_MAININDICATORMAX',
            'columns': 'ORG_CODE,SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,SECURITY_INNER_CODE,REPORT_DATE,BASIC_EPS,'
                       'PER_NETCASH_OPERATE,BPS,BPS_NEDILUTED,COMMON_ACS,PER_SHARES,ISSUED_COMMON_SHARES,HK_COMMON_SHARES,'
                       'TOTAL_MARKET_CAP,HKSK_MARKET_CAP,OPERATE_INCOME,OPERATE_INCOME_SQ,OPERATE_INCOME_QOQ,'
                       'OPERATE_INCOME_QOQ_SQ,HOLDER_PROFIT,HOLDER_PROFIT_SQ,HOLDER_PROFIT_QOQ,HOLDER_PROFIT_QOQ_SQ,PE_TTM,'
                       'PE_TTM_SQ,PB_TTM,PB_TTM_SQ,NET_PROFIT_RATIO,NET_PROFIT_RATIO_SQ,ROE_AVG,ROE_AVG_SQ,ROA,'
                       'ROA_SQ,DIVIDEND_TTM,DIVIDEND_LFY,DIVI_RATIO,DIVIDEND_RATE,IS_CNY_CODE',
            'quoteColumns': '',
            'filter': f'(SECUCODE="{symbol}.HK")',
            'pageNumber': '1',
            'pageSize': '200',
            'sortTypes': '-1',
            'sortColumns': 'REPORT_DATE',
            'source': 'F10',
            'client': 'PC',
            'v': '07945646099062258'
        }
        # cls.headers["User-Agent"] = random.choice(cls.user_agent_list)
        # cls.headers["Cookie"] = random.choice(cls.cookie_list)
        # r = requests.get(url, headers=cls.headers, timeout=10, params=params)
        # data_json = r.json()
        data_json = cls._request_loop(url, symbol, params)
        cls.request_count += 1
        try:
            temp_df = pd.DataFrame(data_json['result']['data'])
        except Exception:
            return pd.DataFrame()
        
        if use_mapping:
            field_mapping = {
                'SECURITY_CODE': '股票代码',
                'BASIC_EPS': '基本每股收益(元)',
                'BPS': '每股净资产(元)',
                'COMMON_ACS': '法定股本(股)',
                'PER_SHARES': '每手股',
                'DIVIDEND_TTM': '每股股息TTM(港元)',
                'DIVI_RATIO': '派息比率(%)',
                'ISSUED_COMMON_SHARES': '已发行股本(股)',
                'HK_COMMON_SHARES': '已发行股本-H股(股)',
                'PER_NETCASH_OPERATE': '每股经营现金流(元)',
                'DIVIDEND_RATE': '股息率TTM(%)',
                'TOTAL_MARKET_CAP': '总市值(港元)',
                'HKSK_MARKET_CAP': '港股市值(港元)',
                'OPERATE_INCOME': '营业总收入',
                'OPERATE_INCOME_QOQ': '营业总收入滚动环比增长(%)',
                'NET_PROFIT_RATIO': '销售净利率(%)',
                'HOLDER_PROFIT': '净利润',
                'HOLDER_PROFIT_QOQ': '净利润滚动环比增长(%)',
                'ROE_AVG': '股东权益回报率(%)',
                'PE_TTM': '市盈率',
                'PB_TTM': '市净率',
                'ROA': '总资产回报率(%)'
            }
            temp_df.rename(columns=field_mapping, inplace=True)
            temp_df = temp_df[[
                "基本每股收益(元)",
                "每股净资产(元)",
                "法定股本(股)",
                "每手股",
                "每股股息TTM(港元)",
                "派息比率(%)",
                "已发行股本(股)",
                "已发行股本-H股(股)",
                "每股经营现金流(元)",
                "股息率TTM(%)",
                "总市值(港元)",
                "港股市值(港元)",
                "营业总收入",
                "营业总收入滚动环比增长(%)",
                "销售净利率(%)",
                "净利润",
                "净利润滚动环比增长(%)",
                "股东权益回报率(%)",
                "市盈率",
                "市净率",
                "总资产回报率(%)"

            ]]
        return temp_df
    


if __name__ == "__main__":
    # ProductQuery._session_prepare()
    data = ProductQuery.get_future_product()
    data.to_csv('./future.csv')



