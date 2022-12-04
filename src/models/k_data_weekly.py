# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, String, ForeignKey, BigInteger, Float, Date, Integer
from sqlalchemy.orm import relationship
from .base import Base


class KDataWeekly(Base):
    __tablename__ = 'k_data_weekly'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    stock = relationship('Stock', back_populates='k_data_weekly')
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    turn = Column(Float, nullable=False)
    pct_chg = Column(Float, nullable=False)

    def __repr__(self):
        return "<KDataWeekly date:%s stock_id:%s>" % (self.date, self.stock_id)