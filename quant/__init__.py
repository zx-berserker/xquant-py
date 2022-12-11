# -*- coding:utf-8 -*-
"""
date: 2022/12/1
author: Berserker
"""


from quant.tool.database.base import SQLAlchemy


def quant_database_init():
    SQLAlchemy.create_all()