# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Boolean
from datetime import datetime
from contextlib import contextmanager
__all__ = ['Base', 'BaseHasCreateTime']


SQLBase = declarative_base()


class Base(SQLBase):
    __abstract__ = True

    status = Column(Boolean, default=True)

    def __eq__(self, other):
        if hasattr(self, "id") and hasattr(other, "id"):
            if self.id == other.id:
                return True
        return False


class BaseHasCreateTime(Base):
    __abstract__ = True

    create_time = Column(Integer)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    # def set_attrs(self, attrs):
    #     for key, value in attrs.items():
    #         if hasattr(self, key) and key != 'id':
    #             setattr(self, key, value)


