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


if __name__ == '__main__':

    data_list = query_test()
    print(data_list)
    data = ''
    for li in data_list:
        data += str(li)
    fac = FileWriterTaskFactory('E:/WorkSpace/test', 'name.txt')
    task = fac.get_task(data)
    task.executive()