# -*- encoding:utf-8 -*-
"""
date: 2020/8/25
author: Berserker
"""

from src.strategy.base import VariableTypeEnum, Variable
import numpy as np
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum


class BaseIndicator(object):
    
    #  def ref(self, ref_count, np_ary):
    #     if ary is None:
    #         raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
    #     temp_list = np_ary
    #     ref_list = [temp_list[0] for i in range(0, ref_count)]
    #     ref_list.extend(temp_list)
    #     return np.asanyarray(ref_list[:len(data_list)])
    @staticmethod
    def ma(cls, period, np_ary):
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        
        data_ary = np_ary
        weight_ary = np.ones(period) / period
        sma_ary = np.convolve(data_ary, weight_ary, mode="full")[:len(data_ary)]

        for i in range(1, period):
            sma_ary[i] = data_ary[0:i].sum() / (i + 1)
        return sma_ary
    
    @staticmethod
    def ma_slope(cls, period, np_ary):
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        ma_ary = cls.ma(period, np_ary)
        ref_ary = cls.ref(1, ma_ary)
        div_ary = np.true_divide(ma_ary, ref_ary, out=np.ones_like(ma_ary), where=ref_ary != 0)
        ma_slop_ary = (div_ary - 1) * 100
        return ma_slop_ary

    @staticmethod
    def ma_slope_atan(cls, period, np_ary):
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        ma_slope_ary = cls.ma_slope(period, np_ary)
        atan_ary = np.arctan(ma_slope_ary)
        return atan_ary

    @staticmethod
    def dma(cls, np_ary, coe_ary):
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")         
        for i in range(1, len(np_ary)):
            np_ary[i] = coe_ary[i] * np_ary[i] + (1 - coe_ary[i]) * np_ary[i-1]
        return np_ary
 
    @staticmethod    
    def sma(cls, period, np_ary, coefficient):
        if coefficient > period:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "m is greater than period !")
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        
        data_ary = np_ary
        weight_ary = np.ones(period) / period * (period - coefficient)
        weight_ary[period-1] = coefficient / period
        sma_ary = np.convolve(data_ary, weight_ary, mode="full")[:len(data_ary)]
        for i in range(1, period):
            sma_ary[i] = data_ary[0:i].sum() / (i + 1)
        return sma_ary

    @staticmethod
    def _ema_period(cls, np_ary):
        n = len(np_ary)
        a = 2/(n+1)
        data_ary = np.zeros(n)
        for i in range(n):
            data_ary[i] = np_ary[i] if i == 0 else a*np_ary[i]+(1-a)*data_ary[i-1]
        return data_ary[-1]

    @staticmethod    
    def ema(cls, period, np_ary):
        if np_ary is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        data_ary = np.full(np_ary.shape, np_ary.nan)
        for i in range(period-1, len(np_ary)):
            data_ary[i] = cls._ema_period(np_ary[i+1-period:i+1])
        return data_ary
        # temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        # length = len(temp_list)
        # ema_list = []
        # ema_begin_ary = np.mean(temp_list[0: period - 1])
        # ema_list.append(temp_list[0])
        # for i in range(1, length):
        #     ema = 0
        #     if i == period:
        #         ema = (2 * temp_list[i] + (period - 1) * ema_begin_ary) / (period + 1)
        #     else:
        #         ema = (2 * temp_list[i] + (period - 1) * ema_list[-1]) / (period + 1)
        #     ema_list.append(ema)

        # return np.array(ema_list)


class CommonIndicator(object):

    def __init__(self, variable_type=VariableTypeEnum.K_DATA_CLOSE):
        self.variable_type = variable_type

    def ref(self, ref_count, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        ref_list = [temp_list[0] for i in range(0, ref_count)]
        ref_list.extend(temp_list)
        return np.asanyarray(ref_list[:len(data_list)])

    def ma(self, period, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        data_ary = np.asanyarray(temp_list)
        weight_ary = np.ones(period) / period
        sma_ary = np.convolve(data_ary, weight_ary, mode="full")[:len(data_ary)]

        for i in range(1, period):
            sma_ary[i] = data_ary[0:i].sum() / (i + 1)
        return sma_ary

    def ma_slope(self, period, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        ma_ary = self.ma(period, data_list)
        ref_ary = self.ref(1, ma_ary)
        div_ary = np.true_divide(ma_ary, ref_ary, out=np.ones_like(ma_ary), where=ref_ary != 0)
        ma_slop_ary = (div_ary - 1) * 100
        return ma_slop_ary

    def ma_slope_atan(self, period, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        ma_slope_ary = self.ma_slope(period, data_list)
        atan_ary = np.arctan(ma_slope_ary)
        return atan_ary

    def sma(self, period, data_list, coefficient):
        if coefficient > period:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "m is greater than period !")
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        data_ary = np.asanyarray(temp_list)
        weight_ary = np.ones(period) / period * (period - coefficient)
        weight_ary[period-1] = coefficient / period
        sma_ary = np.convolve(data_ary, weight_ary, mode="full")[:len(data_ary)]
        for i in range(1, period):
            sma_ary[i] = data_ary[0:i].sum() / (i + 1)
        return sma_ary

    def ema(self, period, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        length = len(temp_list)
        ema_list = []
        ema_begin_ary = np.mean(temp_list[0: period - 1])

        ema_list.append(temp_list[0])
        for i in range(1, length):
            ema = 0
            if i == period:
                ema = (2 * temp_list[i] + (period - 1) * ema_begin_ary) / (period + 1)
            else:
                ema = (2 * temp_list[i] + (period - 1) * ema_list[-1]) / (period + 1)
            ema_list.append(ema)

        return np.array(ema_list)

    def macd(self, data_list, short_period=12, long_period=26, signal_period=9):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        ema12_ary = self.ema(short_period, data_list)
        ema26_ary = self.ema(long_period, data_list)
        diff_ary = ema12_ary - ema26_ary
        dea_ary = self.ema(signal_period, diff_ary)
        macd_ary = 2 * (diff_ary - dea_ary)
        return macd_ary, diff_ary, dea_ary

    def _rsi_gain_lost(self, data_list):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        temp_list = Variable.data_list_to_variable_list(self.variable_type, data_list)
        gain_list = [0]
        loss_list = [0]
        length = len(temp_list)
        for i in range(1, length):
            gap = temp_list[i] - temp_list[i - 1]
            if gap > 0:
                gain_list.append(gap)
                loss_list.append(0)
            else:
                gain_list.append(0)
                loss_list.append(gap)
        return gain_list, loss_list

    def rsi(self, data_list, short_period=6, medium_period=12, long_period=24):
        if data_list is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "the data_list is none !")
        gain_list, loss_list = self._rsi_gain_lost(data_list)

        short_gain_ema = self.ema(short_period, gain_list)
        medium_gain_ema = self.ema(medium_period, gain_list)
        long_gain_ema = self.ema(long_period, gain_list)

        short_loss_ema = self.ema(short_period, loss_list)
        medium_loss_ema = self.ema(medium_period, loss_list)
        long_loss_ema = self.ema(long_period, loss_list)

        rsi_short = short_gain_ema / (short_gain_ema - short_loss_ema)
        rsi_medium = medium_gain_ema / (medium_gain_ema - medium_loss_ema)
        rsi_long = long_gain_ema / (long_gain_ema - long_loss_ema)
        return rsi_short, rsi_medium, rsi_long



