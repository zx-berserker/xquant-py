# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base
from .many_to_many_table import stock_block_table


class Block(Base):
    __tablename__ = 'block'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), nullable=False)
    stocks = relationship("Stock", secondary=stock_block_table, back_populates='blocks')

    def __repr__(self):
        return '<Block id:%s name:%s code:%s>' % (self.id, self.name, self.code)
    
    