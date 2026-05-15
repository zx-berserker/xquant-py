# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""
from quant.models.block import Block
from quant.models.industry import Industry
from quant.models.stock import Stock
from quant.tool.ini_file_reader import IniFileReader
from operator import or_, and_
from quant.libs.enums import StockTypeEnum
from quant.tool.database import SQLAlchemy
from quant.spider.east_money import QuotePeriodEnum
import os
from quant.tool.database.database_task_factoty import BulkUpdateTaskFactory, CacheFileReaderTaskFactory
from quant.tool.database.updater import Updater
from quant.models.quote_daily import QuoteDaily
from quant.models.quote_hourly import QuoteHourly
from quant.models.quote_monthly import QuoteMonthly
from quant.models.quote_weekly import QuoteWeekly
from quant.libs.log import XLog
import shutil

def update_industry_table():
    reader = IniFileReader('./file/industry.ini')
    info_list = reader.get_ini_infos('name')
    with SQLAlchemy.session_context() as session:
        for obj in info_list:
            for key, value in obj.items():
                industry = Industry(
                    name=value.replace(';', ''),
                    code=key
                )
                session.add(industry)
        session.commit()


def update_block_table():
    reader = IniFileReader('./file/block.ini')
    info_list = reader.get_ini_infos('板块指数代码')
    with SQLAlchemy.session_context() as session:
        for obj in info_list:
            for key, value in obj.items():
                val = value.split(',')
                block = Block(
                    name=val[0],
                    code=val[1]
                )
                session.add(block)
        session.commit()


def update_stock_block_table():
    reader = IniFileReader('./file/stock_block.ini')
    code_list = reader.get_sections_options('BLOCK_NAME_MAP_TABLE')
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Block).all()
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
                stock = session.query(Stock).filter(and_(
                    Stock._stock_type == int(StockTypeEnum.STOCK_SHARES.value),
                    Stock.code == code
                )).first()
                if stock is None:
                    continue
                block.stocks.append(stock)



def update_quote_from_cache_file(dir_path:str='/home/xquant/cache', dst_path='/home/xquant/cache/Done'):
    file_name_list = os.listdir(dir_path)
    data_list_dic:dict[str, list[str]] = {}
    data_list_dic[QuotePeriodEnum.DAILY.name] = []
    data_list_dic[QuotePeriodEnum.HOURLY.name] = []
    data_list_dic[QuotePeriodEnum.MONTHLY.name] = []
    data_list_dic[QuotePeriodEnum.WEEKLY.name] = []
    for name in file_name_list:
        name_list = name.split(".")
        if "json" in name_list:
            pre_name_list = name_list[0].split("-")
            if QuotePeriodEnum.DAILY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.DAILY.name].append(name)
            elif QuotePeriodEnum.HOURLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.HOURLY.name].append(name)
            elif QuotePeriodEnum.MONTHLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.MONTHLY.name].append(name)
            elif QuotePeriodEnum.WEEKLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.WEEKLY.name].append(name)

    for key in data_list_dic:
        if key == QuotePeriodEnum.DAILY.name:
            updateFactory = BulkUpdateTaskFactory(QuoteDaily)
        elif key == QuotePeriodEnum.HOURLY.name:
            updateFactory = BulkUpdateTaskFactory(QuoteHourly)
        elif key == QuotePeriodEnum.WEEKLY.name:
            updateFactory = BulkUpdateTaskFactory(QuoteWeekly)
        elif key == QuotePeriodEnum.MONTHLY.name:
            updateFactory = BulkUpdateTaskFactory(QuoteMonthly)
        XLog.info(key)
        dataFactory = CacheFileReaderTaskFactory(dir_path)
        
        Updater.spider_thread_pool_capacity = 1
        Updater.update_thread_pool_capacity = 1
        Updater.interval_sleep = 0
        updater = Updater(data_list_dic[key], updateFactory, dataFactory)
        updater.start()
        error = updater.join()
        if error:
            XLog.error(key + " error break!")
            return
        
        XLog.info(key + " move files to:" + dst_path)
        for file_name in data_list_dic[key]:
            src = dir_path + '/' + file_name
            dst = dst_path+ '/' + file_name
            shutil.move(src, dst)
        XLog.info(key + " finish")

    
    XLog.info("end.")





if __name__ == "__main__":
    update_quote_from_cache_file()