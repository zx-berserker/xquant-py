# -*- coding:utf-8 -*-
"""
date: 2026/01/10
author: Berserker
"""
from datetime import datetime as dt, timedelta, timezone

class datetime(dt):
    # plus_8
    utc_base = timezone(timedelta(hours=8))

    def __new__(cls, year, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, *, fold=0):
       
        return dt.__new__(cls, year, month, day, hour, minute, second, microsecond, tzinfo, fold=fold)
    

    @classmethod
    def now(cls, tz=None):
        "Construct a datetime from time.time() and optional time zone info."
        return super().now(cls.utc_base)
    



