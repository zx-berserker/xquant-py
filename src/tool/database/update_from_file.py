# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""
from src.models.base import db
from src.models.block import Block
from src.models.strategy import Strategy
from src.models.k_data_daily import KDataDaily
from src.models.k_data_monthly import KDataMonthly
from src.models.k_data_weekly import KDataWeekly
from src.models.industry import Industry
from src.models.stock import Stock
from src.models.trade import Trade
from src.tool.ini_file_reader import IniFileReader
from operator import or_, and_
from src.libs.enums import StockTypeEnum


def update_industry_table():
    reader = IniFileReader('./file/industry.ini')
    info_list = reader.get_ini_infos('name')
    for obj in info_list:
        for key, value in obj.items():
            industry = Industry(
                name=value.replace(';', ''),
                code=key
            )
            db.session.add(industry)


def update_block_table():
    reader = IniFileReader('./file/block.ini')
    info_list = reader.get_ini_infos('板块指数代码')
    for obj in info_list:
        for key, value in obj.items():
            val = value.split(',')
            block = Block(
                name=val[0],
                code=val[1]
            )
            db.session.add(block)


def update_stock_block_table():
    block_list = Block.query.all()
    reader = IniFileReader('./file/stock_block.ini')
    code_list = reader.get_sections_options('BLOCK_NAME_MAP_TABLE')
    for block in block_list:
        if block.code not in code_list:
            continue
        value = reader.get_option_values('BLOCK_STOCK_CONTEXT', block.code)
        value = value[:-1]
        value_list = value.split(',')
        for item_str in value_list:
            code = item_str.split(':')[1]
            if code[0] == '6':
                code = 'sh.' + code
            else:
                code = 'sz.' + code
            stock = Stock.query.filter(and_(
                Stock._stock_type == int(StockTypeEnum.STOCK_SHARES.value),
                Stock.code == code
            )).first()
            if stock is None:
                continue
            block.stocks.append(stock)



