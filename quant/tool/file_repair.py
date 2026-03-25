# -*- coding:utf-8 -*-
"""
date: 2025/11/20
author: Berserker
"""
import os
from quant.libs.log import XLog
import json

def quote_json_file_repair(dir_path:str='/home/xquant/cache/Todo_Fix'):
    #
    file_name_list = os.listdir(dir_path)
    for name in file_name_list:
        if not name.endswith(".json"):
            continue
        XLog.info(name)
        file_name = os.path.join(dir_path, name)
        with open(file_name,"r", encoding="utf-8") as file:
            #TODO -1 or 0
            size =  file.seek(0,os.SEEK_END)
            file.seek(size-1,os.SEEK_SET)
            last_char = file.read(1)
            if last_char == "]":
                continue

        with open(file_name, "a", encoding="utf-8")  as file:
            file.write("]")
            XLog.info("fix: " + name + " ( add \"]\" )")


def quote_json_file_repair_change(dir_path:str='/home/xquant/cache/Todo_Fix'):
    file_name_list = os.listdir(dir_path)
    for name in file_name_list:
        if not name.endswith(".json"):
            continue
        XLog.info(name)
        file_name = os.path.join(dir_path, name)
        with open(file_name,"r", encoding="utf-8") as file:
            json_data_list = json.load(file)
            for data in json_data_list:
                data['amount'] = '%.2f' % (data['amount'] * 10000)

        file_name_1 = os.path.join('/home/xquant/cache/', name)
        with open(file_name_1, 'w', encoding="utf-8") as  file:
            json.dump(json_data_list, file)

if __name__ == "__main__":
    quote_json_file_repair_change()