# -*- encoding:utf-8 -*-
"""
date: 2022/11/11
author: Berserker
"""

from sqlalchemy import Column, ForeignKey, BigInteger, Float, Integer, Date
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship
from .base import Base


class KData2Hourly(Base):
    __tablename__ = 'k_data_2hourly'
    """半个交易日
    time: 交易所行情时间(YYYY-MM-DD HH:MM:SS.sss)
    volume: 成交量(股)
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DATETIME(fsp=3), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    stock = relationship('Stock', back_populates='k_data_2hourly')
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)

    def __repr__(self):
        return "<KData2Hourly time:%s stock_id:%s>" % (self.time, self.stock_id)
    
