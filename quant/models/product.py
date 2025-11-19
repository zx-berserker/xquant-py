# -*- coding:utf-8 -*-
"""
date: 2025/11/12
author: Berserker
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from quant.libs.enums import ProductTypeEnum
import re
from dataclasses import dataclass, asdict


@dataclass
class Product(Base):
    __tablename__ = "product"

    id:int = Column(Integer, primary_key=True, autoincrement=True)
    code:str = Column(String(20), unique=False, nullable=False)
    name:str = Column(String(50), nullable=False)
    _type = Column('type', Integer, nullable=False)
    exchange_id = Column(Integer, ForeignKey('exchange.id'), nullable=True)
    exchange = relationship("Exchange",  order_by='Exchange.id',  back_populates='products')
    quote_hourly = relationship('QuoteHourly', back_populates='product', order_by='QuoteHourly.time')
    quote_daily = relationship('QuoteDaily', back_populates='product', order_by='QuoteDaily.time')
    quote_weekly = relationship('QuoteWeekly', back_populates='product', order_by='QuoteWeekly.time')
    quote_monthly = relationship('QuoteMonthly', back_populates='product', order_by='QuoteMonthly.time')


    @property
    def type(self):
        return ProductTypeEnum(self._type)

    @type.setter
    def type(self, type_enum:ProductTypeEnum):
        self._type = type_enum.value

    def __repr__(self):
        return "<Product name:%s code:%s>" % (self.name, self.code)
    
    def is_st(self, pattern=r".*ST.*"):
        if self.type != ProductTypeEnum.PRODUCT_STOCK:
            return False
        if re.match(pattern, self.name, re.I):
            return True
        else:
            return False

    def is_delisted(self, pattern=r".*退.*"):
        if self.type != ProductTypeEnum.PRODUCT_STOCK:
            return False
        if re.match(pattern, self.name, re.I):
            return True
        else:
            return False
        
    def to_dic(self):
        data = asdict(self)
        data["type"] = self._type
        return data
