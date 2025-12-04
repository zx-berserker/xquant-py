# -*- coding:utf-8 -*-
"""
date: 2025/11/10
author: Berserker
"""

import akshare as ak
from quant.libs.enums import ProductTypeEnum

def test_enmus(ntype:ProductTypeEnum):
    print(type(ntype))
    print(type(ntype.value))
    print(ntype.value)


if __name__ == "__main__":
    test_enmus(ProductTypeEnum.PRODUCT_STOCK)


    # futures_hist_em_df = ak.futures_hist_em(symbol="热卷", period="daily")
    """
    https://push2his.eastmoney.com/api/qt/stock/kline/get?klt=102&fqt=0&secid=0.003020&ut=7eea3edcaed734bea9cbfc24409ed989&iscca=1&end=20250101&lmt=1000&forcect=1&fields2=f51,f52,f53,f54,f55,f56,f57,f59,f63&fields1=f1,f2,f3,f4,f5,f6,f7,f8

    "https://push2.eastmoney.com/api/qt/clist/get"
    "https://push2.eastmoney.com/api/qt/clist/get"
    https://push2his.eastmoney.com/api/qt/stock/kline/get?klt=60&fqt=1&secid=159.cufi&ut=7eea3edcaed734bea9cbfc24409ed989&iscca=1&end=20250101&lmt=1000&forcect=1&fields2=f51,f52,f53,f54,f55,f56,f57,f59,f63&fields1=f1,f2,f3,f4,f5,f6,f7,f8

    stock: 1上海，0深证 （secid=1.600000 浦发银行 ）
    """

    """ 香港116
      url = "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
        params = {
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            "iscr": "0",
            "ndays": "5",
            "secid": f"116.{symbol}",
        }

    stock_zh_a_hist_min_em    
    """

    """ 港股
    https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&cb=jQuery371006652507978489475_1762878467777&fs=m%3A116%2Bt%3A3%2Cm%3A116%2Bt%3A4%2Cm%3A116%2Bt%3A1%2Cm%3A116%2Bt%3A2&fields=f12%2Cf13%2Cf14%2Cf19%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf17%2Cf18%2Cf15%2Cf16%2Cf5%2Cf6&fid=f3&pn=1&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=7611027587172892%7C0%7C1%7C0%7Cweb&_=1762878467783
    
    https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&fields=f12,f14&fid=f3&pn=1&po=1&dect=1&fs=m%3A116%2Bt%3A3%2Cm%3A116%2Bt%3A4%2Cm%3A116%2Bt%3A1%2Cm%3A116%2Bt%3A2

    https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&fields=f12,f14&fid=f3&pn=1&po=1&dect=1&pz=20&fs=b:MK0838
    """

    """
    HK m:116+t:3,m:116+t:4
    SH A: m:1+t:2+f:!2,m:1+t:23+f:!2
    SZ A: m:0+t:6+f:!2,m:0+t:80+f:!2

    sh ETF: b:MK0839
    sz ETF: b:MK0840
    hk ETF: b:MK0838

    港股通: b:MK0146,b:MK0144
    新股：m:0+f:8,m:1+f:8
    """


    """
    "f12": "HSI",
    "f13": 100,
    "f14": "恒生指数",


    "f12": "399006",
    "f13": 0,
    "f14": "创业板指",


            "f12": "399001",
            "f13": 0,
            "f14": "深证成指",   

            "f12": "000001",
            "f13": 1,
            "f14": "上证指数",  

            "f12": "000300",
            "f13": 1,
            "f14": "沪深300",

            "f12": "399006",
            "f13": 0,
            "f14": "创业板指",    


            "f12": "N225",
            "f13": 100,
            "f14": "日经225",



            "f12": "KS11",
            "f13": 100,
            "f14": "韩国KOSPI",

            
            "f12": "NDX",
            "f13": 100,
            "f14": "纳斯达克",

            "f12": "SPX",
            "f13": 100,
            "f14": "标普500",


            "f12": "DJIA",
            "f13": 100,
            "f14": "道琼斯",    


        "f12": "HSTECH",
        "f14": "恒生科技指数",   
        "f13": 124,     



        香港指数 124





    """
    # s = r"\u\ "
    # print(s)