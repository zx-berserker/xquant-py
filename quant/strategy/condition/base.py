# -*- encoding:utf-8 -*-
"""
date: 2020/8/24
author: Berserker
"""

from abc import ABC, abstractmethod
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from enum import Enum
from quant.tool.function_tool import check_dic_key_legal


class ConditionTypeEnum(Enum):
    COND_VOLUME_MONOMIAL_CLIMAX = "cond_volume_monomial_climax"
    COND_VOLUME_MONOMIAL_SHRINK = "cond_volume_monomial_shrink"
    COND_VOLUME_MONOMIAL_NONE = "cond_volume_monomial_none"
    COND_VOLUME_MONOMIAL_LIVELY = "cond_volume_monomial_lively"
    COND_PRICE_MONOMIAL_RISE = "cond_price_monomial_rise"
    COND_PRICE_MONOMIAL_DROP = "cond_price_monomial_drop"
    COND_PRICE_MONOMIAL_FREEZE = "cond_price_monomial_freeze"
    COND_RECENT_COMPARE_MAXIMUM = "cond_recent_compare_maximum"
    COND_RECENT_COMPARE_MINIMUM = "cond_recent_compare_minimum"
    COND_RECENT_COMPARE_FLUCTUATION = "cond_recent_compare_fluctuation"
    COND_SUBINTERVAL_FLUCTUATION = "cond_subinterval_fluctuation"
    COND_SUBINTERVAL_PCT_CHG = "cond_subinterval_pct_chg"
    COND_VOLUME_CHART_PATTERN_LIVELY = "con_volume_chart_pattern_lively"
    COND_VOLUME_CHART_PATTERN_HEAP = "cond_volume_chart_pattern_heap"
    COND_VOLUME_CHART_PATTERN_AV_HEAP = "cond_volume_chart_pattern_av_heap"
    COND_VOLUME_CHART_PATTERN_HALF_DROP_HEAP = "cond_volume_chart_pattern_half_drop_heap"
    COND_VOLUME_CHART_PATTERN_HALF_RISE_HEAP = "cond_volume_chart_pattern_half_rise_heap"
    COND_PRICE_CHART_PATTERN_PEAK = "cond_price_chart_pattern_peak"
    COND_PRICE_CHART_PATTERN_AV_PEAK = "cond_price_chart_pattern_av_peak"
    COND_PRICE_CHART_PATTERN_SHOOT_UP_PEAK = "cond_price_chart_pattern_shoot_up_peak"
    COND_PRICE_CHART_PATTERN_DROP_DOWN_PEAK = "cond_price_chart_pattern_drop_down_peak"
    COND_PRICE_CHART_PATTERN_GAP = "cond_price_chart_pattern_gap"
    COND_PRICE_CHART_PATTERN_GAP_UP = "cond_price_chart_pattern_gap_up"
    COND_PRICE_CHART_PATTERN_GAP_DOWN = "cond_price_chart_pattern_gap_down"
    COND_PRICE_INDICATOR_MACD_LONG = "cond_price_indicator_macd_long"


class ConditionOperatorTypeEnum(Enum):
    COND_GREATER = 'cond_operator_greater'
    COND_LESS = 'cond_operator_less'
    COND_EQUAL = 'cond_operator_equal'
    COND_GREATER_EQUAL = 'cond_operator_greater_equal'
    COND_LESS_EQUAL = 'cond_operator_less_equal'


class ConditionOperator(object):

    _operator = {
        ConditionOperatorTypeEnum.COND_GREATER.value: lambda left, right: left > right,
        ConditionOperatorTypeEnum.COND_LESS.value: lambda left, right: left < right,
        ConditionOperatorTypeEnum.COND_EQUAL.value: lambda left, right: left == right,
        ConditionOperatorTypeEnum.COND_GREATER_EQUAL.value: lambda left, right: left >= right,
        ConditionOperatorTypeEnum.COND_LESS_EQUAL.value: lambda left, right: left <= right
    }

    @classmethod
    def get_operator(cls, operator_type):
        check_dic_key_legal(cls._operator, operator_type.value)
        return cls._operator[operator_type.value]


class Condition(ABC):
    name = 'Condition'

    def __init__(self, variable_type, operator_type, name=None):
        self.variable_type = variable_type
        self.parameters = None
        self.cond_operator = ConditionOperator.get_operator(operator_type)
        self.ret_data = None
        if name:
            self.name = name

    @abstractmethod
    def prepare(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    @abstractmethod
    def judge(self, *args, **kwargs):
        raise XException(ErrorCodeEnum.CODE_INVALID, "Abstract function is invalid !")

    def get_ret_data(self):
        return self.ret_data

