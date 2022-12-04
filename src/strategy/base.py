# -*- encoding:utf-8 -*-
"""
date: 2020/8/25
author: Berserker
"""

from enum import IntEnum
from src.tool.function_tool import check_dic_key_legal
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum


class VariableTypeEnum(IntEnum):
    COMMON_DATA_TYPE = 0
    STOCK_INFO_CAPITAL = COMMON_DATA_TYPE + 1
    SHAREHOLDER_HOLD_RATIO = COMMON_DATA_TYPE + 2
    SHAREHOLDER_HOLD_NUMBER = COMMON_DATA_TYPE + 3
    ARRAY_DATA_TYPE = 100
    K_DATA_OPEN = ARRAY_DATA_TYPE + 1
    K_DATA_CLOSE = ARRAY_DATA_TYPE + 2
    K_DATA_VOLUME = ARRAY_DATA_TYPE + 3
    K_DATA_TURN = ARRAY_DATA_TYPE + 4
    K_DATA_HIGH = ARRAY_DATA_TYPE + 5
    K_DATA_LOW = ARRAY_DATA_TYPE + 6
    K_DATA_PCT_CHG = ARRAY_DATA_TYPE + 7
    K_DATA_AMOUNT = ARRAY_DATA_TYPE + 8


class Variable(object):

    _variable = {
        VariableTypeEnum.K_DATA_CLOSE: lambda k_data: k_data.close if hasattr(k_data, "close") else k_data,
        VariableTypeEnum.K_DATA_VOLUME: lambda k_data: k_data.volume if hasattr(k_data, "volume") else k_data,
        VariableTypeEnum.K_DATA_TURN: lambda k_data: k_data.turn if hasattr(k_data, "turn") else k_data,
        VariableTypeEnum.K_DATA_HIGH: lambda k_data: k_data.high if hasattr(k_data, "high") else k_data,
        VariableTypeEnum.K_DATA_LOW: lambda k_data: k_data.low if hasattr(k_data, "low") else k_data,
        VariableTypeEnum.K_DATA_OPEN: lambda k_data: k_data.low if hasattr(k_data, "open") else k_data,
        VariableTypeEnum.K_DATA_AMOUNT: lambda k_data: k_data.low if hasattr(k_data, "amount") else k_data,
        VariableTypeEnum.K_DATA_PCT_CHG: lambda k_data: k_data.pct_chg if hasattr(k_data, "pct_chg") else k_data,
        VariableTypeEnum.STOCK_INFO_CAPITAL: lambda info: info.liqa_share if hasattr(info, "liqa_share") else info,
        VariableTypeEnum.SHAREHOLDER_HOLD_RATIO: lambda holder: holder.hold_ratio if hasattr(holder, "hold_ratio") else holder,
        VariableTypeEnum.SHAREHOLDER_HOLD_NUMBER: lambda holder: holder.hold_number if hasattr(holder, "hold_number") else holder
    }

    @classmethod
    def get_val(cls, variable_type, data):
        check_dic_key_legal(cls._variable, variable_type)
        return cls._variable[variable_type](data)

    @classmethod
    def get_fun(cls, variable_type):
        check_dic_key_legal(cls._variable, variable_type)
        return cls._variable[variable_type]

    @classmethod
    def data_list_to_variable_list(cls, variable_type, data_list):
        if variable_type > VariableTypeEnum.ARRAY_DATA_TYPE:
            return [cls.get_val(variable_type, data) for data in data_list]
        else:
            raise XException(ErrorCodeEnum.CODE_INVALID, "VariableType not support array!")


