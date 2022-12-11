# -*- encoding:utf-8 -*-
"""
date: 2020/8/24
author: Berserker
"""
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.strategy.base import Variable, VariableTypeEnum
from .base import Condition, ConditionTypeEnum, ConditionOperatorTypeEnum


class ShootUpCondition(Condition):
    """
    todo: change class for multi conditions
    ShootUpCondition: found from data list where the value of later data is bigger then front's dramatically
    """
    name = 'ShootUpCondition'

    def __init__(self, variable_type, operator_type=ConditionOperatorTypeEnum.COND_GREATER, name=None):
        """
        :param variable_type: VariableTypeEnum
        :param name: condition name
        self.parameters: []
            k_data: k_data object
        """
        super(ShootUpCondition, self).__init__(variable_type, operator_type, name)
        self.parameters = ['k_data', ]
        self.times = None
        self.data_list = None

    def prepare(self, data_list, times):
        """
        :param data_list: data_list: the list of data (eg. k_data_daily)
        :param times: the times of value is as big as previous value
        :return:
        """
        self.data_list = data_list
        self.times = times

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_k_data = kwargs[self.parameters[0]]
        try:
            index = self.data_list.index(param_k_data)
        except ValueError:
            return False
        if index == 0:
            return False
        ret = self.cond_operator(
            Variable.get_val(self.variable_type, param_k_data),
            Variable.get_val(self.variable_type, self.data_list[index - 1]) * self.times
        )
        return ret


class RecentCompareCondition(Condition):
    """
    RecentCompareCondition:
    """
    name = "RecentCompareMaxValueCondition"

    def __init__(self, variable_type, operator_type=ConditionOperatorTypeEnum.COND_GREATER, name=None):
        """
        :param variable_type: VariableTypeEnum
        :param name: condition name
        self.parameters: []
            period_length: the length of data deal with
            start_index: the start index of data list deal with
            end_index: the end index of data list deal with
        """
        super(RecentCompareCondition, self).__init__(variable_type, operator_type, name)
        self.parameters = ['condition_type', 'start_index', 'end_index', 'coefficient']
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_RECENT_COMPARE_MAXIMUM.value: self._judge_compare_maximum,
            ConditionTypeEnum.COND_RECENT_COMPARE_MINIMUM.value: self._judge_compare_minimum,
            ConditionTypeEnum.COND_RECENT_COMPARE_FLUCTUATION.value: self._judge_compare_fluctuation
        }
        self.data_list = None

    def prepare(self, data_list):
        """

        :param data_list: the list of data (eg. k_data_daily)
        :return:
        """
        self.data_list = data_list

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        param_start_index = kwargs[self.parameters[1]]
        param_end_index = kwargs[self.parameters[2]]
        param_coefficient = kwargs[self.parameters[3]]
        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')

        data_period_list = self.data_list[param_start_index: param_end_index]
        return self._judge_fun_dict[param_condition_type.value](param_coefficient, data_period_list)

    def _judge_compare_maximum(self, coefficient, data_period_list):
        """
        default operator >
        :param coefficient: max / recent > coefficient
        :return:
        """
        data_max = max(data_period_list, key=Variable.get_fun(self.variable_type))
        ret = self.cond_operator(
            Variable.get_val(self.variable_type, data_max),
            Variable.get_val(self.variable_type, data_period_list[-1]) * coefficient
        )
        return ret

    def _judge_compare_minimum(self, coefficient, data_period_list):
        """
        default operator >
        :param coefficient: recent / mini > coefficient
        :return:
        """
        data_min = min(data_period_list, key=Variable.get_fun(self.variable_type))
        ret = self.cond_operator(
            Variable.get_val(self.variable_type, data_period_list[-1]),
            Variable.get_val(self.variable_type, data_min) * coefficient
        )
        return ret

    def _judge_compare_fluctuation(self, coefficient, data_period_list):
        """
        default operator >
        :param coefficient: (max - min) / (recent - min) > coefficient
        :return:
        """
        data_max = max(data_period_list, key=Variable.get_fun(self.variable_type))
        data_min = min(data_period_list, key=Variable.get_fun(self.variable_type))
        fluctuation = Variable.get_val(self.variable_type, data_max) - Variable.get_val(self.variable_type, data_min)
        recent = Variable.get_val(self.variable_type, data_period_list[-1]) - \
            Variable.get_val(self.variable_type, data_min)
        ret = self.cond_operator(fluctuation, recent * coefficient)
        return ret


class SubintervalCondition(Condition):
    name = "SubintervalCondition"

    def __init__(self, variable_type, operator_type=ConditionOperatorTypeEnum.COND_GREATER, name=None):
        super(SubintervalCondition, self).__init__(variable_type, operator_type, name)
        self._judge_fun_dict = {
            ConditionTypeEnum.COND_SUBINTERVAL_FLUCTUATION.value: self._judge_subinterval_fluctuation,
            ConditionTypeEnum.COND_SUBINTERVAL_PCT_CHG.value: self._judge_subinterval_pct_chg
        }
        self.parameters = ['condition_type', 'start_index', 'end_index', 'coefficient']
        self.data_list = None

    def prepare(self, data_list):
        self.data_list = data_list

    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        param_condition_type = kwargs[self.parameters[0]]
        param_start_index = kwargs[self.parameters[1]]
        param_end_index = kwargs[self.parameters[2]]
        param_coefficient = kwargs[self.parameters[3]]
        data_period_list = self.data_list[param_start_index: param_end_index]

        if param_condition_type.value not in self._judge_fun_dict.keys():
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The condition_type is invalid !')
        return self._judge_fun_dict[param_condition_type.value](param_coefficient, data_period_list)

    def _judge_subinterval_fluctuation(self, coefficient, data_period_list):
        """
        default operator >
        :param coefficient: max / min >  coefficient
        :return:
        """
        data_max = max(data_period_list, key=Variable.get_fun(self.variable_type))
        data_min = min(data_period_list, key=Variable.get_fun(self.variable_type))
        ret = self.cond_operator(
            Variable.get_val(self.variable_type, data_max),
            Variable.get_val(self.variable_type, data_min) * coefficient
        )
        return ret

    def _judge_subinterval_pct_chg(self, coefficient, data_period_list):
        data_max = max(data_period_list, key=Variable.get_fun(self.variable_type))
        data_min = min(data_period_list, key=Variable.get_fun(self.variable_type))
        index_max = self.data_list.index(data_max)
        index_min = self.data_list.index(data_min)
        if index_max > index_min:
            ret = Variable.get_val(self.variable_type, data_max) / Variable.get_val(self.variable_type, data_min) - 1
        else:
            ret = Variable.get_val(self.variable_type, data_min) / Variable.get_val(self.variable_type, data_max) - 1
        return self.cond_operator(ret, coefficient)



