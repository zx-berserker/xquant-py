# -*- encoding:utf-8 -*-
"""
date: 2020/8/29
author: Berserker
"""

from urllib3 import PoolManager, exceptions
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
from enum import Enum
import json
import re
from quant.tool.database.base import SQLAlchemy
from quant.models.stock import Stock


class ShareholderInfo(object):
    base_url = "http://data.eastmoney.com/DataCenter_V3/gdfx/data.ashx?"
    sort_rule = 1
    sort_type = "NDATE,SCODE,RANK"
    js_obj = "x_json"
    http = PoolManager()
    page_size = 1000

    class QueryTypeEnum(Enum):
        QUERY_SHARE_HOLDER = "HDDETAIL"
        QUERY_FLOAT_SHARE_HOLDER = "NSHDDETAIL"

    @classmethod
    def get_page_index_max(cls, query_type):
        json_re = re.compile(r'.*?' + cls.js_obj + ' = (.*?);')
        url = cls.base_url + 'SortType=' + cls.sort_type + '&SortRule=' + str(cls.sort_rule) + '&jsObj=' + \
            cls.js_obj + '&PageSize=' + str(cls.page_size) + '&type=' + query_type.value + '&PageIndex=1'
        try:
            response = cls.http.request("POST", url)
        except exceptions.HTTPError as e:
            print(e)
            raise e
        http_data = response.data.decode('gb18030')
        data_list = json_re.findall(http_data)
        if not data_list:
            raise XException(ErrorCodeEnum.CODE_FAILED, "json_data is none !")
        json_str = data_list[0].replace('pages', '"pages"', 1).replace('data', '"data"', 1)
        json_data = json.loads(json_str)
        return int(json_data['pages'])

    def __init__(self, query_type, page_index_max):
        self._json_re = re.compile(r'.*?' + self.js_obj + ' = (.*?);')
        self._page_index = 1
        self._url = self.base_url + 'SortType=' + self.sort_type + '&SortRule=' + str(self.sort_rule) + '&jsObj=' + \
            self.js_obj + '&PageSize=' + str(self.page_size) + '&type=' + query_type.value
        self._page_index_max = page_index_max
        if page_index_max is None:
            self._page_index_max = self.get_page_index_max(query_type)

    def __iter__(self):
        return self

    def __next__(self):
        if self.page_index <= self._page_index_max:
            url = self._url + '&PageIndex=' + str(self.page_index)
            try:
                response = self.http.request("POST", url)
            except exceptions.HTTPError as e:
                print(e)
                raise XException(ErrorCodeEnum.CODE_FAILED, str(e))
            http_data = response.data.decode('gb18030')
            data_list = self._json_re.findall(http_data)
            if not data_list:
                raise XException(ErrorCodeEnum.CODE_FAILED, "json_data is none !")
            json_str = data_list[0].replace('pages', '"pages"', 1).replace('data', '"data"', 1)
            json_data = json.loads(json_str)
            data = json_data['data']
            if not json_data:
                print("page:%d http_data:%s" % (self.page_index, http_data))
                raise XException(ErrorCodeEnum.CODE_FAILED, "json_data is none !")
            self.page_index += 1
            return data
        else:
            self.page_index = 1
            raise StopIteration

    @classmethod
    def query(cls, query_type, page_index):
        json_re = re.compile(r'.*?' + cls.js_obj + ' = (.*?);')
        url = cls.base_url + 'SortType=' + cls.sort_type + '&SortRule=' + str(cls.sort_rule) + '&jsObj=' + cls.js_obj +\
            '&PageSize=' + str(cls.page_size) + '&type=' + query_type.value + '&PageIndex=' + str(page_index)
        try:
            response = cls.http.request("POST", url)
        except exceptions.HTTPError as e:
            print(e)
            raise e
        http_data = response.data.decode('gb18030')
        data_list = json_re.findall(http_data)
        if not data_list:
            raise XException(ErrorCodeEnum.CODE_FAILED, "data_list is none !")
        json_str = data_list[0].replace('pages', '"pages"', 1).replace('data', '"data"', 1)
        json_data = json.loads(json_str)
        if not json_data:
            print("page:%d http_data:%s" % (page_index, http_data))
            raise XException(ErrorCodeEnum.CODE_FAILED, "json_data is none !")
        return json_data['data']

    @staticmethod
    def json_list_to_model_dict(data_json, query_type):
        """
        :param data_json:
            SHAREHDNAME: 股东名称
            SHAREHDTYPE: 股东类型
            SHAREHDNUM: 数量
            SHAREHDRATIO: 持股占比
            RANK: 股东排名
            RDATE: 报告日期
            LTAG: 流通市值
            BZ: 持股变动
            SCODE: 股票代码
        :param query_type: ShareholderInfo.QueryTypeEnum
        :return: dict
        """
        if not data_json:
            return {}

        code = data_json['SCODE']
        if code[0] == '6':
            stock_code = 'sh.' + code
        else:
            stock_code = 'sz.' + code

        with SQLAlchemy.session_context() as session:
            stock = session.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            return None
        model_dict = None
        if query_type == ShareholderInfo.QueryTypeEnum.QUERY_SHARE_HOLDER:
            model_dict = {
                'date': data_json['RDATE'].split('T')[0],
                'name': data_json['SHAREHDNAME'],
                'holder_type': data_json['SHAREHDTYPE'],
                'stock_id': stock.id,
                'hold_number': int(data_json['SHAREHDNUM']),
                'hold_ratio': data_json['SHAREHDRATIO'] * 100,
                'rank': int(data_json['RANK']),
                'amount': data_json['LTAG'],
                'change': data_json['BZ']
            }
        elif query_type == ShareholderInfo.QueryTypeEnum.QUERY_FLOAT_SHARE_HOLDER:
            model_dict = {
                'date': data_json['RDATE'].split('T')[0],
                'name': data_json['SHAREHDNAME'],
                'holder_type': data_json['SHAREHDTYPE'],
                'stock_id': stock.id,
                'hold_number': int(data_json['SHAREHDNUM']),
                'hold_ratio': data_json['SHAREHDRATIO'],
                'rank': int(data_json['RANK']),
                'amount': data_json['LTAG'],
                'change': data_json['BZ']
            }

        return model_dict

