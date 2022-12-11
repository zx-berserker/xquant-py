# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from quant.libs.multi_thread.xtask import XTask, XTaskFactory
from quant.spider.baostock.query_stock_info import QueryStockInfo
from quant.tool.function_tool import check_df_value
from quant.spider.east_money.shareholder_info import ShareholderInfo


class KDataSpiderTask(XTask):

    def __init__(self, stock, freq_type=QueryStockInfo.FreqTypeEnum.FREQ_DAILY, start_date='2006-01-01'):
        super(KDataSpiderTask, self).__init__()
        self.stock = stock
        self.freq_type = freq_type
        self.start_date = start_date
        if self.stock is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "stock is None!!!")
        self.ret_data = None

    def get_stock(self):
        return self.stock

    def task_main(self):
        k_data_df = QueryStockInfo.query_k_data(self.stock.code, start_date=self.start_date, freq_type=self.freq_type)
        data_list = []
        for index in k_data_df.index:
            data_dict = {
                'stock_id': self.stock.id,
                'open': float(k_data_df.loc[index].values[2]),
                'high': float(k_data_df.loc[index].values[3]),
                'low': float(k_data_df.loc[index].values[4]),
                'close': float(check_df_value(k_data_df.loc[index].values[5], 0.0)),
                'volume': int(check_df_value(k_data_df.loc[index].values[6], 0)),
                'amount': float(check_df_value(k_data_df.loc[index].values[7], 0.0)),
            }
            date_time = k_data_df.loc[index].values[0]
            if self.freq_type == QueryStockInfo.FreqTypeEnum.FREQ_HOURLY:
                time_str = date_time[0:4] + '-' + date_time[4:6] + '-' + date_time[6:8] + ' ' + date_time[8:10] + ':' +\
                           date_time[10:12] + ':' + date_time[12:14] + '.' + date_time[14:17]
                data_dict['time'] = time_str
            else:
                data_dict['date'] = date_time
                data_dict['turn'] = float(check_df_value(k_data_df.loc[index].values[8], 0.0))
                data_dict['pct_chg'] = float(check_df_value(k_data_df.loc[index].values[9], 0.0))

            if self.freq_type == QueryStockInfo.FreqTypeEnum.FREQ_DAILY:
                data_dict['pre_close'] = float(check_df_value(k_data_df.loc[index].values[10], 0.0))
                data_dict['pe_ttm'] = float(check_df_value(k_data_df.loc[index].values[11], 0.0))
                data_dict['pb_mrq'] = float(check_df_value(k_data_df.loc[index].values[12], 0.0))
                data_dict['ps_ttm'] = float(check_df_value(k_data_df.loc[index].values[13], 0.0))
                data_dict['pcf_ncf_ttm'] = float(check_df_value(k_data_df.loc[index].values[14], 0.0))
            data_list.append(data_dict)
            self.ret_data = data_list
        return data_list

    def __repr__(self):
        return "<KDataSpiderTask id:%d stock:%s>" % (id(self), self.stock)


class ShareholderSpiderTask(XTask):

    def __init__(self, page_index, query_type):
        super(ShareholderSpiderTask, self).__init__()
        self._query_type = query_type
        self._page_index = page_index
        if query_type is None or page_index is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "parameter is None!!!")

    def task_main(self):
        json_ary = ShareholderInfo.query(self._query_type, self._page_index)
        if not json_ary:
            return None
        data_list = []
        for item in json_ary:
            data_dict = ShareholderInfo.json_list_to_model_dict(item, self._query_type)
            if data_dict:
                data_list.append(data_dict)
        return data_list

    def __repr__(self):
        return "<ShareholderSpiderTask id:%d page_index:%s>" % (id(self), self._page_index)


class StockInfoSpiderTask(XTask):
    
    def __init__(self, stock, year=None, quarter=None):
        super(StockInfoSpiderTask, self).__init__()
        self.stock = stock
        self.year = year
        self.quarter = quarter
        if self.stock is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID, "stock is None!!!")

    def get_stock(self):
        return self.stock
    
    def task_main(self):
        
        stock_info = QueryStockInfo.query_stock_profit_data(self.stock.code, year=self.year, quarter=self.quarter)
        data_list = []
        for index in stock_info.index:
            data_dict = {
                'stock_id': self.stock.id,
                'date': stock_info.loc[index].values[2],
                'roe_avg': float(check_df_value(stock_info.loc[index].values[3], 0.0)),
                'np_margin': float(check_df_value(stock_info.loc[index].values[4], 0.0)),
                'gp_margin': float(check_df_value(stock_info.loc[index].values[5], 0.0)),
                'net_profit': float(check_df_value(stock_info.loc[index].values[6], 0.0)),
                'eps_ttm': float(check_df_value(stock_info.loc[index].values[7], 0.0)),
                'mbr_revenue': float(check_df_value(stock_info.loc[index].values[8], 0.0)),
                'total_share': int(float(check_df_value(stock_info.loc[index].values[9], 0))),
                'liqa_share': int(float(check_df_value(stock_info.loc[index].values[10], 0))),
            }
            data_list.append(data_dict)
        print(data_list)
        return data_list

    def __repr__(self):
        return "<StockInfoSpiderTask id:%d stock:%s>" % (id(self), self.stock)
