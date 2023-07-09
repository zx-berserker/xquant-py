# -*- encoding:utf-8 -*-
"""
date: 2020/9/4
author: Berserker
"""
from quant.strategy.base import VariableTypeEnum, Variable
import numpy as np
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from .common_indicator import BaseIndicator
from .indicator_tools import IndicatorTools, IndicatorToolsProcessType


class IndicatorData(object):

    def __init__(self, data_ary=None, data=None):
        if data_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")        
        self.data_ary = data_ary
        self.data = data
        self.data_type_list = []
        self.data_ary_dic = {}
        
    def update(self, type_list):
        for tp in type_list:
            if tp not in self.data_ary_dic:
                if tp > VariableTypeEnum.ARRAY_DATA_TYPE:
                    self.data_ary_dic[tp] = np.asanyarray(Variable.data_list_to_variable_list(tp, self.data_ary))
                else:
                    self.data_ary_dic[tp] = Variable.get_val(tp, self.data)
                self.data_type_list.append(tp)
        return self
    
    def get_data(self, data_type):
        return self.data_ary_dic[data_type]


class PriceIndicator(object):

    def __init__(self) -> None:
        pass
    
    @staticmethod                    
    def cyc(indicator_data, short_period=2, medium_period=10, long_period=42):
        data_type_list = [VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN,
                          VariableTypeEnum.K_DATA_VOLUME, VariableTypeEnum.K_DATA_LOW,
                          VariableTypeEnum.K_DATA_HIGH, VariableTypeEnum.K_DATA_AMOUNT,
                          VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN,
                          VariableTypeEnum.STOCK_INFO_CAPITAL]
        data = IndicatorData.update(indicator_data, data_type_list)
        high_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_HIGH)
        low_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_LOW)
        open_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_OPEN)
        close_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_CLOSE)
        amount_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_AMOUNT)
        volume_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_VOLUME)
        capital = IndicatorData.get_data(data, VariableTypeEnum.STOCK_INFO_CAPITAL)
       
        vard_ary = (3*high_ary+low_ary+open_ary+2*close_ary)/7
        varc_ary = amount_ary/volume_ary/100
        var_s_ary = np.convolve(amount_ary, np.ones(short_period, dtype=int), 'valid')/varc_ary/100
        var_m_ary = np.convolve(amount_ary, np.ones(medium_period, dtype=int), 'valid')/varc_ary/100
        var_l_ary = np.convolve(amount_ary, np.ones(long_period, dtype=int), 'valid')/varc_ary/100  
        cyc_short = BaseIndicator.dma(vard_ary, volume_ary/var_s_ary/100)
        cyc_medium = BaseIndicator.dma(vard_ary, volume_ary/var_m_ary/100)
        cyc_long = BaseIndicator.dma(vard_ary, volume_ary/var_l_ary/100)
        cyc_w = BaseIndicator.dma(vard_ary, volume_ary/capital/100)
        return cyc_short, cyc_medium, cyc_long, cyc_w
    
    @staticmethod
    def atom_price_avg(indicator_data):
        data_type_list = [VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN,
                          VariableTypeEnum.K_DATA_LOW, VariableTypeEnum.K_DATA_HIGH,
                          VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN]
        data = IndicatorData.update(indicator_data, data_type_list)
        high_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_HIGH)
        low_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_LOW)
        open_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_OPEN)
        close_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_CLOSE)
     
        return (3*high_ary+low_ary+open_ary+2*close_ary)/7
    
    @staticmethod
    def dma_coe_by_turn(indicator_data, coe_turn=100):
        data_type_list = [VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN,
                          VariableTypeEnum.K_DATA_LOW, VariableTypeEnum.K_DATA_HIGH,
                          VariableTypeEnum.K_DATA_CLOSE, VariableTypeEnum.K_DATA_OPEN,
                          VariableTypeEnum.K_DATA_TURN]
        data = IndicatorData.update(indicator_data, data_type_list)
        price_ary = PriceIndicator.atom_price_avg(indicator_data)
        turn_ary = IndicatorData.get_data(data, VariableTypeEnum.K_DATA_TURN)
        begin = IndicatorTools.section_search(
            IndicatorToolsProcessType.ACCUMALATE,
            lambda param: param >= coe_turn,
            turn_ary)
        coe = 1000000
        flex_ary = np.ones(int(coe_turn * coe)) * np.average(price_ary[0:begin])
        dma_ary = flex_ary[0:begin]
        temp_ary = None
        for index in range(len(price_ary[begin:])):
            i = begin + index
            temp_ary = np.append(np.ones(int(turn_ary[i] * coe)) * price_ary[i], flex_ary)
            dma_ary = np.append(dma_ary, np.average(temp_ary[0:int(coe_turn*coe)]))
            flex_ary = temp_ary[0:int(coe_turn*coe)]
        return dma_ary
