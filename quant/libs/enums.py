# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from enum import Enum


class TradeTypeEnum(Enum):
    TRADE_BUY = 100
    TRADE_SELL = 200


class ClientTypeEnum(Enum):
    USER_EMAIL = 100
    USER_MOBILE = 101
    # 微信小程序
    USER_MINA = 200
    # 微信公众号
    USER_WX = 201


class UserAuthorityEnum(Enum):
    AUTH_COMMON = 1
    AUTH_ADMIN = 100
    AUTH_SUPER = 200


class StockTypeEnum(Enum):
    STOCK_SHARES = 1
    STOCK_INDEX = 2
    STOCK_OTHER = 3


class ErrorCodeEnum(Enum):
    CODE_OK = 0
    CODE_FAILED = 1
    CODE_ERROR_UNKNOWN = 2
    CODE_EXIST = 3
    CODE_NOT_FOUND = 4
    CODE_INVALID = 5
    CODE_PARAMETER_INVALID = 6
    CODE_FORBIDDEN = 7
    CODE_SYSTEM_ERROR = 8
