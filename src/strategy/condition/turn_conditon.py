# -*- encoding:utf-8 -*-
"""
date: 2022/11/22
author: Berserker
"""
from .base import Condition
import numpy as np
from enum import IntEnum
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum
from src.strategy.base import Variable, VariableTypeEnum
from .base import Condition, ConditionTypeEnum, ConditionOperatorTypeEnum
from src.strategy.technical_analysis_indicator.common_indicator import CommonIndicator


class TurnConditionType(IntEnum):
    PRICE_DMA_SECTION_BY_TIME = 1
    PRICE_DMA_SECTION_BY_TURN = 2


class TurnSectionConditon(Condition):
    name = 'CompleteTurnSectionConditon'
    
    def __init__(self, name=None):
        super(TurnSectionConditon, self).__init__(VariableTypeEnum.K_DATA_TURN,
                                                  ConditionOperatorTypeEnum.COND_GREATER_EQUAL, name)
        self.parameters = ['condition_type', 'section_turn', 'begin', 'end']
        self.data_list = None
        self.turn_ary = None
        self.ret_list = []
        
    def prepare(self, data_list):
        self.data_list = data_list
        self.turn_ary = np.asanyarray(Variable.data_list_to_variable_list(VariableTypeEnum.K_DATA_TURN, data_list))
               
    def judge(self, *args, **kwargs):
        for param in self.parameters:
            if param not in kwargs.keys():
                raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, 'The ' + param + ' is invalid !')
        condition_type = kwargs[self.parameters[0]]
        section_turn = kwargs[self.parameters[1]]
        begin = kwargs[self.parameters[2]]
        end = kwargs[self.parameters[2]]
        cum_ary = np.cumsum(self.turn_ary, dtype=float)
        pass
    
    
    def _search_complete_turn_section(self, begin):
        pass