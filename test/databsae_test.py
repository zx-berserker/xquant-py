# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""

from src.tool.database.base import SQLAlchemy
from src.models.block import Block
from src.models.many_to_many_table import stock_block_table
from src.models.k_data_daily import KDataDaily
from sqlalchemy import func
from operator import or_, and_
from src.tool.database.data_models.block import BlockData


def query_test():
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Block).all()
        for block in block_list:
            # query_block_avg(block, session)
            data_list = BlockData.query_block_data(session, block)
            return data_list


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