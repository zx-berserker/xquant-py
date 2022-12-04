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

favorite_stock_table = Table(
    'favorite_stock', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('stock_id', Integer, ForeignKey('stock.id'))
)

favorite_strategy_table = Table(
    'favorite_strategy', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('strategy_id', Integer, ForeignKey('strategy.id'))
)

strategy_stock_table = Table(
    'strategy_stock', Base.metadata,
    Column('strategy_id', Integer, ForeignKey('strategy.id')),
    Column('stock_id', Integer, ForeignKey('stock.id'))
)

