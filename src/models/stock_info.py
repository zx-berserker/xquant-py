"""
date: 2022/11/11
author: Berserker
"""

from sqlalchemy import Column, Integer, ForeignKey, Date, Float, BigInteger
from sqlalchemy.orm import relationship
from .base import Base


class StockInfo(Base):
    __tablename__ = 'stock_info'
    """_summary_
    date:  统计日期
    roe_avg: 净资产收益率(平均)(%)
    np_margin: 销售净利率(%)
    gp_margin: 销售毛利率(%)
    net_profit: 净利润(元)
    eps_ttm: 每股收益(元)
    mbr_revenue: 主营营业收入(元)
    total_share: 总股本(股)
    liqa_share: 流通股本
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    stock_id = Column(Integer, ForeignKey('stock.id'), nullable=False)
    roe_avg = Column(Float, nullable=False)
    np_margin = Column(Float)
    gp_margin = Column(Float)
    net_profit = Column(Float, nullable=False)
    eps_ttm = Column(Float, nullable=False)
    mbr_revenue = Column(Float, nullable=False)
    total_share = Column(BigInteger, nullable=False)
    liqa_share = Column(BigInteger, nullable=False)
    stock = relationship('Stock', back_populates='stock_info')

    def __repr__(self):
        return "<StockInfo:%s stock_id:%s date:%s total_share:%s>" % (self.id, self.stock_id, self.date, self.total_share)
