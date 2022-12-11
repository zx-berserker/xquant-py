# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .many_to_many_table import stock_block_table
from quant.libs.enums import StockTypeEnum
import re


class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    industry_id = Column(Integer, ForeignKey('industry.id'), nullable=True)
    industry = relationship("Industry",  order_by='Industry.id',  back_populates='stocks')
    name = Column(String(50), nullable=False)
    _stock_type = Column('stock_type', Integer, nullable=False)
    blocks = relationship('Block', secondary=stock_block_table, back_populates='stocks')
    k_data_hourly = relationship('KDataHourly', back_populates='stock', order_by='KDataHourly.time')
    k_data_daily = relationship('KDataDaily', back_populates='stock', order_by='KDataDaily.date')
    k_data_weekly = relationship('KDataWeekly', back_populates='stock', order_by='KDataWeekly.date')
    k_data_monthly = relationship('KDataMonthly', back_populates='stock', order_by='KDataMonthly.date')
    shareholders = relationship('Shareholder', back_populates='stock', order_by='Shareholder.date')
    float_shareholders = relationship('FloatShareholder', back_populates='stock', order_by='FloatShareholder.date')
    stock_info = relationship('StockInfo', back_populates='stock', order_by='StockInfo.date')
    k_data_2hourly = relationship('KData2Hourly', back_populates='stock', order_by='KData2Hourly.time')

    @property
    def stock_type(self):
        return StockTypeEnum(self._stock_type)

    @stock_type.setter
    def stock_type(self, type_enum):
        self._stock_type = int(type_enum)

    def __repr__(self):
        return "<%s name:%s code:%s industry:%s>" % (self.id, self.name, self.code, self.industry_id)

    def is_st(self, pattern=r".*ST.*"):
        if re.match(pattern, self.name, re.I):
            return True
        else:
            return False

    def is_delisted(self, pattern=r".*退.*"):
        if re.match(pattern, self.name, re.I):
            return True
        else:
            return False

