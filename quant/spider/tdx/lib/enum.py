# -*- coding:utf-8 -*-
"""
date: 2025/11/16
author: Berserker
"""
from tools.pytdx.params import TDXParams
from enum import Enum

class QuotePeriodEnum(Enum):
    DAILY = TDXParams.KLINE_TYPE_DAILY
    WEEKLY = TDXParams.KLINE_TYPE_WEEKLY
    MONTHLY = TDXParams.KLINE_TYPE_MONTHLY
    HOURLY = TDXParams.KLINE_TYPE_1HOUR