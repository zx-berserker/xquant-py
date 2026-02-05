# -*- coding:utf-8 -*-
"""
date: 2026/01/02
author: Berserker
"""
from quant.spider.tdx.lib.host import hq_hosts, ex_hq_hosts 
from tools.pytdx.hq import TdxHq_API
from tools.pytdx.exhq import TdxExHq_API
from quant.libs.error import XException, ErrorCodeEnum
from quant.libs.log import XLog
from quant.spider.tdx.lib.enum import QuotePeriodEnum
import pandas as pd

class TdxQuery:
    is_connected: bool = False
    api: TdxHq_API = None
    ex_api: TdxExHq_API = None
    _hq_name = None
    _hq_ip = None 
    _hq_port = None
    _ex_hq_name = None
    _ex_hq_ip = None
    _ex_hq_port = None
    @classmethod
    def connect(cls):
        hq_hosts_list = []
        ex_hq_hosts_list = []
        hq_hosts_list.extend(hq_hosts)
        ex_hq_hosts_list.extend(ex_hq_hosts)
        if cls.is_connected:
            return  
        while True:
            if len(hq_hosts_list) == 0:
                raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR,"TdxQuery: hq_hosts is invalid.")
            _hq_name, _hq_ip, _hq_port, _hq_is_new = hq_hosts_list.pop(0)
            cls.api = TdxHq_API(_hq_is_new, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
            ret = cls.api.connect(_hq_ip, _hq_port)
            if ret:
                break
        while True:
            if len(ex_hq_hosts_list) == 0:
                raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR, "TdxQuery: ex_hq_hosts is invalid.")
            _ex_hq_name, _ex_hq_ip, _ex_hq_port, _ex_hq_is_new = ex_hq_hosts_list.pop(0)
            cls.ex_api = TdxExHq_API(_ex_hq_is_new, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
            ret = cls.ex_api.connect(_ex_hq_ip, _ex_hq_port)
            if ret:
                break
        XLog.info("TdxQuery connected to TDX Hq host: ", _hq_name, "(", _hq_ip, ":", _hq_port, ")")
        XLog.info("TdxQuery connected to TDX Ex_Hq host: ", _ex_hq_name, "(", _ex_hq_ip, ":", _ex_hq_port, ")")
        cls._hq_name = _hq_name
        cls._hq_ip = _hq_ip 
        cls._hq_port = _hq_port
        cls._ex_hq_name = _ex_hq_name
        cls._ex_hq_ip = _ex_hq_ip
        cls._ex_hq_port = _ex_hq_port
        cls.is_connected = True
        
    
    @classmethod
    def disconnect(cls):
        if not cls.is_connected:
            return  
        cls.api.disconnect()
        cls.ex_api.disconnect()
        cls.is_connected = False
        cls._hq_name = None
        cls._hq_ip = None 
        cls._hq_port = None
        cls._ex_hq_name = None
        cls._ex_hq_ip = None
        cls._ex_hq_port = None
        XLog.info("TdxQuery disconnect TDX Hq host: ", cls._hq_name, "(", cls._hq_ip, ":", cls._hq_port, ")")
        XLog.info("TdxQuery disconnect TDX Ex_Hq host: ", cls._ex_hq_name, "(", cls._ex_hq_ip, ":", cls._ex_hq_port, ")")

    
    @classmethod
    def get_quote(cls, period:QuotePeriodEnum, market:int, code, start_time:str='20260101', end_time:str='20260201', count:int=100):
        if not cls.is_connected:
            raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR,"TdxQuery: not connected.")
        
        ret_data = []
        date_time_start = str(pd.to_datetime(start_time, format='%Y%m%d'))
        date_time_end = str(pd.to_datetime(end_time+' 23:59', format='%Y%m%d %H:%M'))
        start = 0
        while True:
            if market in [0,1]: #TODO 上证、深证
                data = cls.api.get_security_bars(period.value, market, code, start, count)
            else: #TODO 期货 扩展行情
                data = cls.ex_api.get_instrument_bars(period.value, market, code, start, count)
            if not data:
                break
            ret_data.extend(data)
            temp_df = cls.api.to_df(data)
            length = len(temp_df)
            if temp_df.at[length-1, 'datetime'] < date_time_start or length < count:
                break
            start += count
        if market in [0,1]:
            data_df = cls.api.to_df(ret_data)
        else:
            data_df = cls.ex_api.to_df(ret_data)
        
        data_df.loc[:,'time'] = pd.to_datetime(data_df['datetime'])
        data_df.set_index('datetime', inplace=True)
        data_df.sort_index(inplace=True)
        data_df.loc[:,'pct_chg'] = (data_df['close'] - data_df['close'].shift(1)) / data_df['close'].shift(1) * 100
        data_df.loc[data_df.index[0], 'pct_chg'] = (data_df.iloc[0]['close'] - data_df.iloc[0]['open']) / data_df.iloc[0]['open'] * 100
        data_df = data_df[(data_df['time'] >= date_time_start) & (data_df['time'] <= date_time_end)]
        if period == QuotePeriodEnum.HOURLY:
            data_df.loc[:,'time'] = data_df['time'].dt.strftime('%Y-%m-%d %H:%M')
        else:
            data_df.loc[:,'time'] = data_df['time'].dt.strftime('%Y-%m-%d')
        
        data_df.loc[:,'open'] = data_df['open'].round(2)
        data_df.loc[:,"close"] = data_df["close"].round(2)
        data_df.loc[:,'high'] = data_df['high'].round(2)
        data_df.loc[:,'low'] = data_df['low'].round(2)
        data_df.loc[:,'pct_chg'] = data_df['pct_chg'].round(2)
        data_df.loc[:,'turn'] = 0
        data_df.loc[:,'hold'] = data_df['position']
        data_df.loc[:,'volume'] = data_df['trade']
        data_df.loc[:,'amount'] = 0


        ret_data_df = data_df[
            [
                "time",
                "open",
                "close",
                "high",
                "low",
                "volume",
                "amount",
                "pct_chg",
                "turn",
                "hold",
            ]
        ]
        return ret_data_df
        


if __name__ == '__main__':
    TdxQuery.connect()
    k_data = TdxQuery.get_quote(QuotePeriodEnum.DAILY, 66, "SIL9", "20260128", "20260203", count=2)
    print(k_data)
    # data = TdxQuery.ex_api.get_instrument_bars(QuotePeriodEnum.DAILY.value, 30, "AUL9", start=0, count=10) 96
    # print(data)
    # start = 0
    # all_data = []
    # while True: 
    #     data = TdxQuery.ex_api.get_instrument_info(start)
    #     all_data.extend(data)
    #     start += 100
    #     if start >= 62465:
    #         break
    # data_df = TdxQuery.ex_api.to_df(all_data)
    # data_df.to_csv("./instrument_info.csv", index=True, encoding='utf-8-sig')
    # print(data_df)
    TdxQuery.disconnect()

    