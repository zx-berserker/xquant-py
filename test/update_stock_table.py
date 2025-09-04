# -*- encoding:utf-8 -*-
"""
date: 2023/06/11
author: Berserker
"""
from quant.tool.ini_file_reader import IniFileReader
from quant.models.stock import Stock
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.models.industry import Industry
from quant.models.stock import Stock
from quant.tool.database.base import SQLAlchemy
import pandas as pd
from quant.spider.baostock.query_stock_info import QueryStockInfo

def code_formate(code):
    if code[0] == '6':
        return "sh." + code
    else:
        return 'sz.'+ code
    
def code_exist(code, industry_id):
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == code).first()
        if stock is None:
            print(code)
            return False
        else :
            stock.industry_id = industry_id
            session.commit()
            return True

def main_update_stock_table(file_path="./quant/tool/database/file/industry_2025-09-04.ini"):
    reader = IniFileReader(file_path)
    info_dic = reader.get_ini_infos("industry")
    stock_dicts = []
    with SQLAlchemy.session_context() as session:
        industry_list = session.query(Industry).all()
    for industry in industry_list:
        ind_code = industry.code
        stoc_str = info_dic[ind_code]
        sto_code_list = stoc_str.split(',')
        for sto_code in sto_code_list:
            code = code_formate(sto_code)
            is_exist = code_exist(code, industry.id)
            if not is_exist:
                stock_info = QueryStockInfo.query_stock_info(code)
                if not stock_info.empty:
                    stock_dicts.append({
                        'status': 1,
                        'code': code,
                        'name': stock_info.loc[0].values[1],
                        'industry_id': industry.id,
                        '_stock_type': 1
                    })
                else:
                    print("Is None: "+code)
    print(stock_dicts) 
    with SQLAlchemy.session_context() as session:
        session.bulk_insert_mappings(Stock,stock_dicts)
        session.commit()    
      
            

def main_update_industry_table(file_path="./quant/tool/database/file/industry_2025-09-04.ini"):
    SQLAlchemy.create_all()
    reader = IniFileReader(file_path)
    info_dic = reader.get_ini_infos("name")   
    with SQLAlchemy.session_context() as session:
        code_list = []
        q_code_list = session.query(Industry.code).all()
        if len(q_code_list) > 0:
            code_list = [li[0] for li in q_code_list]
        for key in info_dic:
            if key in code_list:
                continue
            industry = Industry(
                name=info_dic[key].replace(';', ''),
                code=key
            )
            session.add(industry)
            session.commit()
            
    
    

if __name__ == '__main__':
    # main_update_stock_table()
    # stock_info = QueryStockInfo.query_stock_info('sz.001366')
    # print(stock_info)
    main_update_stock_table()