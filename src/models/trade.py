# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Integer, String, Date, BigInteger,ForeignKey, Float, SmallInteger
from sqlalchemy.orm import relationship
from .base import Base
from src.libs.enums import TradeTypeEnum


class Trade(Base):
    __tablename__ = 'trade'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')
    date = Column(Date, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'))
    # 价格
    price = Column(Float, nullable=False)
    # 股数
    share = Column(Integer, nullable=False)
    strategy_id = Column(Integer, ForeignKey('strategy.id'))
    strategy = relationship('Strategy')
    # 类型 -1 买，1 卖
    _type = Column('type', SmallInteger)

    @property
    def type(self):
        if self._type == -1:
            return TradeTypeEnum.TRADE_BUY
        else:
            return TradeTypeEnum.TRADE_SELL

    @type.setter
    def type(self, type_enum):
        if type_enum == TradeTypeEnum.TRADE_BUY:
            self._type = -1
        elif type_enum == TradeTypeEnum.TRADE_SELL:
            self._type = 1
