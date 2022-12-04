# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

# SQLALCHEMY_DATABASE_URI = 'mysql+cymysql://root:zx123456@127.0.0.1/xquant'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:zx123456@127.0.0.1:3306/xquant'

SECRET_KEY = '\x88D\xf09\x91\x01\x98\x89\x87\x93\xa0A\xc68\xf9\xecJ:U\x17\xc5V\xbe\x8b\xef\xd7\xd8\xd3\xe6\x98*4'

# 开启数据库查询性能测试
SQLALCHEMY_RECORD_QUERIES = True

# 性能测试的阀值
DATABASE_QUERY_TIMEOUT = 0.5

SQLALCHEMY_TRACK_MODIFICATIONS = True

WTF_CSRF_CHECK_DEFAULT = False

SQLALCHEMY_ECHO = False

