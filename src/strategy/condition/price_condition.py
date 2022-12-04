# -*- encoding:utf-8 -*-
"""
date: 2020/8/28
author: Berserker
"""
import numpy as np
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum
from src.strategy.base import Variable, VariableTypeEnum
from .base import Condition, ConditionTypeEnum, ConditionOperatorTypeEnum
from src.strategy.technical_analysis_indicator.common_indicator import CommonIndicator


class PriceMonomialCondition(Condition):
    name = "PriceMonomialCondition "

    def __init__(self, name=None):
        super(PriceMonomialCondition, self).__init__(VariableTypeEnum.K_DATA_CLOSE,
                                                     ConditionOperatorTypeEnum.COND_GREATER, name)
        self.data_list = None
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_PRICE_MONOMIAL_RISE.value: self._judge_price_rise,
            ConditionTypeEnum.COND_PRICE_MONOMIAL_DROP.value: self._judge_price_drop,
            ConditionTypeEnum.COND_PRICE_MONOMIAL_FREEZE.value: self._judge_price_freeze
        }

        self.parameters = ["k_data", 'condition_type']

    def prepare(self, data_list):
        self.data_list = data_list

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_k_data = kwargs[self.parameters[0]]
        param_condition_type = kwargs[self.parameters[1]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        try:
            index = self.data_list.index(param_k_data)
        except ValueError:
            return False
        return self._judge_fun_dict[param_condition_type.value](param_k_data, index)

    def _judge_price_rise(self, k_data, index):
        if Variable.get_val(VariableTypeEnum.K_DATA_PCT_CHG, k_data) > 0.01 and \
            Variable.get_val(self.variable_type, k_data) - \
                Variable.get_val(self.variable_type, self.data_list[index - 1]) > 0.01:
            return True
        return False

    def _judge_price_drop(self, k_data, index):
        if Variable.get_val(VariableTypeEnum.K_DATA_PCT_CHG, k_data) < -0.01 and \
            Variable.get_val(self.variable_type, k_data) - \
                Variable.get_val(self.variable_type, self.data_list[index - 1]) < -0.01:
            return True
        return False

    def _judge_price_freeze(self, k_data, index):
        if -0.01 < Variable.get_val(VariableTypeEnum.K_DATA_PCT_CHG, k_data) < 0.01 or \
            -0.01 < Variable.get_val(self.variable_type, k_data) - \
                Variable.get_val(self.variable_type, self.data_list[index - 1]) < 0.01:
            return True
        return False


class PriceChartPatternCondition(Condition):
    name = "PriceChartPatternCondition"

    coe_gap_up = np.pi / 2 * 0.8367
    coe_gap_down = np.pi / 2 * -0.8367
    coe_peak_rise = np.pi / 6
    coe_peak_drop = np.pi / -6
    coe_peak_slope_radio = 0.25

    def __init__(self, name=None):
        super(PriceChartPatternCondition, self).__init__(VariableTypeEnum.K_DATA_CLOSE,
                                                         ConditionOperatorTypeEnum.COND_GREATER, name)
        self.parameters = ['condition_type', 'start_index', 'end_index']
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_PEAK.value: self._judge_pattern_peak,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_AV_PEAK.value: self._judge_pattern_av_peak,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_SHOOT_UP_PEAK.value: self._judge_pattern_shoot_up_peak,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_DROP_DOWN_PEAK.value: self._judge_pattern_drop_down_peak,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_GAP.value: self._judge_pattern_gap,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_GAP_UP.value: self._judge_pattern_gap_up,
            ConditionTypeEnum.COND_PRICE_CHART_PATTERN_GAP_DOWN.value: self._judge_pattern_gap_down
        }
        self.close_indicator = CommonIndicator(VariableTypeEnum.K_DATA_CLOSE)
        self.high_indicator = CommonIndicator(VariableTypeEnum.K_DATA_HIGH)
        self.low_indicator = CommonIndicator(VariableTypeEnum.K_DATA_LOW)
        self.data_list = None
        self.close_ref = None
        self.ma5 = None
        self.ma10 = None
        self.ma5_slope_radian = None
        self.ret_peak_data = None
        self.temp_start_index = None
        self.temp_end_index = None

    def prepare(self, data_list):
        self.data_list = data_list
        self.close_ref = self.close_indicator.ref(1, data_list)
        self.ma5 = self.close_indicator.ma(5, data_list)
        self.ma10 = self.close_indicator.ma(10, data_list)
        self.ma5_slope_radian = self.close_indicator.ma_slope_atan(5, data_list)
        self.ret_peak_data = None

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        param_start_index = kwargs[self.parameters[1]]
        param_end_index = kwargs[self.parameters[2]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        if param_start_index != self.temp_start_index or param_end_index != self.temp_end_index:
            self.ret_peak_data = None
            self.temp_start_index = param_start_index
            self.temp_end_index = param_end_index
        data_period_list = self.data_list[param_start_index: param_end_index]
        return self._judge_fun_dict[param_condition_type.value](data_period_list)

    def _judge_pattern_peak(self, data_period_list):
        ret_data = []
        data_start_index = self.data_list.index(data_period_list[0])
        data_end_index = self.data_list.index(data_period_list[-1])
        start_index = 0
        index = data_start_index
        is_first = True
        is_rise = False
        is_drop = False
        while index <= data_end_index:
            if is_first and self.ma5_slope_radian[index] > 0:
                start_index = index
                is_first = False
                is_rise = True
                is_drop = False
            elif is_rise and self.ma5_slope_radian[index] >= 0:
                pass
            elif is_rise and self.ma5_slope_radian[index] < 0:
                is_rise = False
                is_drop = True
            elif is_drop and self.ma5_slope_radian[index] < 0:
                pass
            elif is_drop and self.ma5_slope_radian[index] >= 0:
                end_index = index - 1
                temp_slope_ary = self.ma5_slope_radian[start_index: end_index]
                tem_ma5_ary = self.ma5[start_index: end_index]
                peek_left_slope = tem_ma5_ary.max() - tem_ma5_ary[0]
                peek_right_slope = tem_ma5_ary.max() - tem_ma5_ary[-1]
                if end_index - start_index > 4 and peek_left_slope != 0 and \
                        temp_slope_ary.max() > self.coe_peak_rise and \
                        temp_slope_ary.min() < self.coe_peak_drop and \
                        1 / self.coe_peak_slope_radio > peek_right_slope / peek_left_slope > self.coe_peak_slope_radio:
                    while start_index > 0:
                        if Variable.get_val(VariableTypeEnum.K_DATA_PCT_CHG, self.data_list[start_index - 1]) < 0:
                            break
                        start_index -= 1
                    while end_index > 0:
                        if Variable.get_val(VariableTypeEnum.K_DATA_PCT_CHG, self.data_list[end_index]) < 0:
                            break
                        end_index -= 1
                    ret_data.append({
                        'start': start_index,
                        'end': end_index
                    })
                is_first = True
                is_drop = False
                index = end_index
            else:
                is_first = True
                is_rise = False
                is_drop = False
            # print("%s===%s" % (self.data_list[index], self.ma5_slope_radian[index]))
            index += 1

        if ret_data:
            self.ret_peak_data = ret_data
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_av_peak(self, data_period_list):
        """
           *
          ***
         *****
        *******
        :return:
        """
        if not self.ret_peak_data:
            ret = self._judge_pattern_peak(data_period_list)
            if not ret:
                return False
        data_temp = self.ret_peak_data
        ret_data = []
        for data in data_temp:
            start_index = data['start']
            end_index = data['end']
            temp_data_list = self.data_list[start_index: end_index + 1]
            temp_len = len(temp_data_list)
            period_len = int(temp_len / 3)
            temp_max = max(temp_data_list, key=Variable.get_fun(self.variable_type))
            temp_max_index = temp_data_list.index(temp_max)
            if period_len <= temp_max_index < temp_len - period_len:
                ret_data.append(data)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_shoot_up_peak(self, data_period_list):
        """
          *
          **
         ****
         *****
        :return:
        """
        if not self.ret_peak_data:
            ret = self._judge_pattern_peak(data_period_list)
            if not ret:
                return False
        data_temp = self.ret_peak_data
        ret_data = []
        for data in data_temp:
            start_index = data['start']
            end_index = data['end']
            temp_data_list = self.data_list[start_index: end_index + 1]
            temp_len = len(temp_data_list)
            period_len = int(temp_len / 3)
            temp_max = max(temp_data_list, key=Variable.get_fun(self.variable_type))
            temp_max_index = temp_data_list.index(temp_max)
            if period_len > temp_max_index:
                ret_data.append(data)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_drop_down_peak(self, data_period_list):
        """
           *
          **
         ****
        *****
        :return:
        """
        if not self.ret_peak_data:
            ret = self._judge_pattern_peak(data_period_list)
            if not ret:
                return False
        data_temp = self.ret_peak_data
        ret_data = []
        for data in data_temp:
            start_index = data['start']
            end_index = data['end']
            temp_data_list = self.data_list[start_index: end_index + 1]
            temp_len = len(temp_data_list)
            period_len = int(temp_len / 3)
            temp_max = max(temp_data_list, key=Variable.get_fun(self.variable_type))
            temp_max_index = temp_data_list.index(temp_max)
            if temp_max_index >= temp_len - period_len:
                ret_data.append(data)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_gap(self, data_period_list):
        """
        :return:
        """
        ret_data = []
        ret = self._judge_pattern_gap_up(data_period_list)
        if ret:
            ret_data.extend(self.get_ret_data())
        ret = self._judge_pattern_gap_down(data_period_list)
        if ret:
            ret_data.extend(self.get_ret_data())

        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_gap_up(self, data_period_list):
        """
             *****

        *****
        :return:
        """
        ret_data = []
        data_index = self.data_list.index(data_period_list[0])
        low = np.asanyarray(Variable.data_list_to_variable_list(VariableTypeEnum.K_DATA_LOW, self.data_list))
        high_ref = self.high_indicator.ref(1, self.data_list)
        gap = low - high_ref
        for data in data_period_list:
            if Variable.get_val(self.variable_type, data) > self.close_ref[data_index] and gap[data_index] > 0:
                ret_data.append({
                    "start": data_index - 1,
                    "end": data_index
                })
            data_index += 1
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_gap_down(self, data_period_list):
        """
        *****

             *****
        :return:
        """
        ret_data = []
        data_index = self.data_list.index(data_period_list[0])
        low_ref = self.low_indicator.ref(1, self.data_list)
        high = np.asanyarray(Variable.data_list_to_variable_list(VariableTypeEnum.K_DATA_HIGH, self.data_list))
        gap = low_ref - high
        for data in data_period_list:
            if Variable.get_val(self.variable_type, data) < self.close_ref[data_index] and gap[data_index] > 0:
                ret_data.append({
                    "start": data_index - 1,
                    "end": data_index
                })
            data_index += 1
        if ret_data:
            self.ret_data = ret_data
            return True
        return False


class PriceIndicatorCondition(Condition):

    name = 'PriceIndicatorCondition'

    def __init__(self, name=None):
        super(PriceIndicatorCondition, self).__init__(VariableTypeEnum.K_DATA_CLOSE,
                                                      ConditionOperatorTypeEnum.COND_GREATER, name)
        self.parameters = ['condition_type']
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_PRICE_INDICATOR_MACD_LONG.value: self._judge_macd_long
        }
        self.close_indicator = CommonIndicator(VariableTypeEnum.K_DATA_CLOSE)
        self.data_list = None
        self.temp_start_index = None
        self.temp_end_index = None

    def prepare(self, data_list):
        self.data_list = data_list

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        return self._judge_fun_dict[param_condition_type.value]()

    def _judge_macd_long(self):
        macd, diff, dea = self.close_indicator.macd(self.data_list)
        if len(macd) < 3:
            return False
        if macd[-1] > macd[-2] > macd[-3] and diff[-1] < 0:
            return True
        else:
            return False
