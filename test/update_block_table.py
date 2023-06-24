# -*- coding:utf-8 -*-
"""
date: 2023/06/23
author: Berserker
"""
from quant.models.block import Block
from quant.models.stock import Stock
from quant.tool.ini_file_reader import IniFileReader
from quant.tool.database.base import SQLAlchemy

def code_formate(code):
    if code[0] == '6':
        return "sh." + code
    else:
        return 'sz.'+ code
    
    
def update_block_table(file_name='./quant/tool/database/file/block_conception_2023.ini', section='BLOCK_NAME_MAP_TABLE'):
    reader = IniFileReader(file_name)
    info_dic = reader.get_ini_infos(section)
    SQLAlchemy.create_all()
    with SQLAlchemy.session_context() as session:
        for key in info_dic:
            if info_dic[key] == '':
                continue
            block = Block(
                name=info_dic[key],
                code=key
            )
            session.add(block)
            session.commit()
            print(block)
            
def update_stock_block_table(file_name='./quant/tool/database/file/block_conception_2023.ini', 
                             section='BLOCK_STOCK_CONTEXT'):
    reader = IniFileReader(file_name)
    context_dic = reader.get_ini_infos(section)
    with SQLAlchemy.session_context() as session:
        for key in context_dic:
            if context_dic[key] == '':
                continue

            block = session.query(Block).filter(Block.code == key).first()
            if block is None:
                continue
            
            stock_list = context_dic[key].split(',')
            for stock_code in stock_list:
                if stock_code == '':
                    continue
                code_str = stock_code.split(':')[1]
                code = code_formate(code_str)
                stock = session.query(Stock).filter(Stock.code == code).first()
                if stock is None:
                    continue
                print(block)
                print(stock)
                block.stocks.append(stock)
                session.commit()
    
    


if __name__ == '__main__':
    # update_block_table()
    # update_block_table('./quant/tool/database/file/block_industry_2023.ini','BLOCK_NAME_MAP_TABLE')
    
    update_stock_block_table()
    update_stock_block_table('./quant/tool/database/file/block_industry_2023.ini','BLOCK_STOCK_CONTEXT')