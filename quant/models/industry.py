# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), nullable=False)
    stocks = relationship('Stock', back_populates='industry')

