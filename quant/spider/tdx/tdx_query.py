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
import requests
import json
import time
from datetime import timedelta
from pandas import Timestamp
from config.secure import HOST
import warnings
warnings.simplefilter(action='error', category=FutureWarning)


class TdxQuery:
    is_active = True
    _stock_market_list = [0,1,31]
    is_connected: bool = False
    api: TdxHq_API = None
    ex_api: TdxExHq_API = None
    ex_future_api: TdxExHq_API = None
    _hq_name = None
    _hq_ip = None 
    _hq_port = None
    _ex_hq_name = None
    _ex_hq_ip = None
    _ex_hq_port = None
    _ex_hq_future_name = None
    _ex_hq_future_ip = None
    _ex_hq_future_port = None
    _request_base_url = f'http://{HOST}:8020/api/v1/tdx'
    requset_market = [
        {
            "name": '沪深A股',
            "code": '50',
        },
        {
            "name": 'ETF基金',
            "code": '31',
        },
        {
            "name": '港股',
            "code": '102',
        },
        {
            "name": '重点指数',
            "code": '9',
        }
    ]
    tdx_query_count = 100
    _bad_query_count = 0

    @classmethod
    def connect(cls):
        hq_hosts_list = []
        ex_hq_hosts_list = []
        ex_hq_future_hosts_list = []

        
        if cls.is_connected or not cls.is_active:
            return  
        while cls.is_active:
            if len(hq_hosts_list) == 0:
                hq_hosts_list.extend(hq_hosts)
                # raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR,"TdxQuery: hq_hosts is invalid.")
            _hq_name, _hq_ip, _hq_port, _hq_is_new = hq_hosts_list.pop(0)
            try:
                cls.api = TdxHq_API(_hq_is_new, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
                ret = cls.api.connect(_hq_ip, _hq_port)
                if ret:
                    break
            except:
                XLog.error("TdxHq_API connect error. name: %s, ip: %s" % (_hq_name, _hq_ip))
                continue
        while cls.is_active:
            if len(ex_hq_hosts_list) == 0:
                ex_hq_hosts_list.extend(ex_hq_hosts[0:5])
            _ex_hq_name, _ex_hq_ip, _ex_hq_port, _ex_hq_is_new = ex_hq_hosts_list.pop(0)
            try:
                cls.ex_api = TdxExHq_API(_ex_hq_is_new, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
                ret = cls.ex_api.connect(_ex_hq_ip, _ex_hq_port)
                if ret:
                    break
            except:
                XLog.error("TdxExHq_API connect error. name: %s, ip: %s" % (_ex_hq_name, _ex_hq_ip))
                continue

        while cls.is_active:
            if len(ex_hq_future_hosts_list) == 0:
                ex_hq_future_hosts_list.extend(ex_hq_hosts[-2:])
            _ex_hq_future_name, _ex_hq_future_ip, _ex_hq_future_port, _ex_hq_future_is_new = ex_hq_future_hosts_list.pop(0)
            try:
                cls.ex_future_api = TdxExHq_API(_ex_hq_future_is_new, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
                ret = cls.ex_future_api.connect(_ex_hq_future_ip, _ex_hq_future_port)
                if ret:
                    break
            except:
                XLog.error("TdxExHq_API connect error. name: %s, ip: %s" % (_ex_hq_name, _ex_hq_ip))
                continue

        cls._hq_name = _hq_name
        cls._hq_ip = _hq_ip 
        cls._hq_port = _hq_port
        cls._ex_hq_name = _ex_hq_name
        cls._ex_hq_ip = _ex_hq_ip
        cls._ex_hq_port = _ex_hq_port
        cls._ex_hq_future_name = _ex_hq_future_name
        cls._ex_hq_future_ip = _ex_hq_future_ip
        cls._ex_hq_future_port = _ex_hq_future_port
        cls.is_connected = True
        XLog.info("TdxQuery connected to TDX Hq host: ", _hq_name, "(", _hq_ip, ":", _hq_port, ")")
        XLog.info("TdxQuery connected to TDX Ex_Hq host: ", _ex_hq_name, "(", _ex_hq_ip, ":", _ex_hq_port, ")")
        XLog.info("TdxQuery connected to TDX Ex_Hq Future host: ", _ex_hq_future_name, "(", _ex_hq_future_ip, ":", _ex_hq_future_port, ")")
    
    @classmethod
    def disconnect(cls):
        if not cls.is_connected:
            return  
        try:
            cls.api.disconnect()
            cls.ex_api.disconnect()
            cls.ex_future_api.disconnect()
        except:
            pass
        cls._hq_name = None
        cls._hq_ip = None 
        cls._hq_port = None
        cls._ex_hq_name = None
        cls._ex_hq_ip = None
        cls._ex_hq_port = None
        cls._ex_hq_future_name = None
        cls._ex_hq_future_ip = None
        cls._ex_hq_future_port = None
        cls.is_connected = False
        XLog.info("TdxQuery disconnect TDX Hq host: ", cls._hq_name, "(", cls._hq_ip, ":", cls._hq_port, ")")
        XLog.info("TdxQuery disconnect TDX Ex_Hq host: ", cls._ex_hq_name, "(", cls._ex_hq_ip, ":", cls._ex_hq_port, ")")
        XLog.info("TdxQuery connected to TDX Ex_Hq Future host: ", cls._ex_hq_future_name, "(", cls._ex_hq_future_ip, ":", cls._ex_hq_future_port, ")")
        

    
    @classmethod
    def _get_quote(cls, period:QuotePeriodEnum, market:int, code, start_time:str, end_time:str, count:int=100):
        ret_data = []
        if not cls.is_active:
            return ret_data
        if not cls.is_connected:
            raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR,"TdxQuery: not connected.")
        
        if start_time == '' or  end_time == '':
            date_time_start = None
            date_time_end = None
        else:
            date_time_start = str(pd.to_datetime(start_time, format='%Y%m%d'))
            date_time_end = str(pd.to_datetime(end_time+' 23:59:59', format='%Y%m%d %H:%M:%S'))
        start = 0

        if period == QuotePeriodEnum.MINUTELY10:
            category = QuotePeriodEnum.MINUTELY1.value
            start_count = count*10
        else:
            category = period.value
            start_count = count

        
        hk_market = None
        while cls.is_active:
            if market in [0,1]: #TODO 深证、上证
                data = cls.api.get_security_bars(category, market, code, start, cls.tdx_query_count)
            elif market in [31,27,71]: #HK
                if market == 31 and hk_market is None:
                    first_temp = cls.ex_api.get_instrument_bars(category, 71, code, start, 3)
                    if len(first_temp)>0:
                        hk_market = 71
                    else:
                        hk_market = 31
                else:
                    hk_market = market
                data = cls.ex_api.get_instrument_bars(category, hk_market, code, start, cls.tdx_query_count)

            else: #TODO 期货 扩展行情
                data = cls.ex_future_api.get_instrument_bars(category, market, code, start, cls.tdx_query_count)
            if not data:
                break
            ret_data.extend(data)
            temp_df = cls.api.to_df(data)
            length = len(temp_df)
            start += length
            if date_time_start and (temp_df.at[length-1, 'datetime'] < date_time_start or length < cls.tdx_query_count):
                break
            elif date_time_start is None and (start > start_count or length < cls.tdx_query_count):
                break
            
        if market in [0,1]:
            data_df:pd.DataFrame = cls.api.to_df(ret_data)
        else:
            data_df:pd.DataFrame = cls.ex_api.to_df(ret_data)

        
        # data_df.loc[:,'datetime'] = pd.to_datetime(data_df['datetime'])
        
        def data_time_fix(data:str):
            value = pd.to_datetime(data, format='%Y-%m-%d %H:%M')
            if (value.hour>19) and ((value.hour<23) or ((value.hour==23) and (value.minute<=59))):
                days = 1
                while cls.is_active:
                    temp_time_str = (value - timedelta(days=days)).strftime('%Y-%m-%d')
                    temp_time_end = temp_time_str + " 16:00:00"
                    tmep_time_start = temp_time_str + " 09:00:00"
                    temp_df = data_df[(data_df['datetime']>tmep_time_start) & (data_df['datetime']<temp_time_end)]
                    if len(temp_df) == 0:
                        temp_df_2 = data_df[data_df['datetime']<tmep_time_start]
                        if len(temp_df_2) > 0:
                            days += 1
                            continue
                        else:
                            return (value - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        ret_str = "%s %02d:%02d:%02d" % (temp_time_str, value.hour, value.minute, value.second)
                        return  ret_str
            else:
                # return data
                return str(value.strftime('%Y-%m-%d %H:%M:%S'))

        data_df.loc[:,'datetime'] = data_df['datetime'].apply(data_time_fix)
        
        data_df.loc[:,'time'] = pd.to_datetime(data_df['datetime'])
        # data_df.loc[:,'time'] = data_df['datetime']
        data_df.loc[:,'datetime'] = pd.to_datetime(data_df['datetime'])
        data_df = data_df.copy().infer_objects(copy=False).set_index('datetime').sort_index()
        if period == QuotePeriodEnum.MINUTELY10:
            args = {
                'open': 'first',    # 开盘价取该周期的第一个
                'high': 'max',      # 最高价取该周期的最大值
                'low': 'min',       # 最低价取该周期的最小值
                'close': 'last',    # 收盘价取该周期的最后一个
                # 'trade': 'sum',       # 成交量求和
                'amount': 'sum',     # 成交额求和
                'time': 'last',
                # 'position': 'sum',
            }
            if market in [0,1]:
                args['vol'] = 'sum'
            else:
                args['position'] = 'sum'
                args['trade'] = 'sum'
            data_df = data_df.resample('10min',label='right', closed='right').agg(args).dropna().infer_objects(copy=False) # 去掉没有数据的空行


        data_df.loc[:,'pct_chg'] = (data_df['close'] - data_df['close'].shift(1)) / data_df['close'].shift(1) * 100
        data_df.loc[data_df.index[0], 'pct_chg'] = (data_df.iloc[0]['close'] - data_df.iloc[0]['open']) / data_df.iloc[0]['open'] * 100
        
        if date_time_start:
            data_df = data_df[(data_df['time'] >= date_time_start) & (data_df['time'] <= date_time_end)].copy()
        else:
            data_df = data_df.tail(count).copy()
        if len(data_df) > 0:
            data_df.loc[:,'open'] = data_df['open'].round(2)
            data_df.loc[:,"close"] = data_df["close"].round(2)
            data_df.loc[:,'high'] = data_df['high'].round(2)
            data_df.loc[:,'low'] = data_df['low'].round(2)
            data_df.loc[:,'pct_chg'] = data_df['pct_chg'].round(2)
            data_df.loc[:,'turn'] = 0
            if market in [0,1]:
                data_df.loc[:,'hold'] = 0
                data_df.loc[:,'volume'] = data_df['vol']
            else:
                data_df.loc[:,'hold'] = data_df['position']
                data_df.loc[:,'volume'] = data_df['trade']
                data_df.loc[:,'amount'] = 0
        else:
            ret_data_df = data_df
            return data_df

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
    

    @classmethod
    def get_realtime_quote(cls, period:QuotePeriodEnum, market:int, code, count:int=240) -> list:
        data_list = []
        if not cls.is_active:
            return data_list
        if not cls.is_connected:
            raise XException(ErrorCodeEnum.CODE_SYSTEM_ERROR,"TdxQuery: not connected.")
       
        data_df = cls._get_quote(period, market, code, '', '', count)
        for index, row in data_df.iterrows():
            time = str(row["time"].strftime('%Y-%m-%d %H:%M:%S'))
            data_list.append({
                "Date": time,
                "Open": row["open"],
                "Close": row["close"],
                "High": row["high"],
                "Low": row["low"],
                "Volume": row["volume"],
                "Amount": row["amount"],
                # "pct_chg": row["pct_chg"],
                # "turn": row["turn"],
                # "hold": row["hold"],                
            })
        return data_list


    @classmethod
    def get_quote(cls, period:QuotePeriodEnum, market:int, code, start_time:str='20260101', end_time:str='20260201', count:int=100) -> pd.DataFrame | list:
        data = pd.DataFrame()
        while cls.is_active:
            try:
                if market is not None:
                    data = cls._get_quote(period, market, code, start_time, end_time, count)
                else: 
                    data = cls._get_stock_quote(code, period, start_time, end_time)
            except Exception as e:
                XLog.error(e)
                if market is not None:
                    try:
                        cls.disconnect()
                    except:
                        pass
                    cls.connect()
                time.sleep(5)
                continue
            break
        return data

    @classmethod
    def _get_stock_quote(cls, code:str, period:QuotePeriodEnum, start_time:str='20260101', end_time:str='20260201'):
        params = {
            "code": code,
            "startDate": start_time,
            "endDate": end_time,
            "period": period.name,
        }
        url = cls._request_base_url + '/quote_list'
        r = requests.get(url, timeout=10, params=params, verify=False)
        data_json = r.json()
        data = json.loads(data_json['data'])
        return data
    
    @classmethod
    def get_product_list(cls, market:str):
        params = {
             "market": market,  # 0:上海
        }
        url = cls._request_base_url + '/product_list'
        r = requests.get(url, timeout=10, params=params, verify=False)
        data_json = r.json()
        data = json.loads(data_json['data'])
        return data
    
    @classmethod
    def is_bad_query(cls, ret:bool=False):
        if ret:
            cls._bad_query_count += 1
        else:
            cls._bad_query_count = 0

        if cls._bad_query_count > 200:
            cls.disconnect()

if __name__ == '__main__':
    TdxQuery.connect()
    market = 30
    stock_code = "BUL9"
    # data = TdxQuery.get_quote(QuotePeriodEnum.HOURLY,market,stock_code, "20260320", "20260320", count=100)

    data = TdxQuery.get_realtime_quote(QuotePeriodEnum.MINUTELY15, market, stock_code,count=20)
    print(data)
    # data = TdxQuery.ex_api.get_markets()
    # ex_api = TdxExHq_API(False, heartbeat=False, auto_retry=True, raise_exception=True, multithread=True)
    # ret = ex_api.connect(ex_hq_hosts[1][1], ex_hq_hosts[1][2])
    # if ret:
    #     pass
    # category = QuotePeriodEnum.MINUTELY1.value
    # code = "09988"
    # start = 0
    # first_temp = ex_api.get_instrument_bars(category, 71, code, start, 3)
    # print(first_temp)
    # data = TdxQuery.get_product_list('50')
    # for item in  data:
        # print(item['Name'])
    # print(data)
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

    