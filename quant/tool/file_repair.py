# -*- coding:utf-8 -*-
"""
date: 2025/11/20
author: Berserker
"""
import os

def quote_json_file_repair(dir_path:str='/home/xquant/cache'):
    #
    file_name_list = os.listdir(dir_path)
    for name in file_name_list:
        print(name)
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
            print("fix: " + name + " ( add \"]\" )")




if __name__ == "__main__":
    quote_json_file_repair()