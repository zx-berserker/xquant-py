# -*- coding:utf-8 -*-
"""
date: 2026-07-05
author: Berserker
"""

import os
import shutil
from quant.spider.east_money import QuotePeriodEnum
from quant.libs.log import XLog

def move_cache_file_done(dir_path:str='/home/xquant/cache/Done', dst_path='/home/xquant/cache'):
    file_name_list = os.listdir(dir_path)
    data_list_dic:dict[str, list[str]] = {}
    data_list_dic[QuotePeriodEnum.DAILY.name] = []
    data_list_dic[QuotePeriodEnum.HOURLY.name] = []
    data_list_dic[QuotePeriodEnum.MONTHLY.name] = []
    data_list_dic[QuotePeriodEnum.WEEKLY.name] = []
    for name in file_name_list:
        name_list = name.split(".")
        if "json" in name_list:
            pre_name_list = name_list[0].split("-")
            if QuotePeriodEnum.DAILY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.DAILY.name].append(name)
            elif QuotePeriodEnum.HOURLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.HOURLY.name].append(name)
            elif QuotePeriodEnum.MONTHLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.MONTHLY.name].append(name)
            elif QuotePeriodEnum.WEEKLY.name in pre_name_list:
                data_list_dic[QuotePeriodEnum.WEEKLY.name].append(name)
    for key in data_list_dic:
        temp_dst_path = dst_path + '/' + key
        XLog.info(key + " move files to:" + temp_dst_path)
        for file_name in data_list_dic[key]:
            src = dir_path + '/' + file_name
            dst = temp_dst_path+ '/' + file_name
            shutil.move(src, dst)
        XLog.info(key + " finish")


if __name__ == "__main__":
    move_cache_file_done()