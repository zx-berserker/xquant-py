# -*- encoding:utf-8 -*-
"""
date: 2020/8/23
author: Berserker
"""

from .base import Factor
from src.strategy.condition.single_variable_condition import SubintervalCondition, RecentCompareCondition
from src.strategy.condition.base import ConditionTypeEnum, ConditionOperatorTypeEnum
from src.strategy.condition.volume_condition import VolumeChartPatternCondition
from src.strategy.condition.price_condition import PriceChartPatternCondition, PriceIndicatorCondition
from src.strategy.base import VariableTypeEnum
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum


class StockBuildPositionFactor(Factor):

    def __init__(self, start_index, end_index):
        super(StockBuildPositionFactor, self).__init__()
        self.add_condition(
            RecentCompareCondition.name,
            RecentCompareCondition(VariableTypeEnum.K_DATA_CLOSE)
        )
        self.add_condition(VolumeChartPatternCondition.name, VolumeChartPatternCondition())
        self.add_condition(SubintervalCondition.name, SubintervalCondition(
            VariableTypeEnum.K_DATA_CLOSE,
            ConditionOperatorTypeEnum.COND_LESS
        ))
        self.add_condition(
            PriceChartPatternCondition.name,
            PriceChartPatternCondition()
        )
        self.parameters = ['data_list', 'shareholder_list', 'float_shareholder_list', 'coe_recent_fluctuation',
                           'coe_fluctuation', 'coe_recent_mini']
        self.start_index = start_index
        self.end_index = end_index
        pass

    def _prepare(self, data_list, shareholder_list, float_shareholder_list):
        self.condition_prepare(VolumeChartPatternCondition.name, data_list, shareholder_list, float_shareholder_list)
        self.condition_prepare(RecentCompareCondition.name, data_list)
        self.condition_prepare(SubintervalCondition.name, data_list)
        self.condition_prepare(PriceChartPatternCondition.name, data_list)

    def estimate(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
            data_list: the list of data (eg. k_data_daily)
            data_length: the length of data deal with
        :return: bool
        """
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The' + param + 'is invalid !')
        self._prepare(kwargs[self.parameters[0]], kwargs[self.parameters[1]], kwargs[self.parameters[2]])

        coe_recent_fluctuation = kwargs[self.parameters[3]]
        coe_fluctuation = kwargs[self.parameters[4]]
        coe_recent_mini = kwargs[self.parameters[5]]

        ret = self.condition_judge(
            RecentCompareCondition.name,
            condition_type=ConditionTypeEnum.COND_RECENT_COMPARE_FLUCTUATION,
            start_index=self.start_index,
            end_index=self.end_index,
            coefficient=coe_recent_fluctuation
        )
        if not ret:
            return ret

        ret = self.condition_judge(
            SubintervalCondition.name,
            condition_type=ConditionTypeEnum.COND_SUBINTERVAL_FLUCTUATION,
            start_index=self.start_index,
            end_index=self.end_index,
            coefficient=coe_fluctuation
        )
        if not ret:
            return False

        ret = self.condition_judge(
            PriceChartPatternCondition.name,
            condition_type=ConditionTypeEnum.COND_PRICE_CHART_PATTERN_PEAK,
            start_index=self.start_index,
            end_index=self.end_index
        )
        if not ret:
            return False

        ret_data_list = self.condition_get_ret_data(PriceChartPatternCondition.name)
        for data in ret_data_list:
            start = data['start']
            end = data['end']
            ret = self.condition_judge(
                VolumeChartPatternCondition.name,
                condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP,
                start_index=start,
                end_index=end
            )
            if ret:
                return True
        return False


class StockSecondBuildPositionFactor(Factor):
    """
    todo: 提取二次建仓买点特征
    """
    def __init__(self):
        super(StockSecondBuildPositionFactor, self).__init__()

    def _prepare(self,*args, **kwargs):
        pass

    def estimate(self, *args, **kwargs):
        pass


class StockOversoldFactor(Factor):

    def __init__(self, start_index, end_index):
        super(StockOversoldFactor, self).__init__()
        self.start_index = start_index
        self.end_index = end_index
        self.parameters = ['data_list', 'shareholder_list', 'float_shareholder_list', 'coe_pct_chg']

        self.add_condition(
            SubintervalCondition.name,
            SubintervalCondition(VariableTypeEnum.K_DATA_CLOSE, ConditionOperatorTypeEnum.COND_LESS)
        )
        self.add_condition(
            VolumeChartPatternCondition.name,
            VolumeChartPatternCondition()
        )

    def _prepare(self, data_list, shareholder_list, float_shareholder_list):
        self.condition_prepare(SubintervalCondition.name, data_list)
        self.condition_prepare(VolumeChartPatternCondition.name, data_list, shareholder_list, float_shareholder_list)
        pass

    def estimate(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The' + param + 'is invalid !')
        self._prepare(kwargs[self.parameters[0]], kwargs[self.parameters[1]], kwargs[self.parameters[2]])

        coe_pct_chg = kwargs[self.parameters[3]]

        ret = self.condition_judge(
            SubintervalCondition.name,
            condition_type=ConditionTypeEnum.COND_SUBINTERVAL_PCT_CHG,
            start_index=self.start_index,
            end_index=self.end_index,
            coefficient=coe_pct_chg
        )
        if not ret:
            return ret
        ret = self.condition_judge(
            VolumeChartPatternCondition.name,
            condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP,
            start_index=self.start_index,
            end_index=self.end_index
        )
        return ret


class StockLivelyFactor(Factor):

    def __init__(self, start_index, end_index):
        super(StockLivelyFactor, self).__init__()
        self.add_condition(
            RecentCompareCondition.name,
            RecentCompareCondition(VariableTypeEnum.K_DATA_CLOSE, ConditionOperatorTypeEnum.COND_LESS)
        )
        self.add_condition(VolumeChartPatternCondition.name, VolumeChartPatternCondition())
        self.add_condition(PriceIndicatorCondition.name, PriceIndicatorCondition())

        self.parameters = ['data_list', 'shareholder_list', 'float_shareholder_list', 'coe_recent_mini',
                           'k_data_hourly_list']
        self.start_index = start_index
        self.end_index = end_index

    def _prepare(self, data_list, shareholder_list, float_shareholder_list, k_data_hourly_list):
        self.condition_prepare(VolumeChartPatternCondition.name, data_list, shareholder_list, float_shareholder_list)
        self.condition_prepare(RecentCompareCondition.name, data_list)
        self.condition_prepare(PriceIndicatorCondition.name, k_data_hourly_list)

    def estimate(self, *args, **kwargs):
        """
                :param args:
                :param kwargs:
                    data_list: the list of data (eg. k_data_daily)
                    data_length: the length of data deal with
                :return: bool
                """
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The' + param + 'is invalid !')
        self._prepare(kwargs[self.parameters[0]], kwargs[self.parameters[1]], kwargs[self.parameters[2]],
                      kwargs[self.parameters[4]])

        coe_recent_mini = kwargs[self.parameters[3]]

        ret = self.condition_judge(
            VolumeChartPatternCondition.name,
            condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_LIVELY,
            start_index=self.start_index,
            end_index=self.end_index
        )
        if not ret:
            return ret

        ret = self.condition_judge(
            VolumeChartPatternCondition.name,
            condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP,
            start_index=self.start_index,
            end_index=self.end_index
        )
        if not ret:
            return ret
        ret = self.condition_judge(
            RecentCompareCondition.name,
            condition_type=ConditionTypeEnum.COND_RECENT_COMPARE_MINIMUM,
            start_index=self.start_index,
            end_index=self.end_index,
            coefficient=coe_recent_mini
        )
        if not ret:
            return ret
        ret = self.condition_judge(
            PriceIndicatorCondition.name,
            condition_type=ConditionTypeEnum.COND_PRICE_INDICATOR_MACD_LONG,
        )
        return ret
