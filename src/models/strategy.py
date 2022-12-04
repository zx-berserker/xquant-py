# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseHasCreateTime
from .many_to_many_table import strategy_stock_table


class Strategy(BaseHasCreateTime):
    __tablename__ = 'strategy'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')
    name = Column(String(50), nullable=False)
    mount = Column(Float, nullable=False)
    risk = Column(Float, nullable=False)
    is_share = Column(Boolean, default=False)
    stocks = relationship('Stock', secondary=strategy_stock_table)