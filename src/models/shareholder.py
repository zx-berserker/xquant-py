# -*- encoding:utf-8 -*-
"""
date: 2020/8/29
author: Berserker
"""
from .base import Base
from sqlalchemy import Column, String, Float, ForeignKey, BigInteger, Integer, Date
from sqlalchemy.orm import relationship


class Shareholder(Base):
    """
    date: 报告日期
    name: 股东名称
    holder_type: 股东类型
    hold_number: 数量
    hold_ratio: 持股占比
    rank: 股东排名
    amount: 市值
    change: 持股变动
    """
    __tablename__ = 'shareholder'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    name = Column(String(200), nullable=False)
    holder_type = Column(String(20), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    stock = relationship('Stock', back_populates='shareholders')
    hold_number = Column(BigInteger, nullable=False)
    hold_ratio = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    change = Column(String(20), nullable=False)


class FloatShareholder(Base):
    """
    date: 报告日期
    name: 股东名称
    holder_type: 股东类型
    hold_number: 数量
    hold_ratio: 持股占比
    rank: 股东排名
    amount: 市值
    change: 持股变动
    """
    __tablename__ = 'float_shareholder'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    name = Column(String(200), nullable=False)
    holder_type = Column(String(20), nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    stock = relationship('Stock', back_populates='float_shareholders')
    hold_number = Column(BigInteger, nullable=False)
    hold_ratio = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    change = Column(String(20), nullable=False)

