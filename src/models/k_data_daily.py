# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Date, String, ForeignKey, Float, BigInteger, Integer
from sqlalchemy.orm import relationship
from .base import Base


class KDataDaily(Base):
    __tablename__ = 'k_data_daily'
    """
    volume: 成交量（股）
    amount: 成交额（元）
    turn: 换手率(%)
    pct_chg: 涨跌幅(%)
    pe_ttm: 滚动市盈率(%)
    pb_mrq: 市净率(%)
    ps_ttm: 滚动市销率(%)
    pcf_ncf_ttm: 滚动市现率(%)
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    stock = relationship('Stock', back_populates='k_data_daily')
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    pre_close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    amount = Column(Float, nullable=False)
    turn = Column(Float, nullable=False, default=0.0)
    pct_chg = Column(Float, nullable=False)
    pe_ttm = Column(Float, default=0.0)
    pb_mrq = Column(Float, default=0.0)
    ps_ttm = Column(Float, default=0.0)
    pcf_ncf_ttm = Column(Float, default=0.0)

    def __repr__(self):
        return "<KDataDaily date:%s stock_id:%s close:%f>" % (self.date, self.stock_id, self.close)
