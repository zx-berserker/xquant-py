# -*- encoding:utf-8 -*-
"""
date: 2020/9/13
author: Berserker
"""

from src.models.many_to_many_table import stock_block_table
from src.models.k_data_daily import KDataDaily
from sqlalchemy import func
from operator import or_, and_


class BlockData(object):

    def __init__(self, block, data_tuple):
        self.block = block
        self.id = data_tuple[0]
        self.date = data_tuple[1]
        self.close = data_tuple[2]
        self.pct_chg = data_tuple[3]
        self.turn = data_tuple[4]

    def __repr__(self):
        return '<BlockData block:%s date:%s close:%f>' % (self.block, self.date, self.close)

    @staticmethod
    def query_block_data(session, block):
        data_list = session.query(
            KDataDaily.id,
            KDataDaily.date,
            func.avg(KDataDaily.close),
            func.avg(KDataDaily.pct_chg),
            func.avg(KDataDaily.turn)
        ).filter(and_(
            KDataDaily.stock_id == stock_block_table.c.stock_id,
            block.id == stock_block_table.c.block_id
        )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
        ret_list = []
        for data in data_list:
            ret_list.append(BlockData(block, data))
        return ret_list
