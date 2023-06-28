# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""
import os, sys
sys.path.append(os.getcwd())

from quant.tool.database.base import SQLAlchemy
from quant.models.block import Block
from quant.models.many_to_many_table import stock_block_table
from quant.models.k_data_daily import KDataDaily
from sqlalchemy import func
from operator import and_
from quant.tool.database.data_models.block import BlockData
from quant.tool.file_writer import FileWriterTaskFactory
from quant.models.stock import Stock
from quant.models.stock_info import StockInfo

def query_test():
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Block).all()
        # for block in block_list:
        #     # query_block_avg(block, session)
        #     data_list = BlockData.query_block_data(session, block)
        #     return data_list
        return block_list


def query_block_avg(block, session):
    print(block.stocks)
    for stock in block.stocks:
        print(stock.k_data_daily[0])
    data_list = session.query(
        KDataDaily.date,
        func.avg(KDataDaily.close)
    ).filter(and_(
        KDataDaily.stock_id == stock_block_table.c.stock_id,
        block.id == stock_block_table.c.block_id
    )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
    print(data_list)



def query_yearly_net_profit():
    with SQLAlchemy.session_context() as session:
        data_list = session.query(
            Stock.name,
            func.sum(StockInfo.net_profit)
        ).filter(
            Stock.id == StockInfo.stock_id,
        ).group_by(StockInfo.stock_id).all()
    for data in data_list:
        if data[1] > 0:
            print(data[0])



if __name__ == '__main__':
    query_yearly_net_profit()