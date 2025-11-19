# -*- coding:utf-8 -*-
"""
date: 2025/11/10
author: Berserker
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base
from dataclasses import dataclass, asdict

@dataclass
class Exchange(Base):
    __tablename__ = "exchange"
    
    id:int = Column(Integer, primary_key=True, autoincrement=True)
    code:str = Column(String(20), unique=True, nullable=False)
    name:str = Column(String(20), unique=True, nullable=False)
    east_money_code = Column(String(20), unique=True, nullable=True)
    products = relationship('Product', back_populates='exchange')

    def __repr__(self):
        return "<Exchange id:%d code:%s name:%s>" % (self.id, self.code, self.name)

    def to_dic(self):
        data = asdict(self)
        return data