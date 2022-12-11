# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey,Table
from sqlalchemy.orm import relationship
from .base import Base

stock_block_table = Table(
    'stock_block', Base.metadata,
    Column('stock_id', Integer, ForeignKey('stock.id')),
    Column('block_id', Integer, ForeignKey('block.id'))
)


