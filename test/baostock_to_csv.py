# -*- encoding:utf-8 -*-
"""
date: 2025/06/24 
author: Berserker
"""


from quant.spider.baostock.query_stock_info import QueryStockInfo
import pandas as pd
from quant.tool.baostock import BaoStock

def stocks_to_csv(date="2025-06-23"):
    data_pd = QueryStockInfo.query_all_stock_code(date)
    data_pd.to_csv("./test/cache/baostock_code.csv", index=None)
    
    temp_pd = data_pd[210:5363]
    temp_pd.to_csv("./test/cache/stocks.csv", index=None)


def stock_liqa_value_to_csv():
    stock_pd = pd.read_csv("./test/cache/stocks.csv")
    name_list = []
    code_list = []
    liqa_list = []
    code_error_list = []
    BaoStock.login()
    for index,stock in stock_pd.iterrows():
        print(stock["code"])
        profit_pd = QueryStockInfo.query_stock_profit_data(stock["code"], year=2025, quarter=1)        
        k_data_pa = QueryStockInfo.query_k_data(stock["code"],start_date="2025-05-23",freq_type=QueryStockInfo.FreqTypeEnum.FREQ_MONTHLY)
        if (profit_pd.empty or k_data_pa.empty or profit_pd["liqaShare"][0]=='' or k_data_pa["close"][0]==''):
            code_error_list.append(stock["code"])
            continue
        lv = float(profit_pd["liqaShare"][0]) * float(k_data_pa["close"][0])
        name_list.append(stock["code_name"])
        code_list.append(stock["code"])
        liqa_list.append(lv)
    BaoStock.logout()
    temp_pd =pd.DataFrame({
        "股票名称":name_list,
        "代码":code_list,
        "流通市值":liqa_list
    })
    print(code_error_list)
    temp_pd.to_csv("./test/cache/liqa_value.csv",index=None)



if __name__ == "__main__":
    stock_liqa_value_to_csv()