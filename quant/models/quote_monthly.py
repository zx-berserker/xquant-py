# -*- coding:utf-8 -*-
"""
date: 2025/11/14
author: Berserker
"""

from sqlalchemy import Column, Date, String, ForeignKey, Float, BigInteger, Integer
from sqlalchemy.orm import relationship
from .base import Base
from dataclasses import dataclass, asdict

@dataclass
class QuoteMonthly(Base):
    __tablename__ = 'quote_monthly'
    """
    volume: 成交量（股）
    amount: 成交额（元）
    pct_chg: 涨跌幅(%)
    turn: 换手率(%)
    hold: (open interest) 期货持仓量
    """
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    time = Column(Date, nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product', back_populates='quote_monthly')
    open:float = Column(Float, nullable=False)
    high:float = Column(Float, nullable=False)
    low:float = Column(Float, nullable=False)
    close:float = Column(Float, nullable=False)
    volume:int = Column(BigInteger, nullable=False)
    amount:float = Column(Float, nullable=False)
    pct_chg:float = Column(Float, nullable=False)
    turn:float = Column(Float, nullable=False, default=0.0)
    hold:int = Column(BigInteger, nullable=False, default=0.0)


    def __repr__(self):
        return "<QuoteMonthly time:%s product_id:%s close:%f>" % (self.time, self.product_id, self.close)

    def to_dic(self):
        data = asdict(self)
        data["time"] = "%s" % (self.time)
        return data