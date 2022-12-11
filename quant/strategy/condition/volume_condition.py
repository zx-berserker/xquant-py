# -*- encoding:utf-8 -*-
"""
date: 2020/8/28
author: Berserker
"""

from .base import Condition, ConditionTypeEnum, ConditionOperatorTypeEnum
from quant.strategy.base import VariableTypeEnum, Variable
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.strategy.technical_analysis_indicator.common_indicator import CommonIndicator


class VolumeMonomialCondition(Condition):
    name = 'VolumeMonomialCondition'

    def __init__(self, name=None):
        super(VolumeMonomialCondition, self).__init__(VariableTypeEnum.K_DATA_VOLUME,
                                                      ConditionOperatorTypeEnum.COND_GREATER, name)
        self.parameters = ['condition_type', 'k_data']
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_VOLUME_MONOMIAL_CLIMAX.value: self._judge_volume_climax,
            ConditionTypeEnum.COND_VOLUME_MONOMIAL_SHRINK.value: self._judge_volume_shrink,
            ConditionTypeEnum.COND_VOLUME_MONOMIAL_NONE.value: self._judge_volume_none,
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_LIVELY.value: self._judge_volume_lively
        }
        self.volume_indicator = CommonIndicator(VariableTypeEnum.K_DATA_VOLUME)
        self.data_list = None
        self.ma5 = None
        self.ma10 = None
        self.shareholder_ratio_total = 0

    def prepare(self,  data_list, shareholder_list, float_shareholder_list):
        self.data_list = data_list
        self.ma5 = self.volume_indicator.ma(5, data_list)
        self.ma10 = self.volume_indicator.ma(10, data_list)
        holder_name_list = []
        self.shareholder_ratio_total = 0
        for holder in shareholder_list[-10:]:
            self.shareholder_ratio_total += holder.hold_ratio
            holder_name_list.append(holder.name)
        for holder in float_shareholder_list[-10:]:
            if holder.name not in holder_name_list:
                self.shareholder_ratio_total += holder.hold_ratio

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        param_k_data = kwargs[self.parameters[1]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        try:
            index = self.data_list.index(param_k_data)
        except ValueError:
            return False
        return self._judge_fun_dict[param_condition_type.value](param_k_data, index)

    def _judge_volume_climax(self, k_data, index):
        if self._judge_volume_none(k_data, index):
            return False
        if Variable.get_val(self.variable_type, k_data) > self.ma5[index] > self.ma10[index]:
            return True
        return False

    def _judge_volume_shrink(self, k_data, index):
        # if self._judge_volume_none(k_data, index):
        #     return False
        if Variable.get_val(self.variable_type, k_data) < self.ma5[index] < self.ma10[index]:
            return True
        return False

    def _judge_volume_none(self, k_data, index):
        """
        :param k_data:
        :param index:
        :return:
        """
        if Variable.get_val(self.variable_type, k_data) == 0:
            return True
        if (100 - self.shareholder_ratio_total) == 0:
            # print('Shareholder hold ratio 100: %s' % k_data)
            return True
        turn = Variable.get_val(VariableTypeEnum.K_DATA_TURN, k_data) / (100 - self.shareholder_ratio_total)
        con1 = (self. ma5[index] * turn) / Variable.get_val(self.variable_type, k_data) * 100
        if con1 < 1.0:
            return True
        return False

    def _judge_volume_lively(self, k_data, index):
        if self._judge_volume_none(k_data, index):
            return False
        if Variable.get_val(self.variable_type, k_data) > self.ma10[index]:
            return True
        return False


class VolumeChartPatternCondition(Condition):
    name = 'VolumeChartPatternCondition'
    coe_range_min = 3
    coe_range_max = 10
    coe_lively_ratio = 0.43

    def __init__(self, name=None):
        super(VolumeChartPatternCondition, self).__init__(VariableTypeEnum.K_DATA_VOLUME,
                                                          ConditionOperatorTypeEnum.COND_GREATER, name)
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP.value: self._judge_pattern_heap,
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_AV_HEAP.value: self._judge_pattern_av_heap,
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HALF_DROP_HEAP.value: self._judge_pattern_half_drop_heap,
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HALF_RISE_HEAP.value: self._judge_pattern_half_rise_heap,
            ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_LIVELY.value: self._judge_pattern_lively
        }
        self.condition = VolumeMonomialCondition()
        self.parameters = ['condition_type', 'start_index', 'end_index']
        self.data_list = None
        self.ret_tem_data = None
        self.temp_start_index = None
        self.temp_end_index = None
        self.heap_condition_type_list = [ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP,
                                         ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_AV_HEAP,
                                         ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HALF_DROP_HEAP,
                                         ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HALF_RISE_HEAP]

    def prepare(self, data_list, shareholder_list, float_shareholder_list):
        self.condition.prepare(data_list, shareholder_list, float_shareholder_list)
        self.data_list = data_list
        self.ret_tem_data = None
        pass

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        param_start_index = kwargs[self.parameters[1]]
        param_end_index = kwargs[self.parameters[2]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        data_period_list = self.data_list[param_start_index: param_end_index]
        if param_start_index != self.temp_start_index or param_end_index != self.temp_end_index:
            self.ret_tem_data = None
            self.temp_start_index = param_start_index
            self.temp_end_index = param_end_index

        if param_condition_type not in self.heap_condition_type_list:
            return self._judge_fun_dict[param_condition_type.value](data_period_list)

        if self.ret_tem_data is None:
            ret = self._judge_fun_dict[ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP.value](data_period_list)
            if not ret:
                return ret
        if param_condition_type == ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_HEAP:
            return True
        return self._judge_fun_dict[param_condition_type.value]()

    def _judge_pattern_lively(self, data_period_list):
        lively_count = 0
        length = len(data_period_list)
        for data in data_period_list:
            ret = self.condition.judge(
                condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_LIVELY,
                k_data=data
            )
            if ret:
                lively_count += 1
        return lively_count / length > self.coe_lively_ratio

    def _judge_pattern_heap(self, data_period_list):
        ret_data = []
        index = 0
        while index < len(data_period_list):
            data_i = data_period_list[index]
            ret = self.condition.judge(
                condition_type=ConditionTypeEnum.COND_VOLUME_MONOMIAL_CLIMAX,
                k_data=data_i
            )
            if ret:
                index_end = index + 1
                index_start = index
                for data_j in data_period_list[index_end:]:
                    ret = self.condition.judge(
                        condition_type=ConditionTypeEnum.COND_VOLUME_MONOMIAL_SHRINK,
                        k_data=data_j
                    )
                    if ret:
                        if index_end - index_start < self.coe_range_min:
                            index = index_start
                            break
                        elif index_end - index_start <= self.coe_range_max:
                            index = index_end
                            ret_data.append({
                                'start': self.data_list.index(data_period_list[index_start]),
                                'end': self.data_list.index(data_j)
                            })
                            break
                        elif index_end - index_start > self.coe_range_max:
                            break
                        index_end += 1
                        continue
                    ret = self.condition.judge(
                        condition_type=ConditionTypeEnum.COND_VOLUME_MONOMIAL_CLIMAX,
                        k_data=data_j
                    )
                    if ret:
                        if index_end - index <= 3:
                            index = index_end
                    index_end += 1
            index += 1

        if ret_data:
            self.ret_data = ret_data
            self.ret_tem_data = ret_data
            return True
        return False

    def _judge_pattern_av_heap(self):
        """
           *
          ***
         *****
        *******
        :return:
        """
        ret_data = []
        for data_dict in self.ret_tem_data:
            temp_list = self.data_list[data_dict['start']: data_dict['end'] + 1]
            temp_len = len(temp_list)
            period_len = int(temp_len / 3)
            max_data = max(temp_list, key=Variable.get_fun(self.variable_type))
            temp_index = temp_list.index(max_data)
            if period_len <= temp_index < temp_len - period_len:
                ret_data.append(data_dict)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_half_drop_heap(self):
        """
        *
        ***
        ****
        *****
        :return:
        """
        ret_data = []
        for data_dict in self.ret_tem_data:
            temp_list = self.data_list[data_dict['start']: data_dict['end'] + 1]
            temp_len = len(temp_list)
            period_len = int(temp_len / 3)
            max_data = max(temp_list, key=Variable.get_fun(self.variable_type))
            temp_index = temp_list.index(max_data)
            if period_len > temp_index:
                ret_data.append(data_dict)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

    def _judge_pattern_half_rise_heap(self):
        """
           *
          **
         ***
        ****
        :return:
        """
        ret_data = []
        for data_dict in self.ret_tem_data:
            temp_list = self.data_list[data_dict['start']: data_dict['end'] + 1]
            temp_len = len(temp_list)
            period_len = int(temp_len / 3)
            max_data = max(temp_list, key=Variable.get_fun(self.variable_type))
            temp_index = temp_list.index(max_data)
            if temp_index >= temp_len - period_len:
                ret_data.append(data_dict)
        if ret_data:
            self.ret_data = ret_data
            return True
        return False

