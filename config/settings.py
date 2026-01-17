# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class GlobeConfig:
    is_fastapi_server = False
    is_log_file = False



if __name__ == "__main__":
    print(root_dir)