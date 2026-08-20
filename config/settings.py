# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

from config.secure import LOG_FILE_PATH
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class GlobeConfig:
    is_fastapi_server = True
    is_log_file = True
    is_print = False
    logger_name = "xquant"
    log_file_path = LOG_FILE_PATH
    log_file_name = 'xquant.log'



if __name__ == "__main__":
    print(root_dir)