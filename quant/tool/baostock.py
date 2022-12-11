# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

import baostock as bs
import threading


def baostock_login(fn):
    def login(*args, **kwargs):
        lg = bs.login()
        if lg.error_code != '0':
            print('error_code:' + lg.error_code)
            print('error_msg:' + lg.error_msg)
            raise
        ret = fn(*args, **kwargs)
        bs.logout()
        return ret
    return login


class BaoStock(object):
    login_mutex = threading.Lock()
    is_login = False
    is_decorator = True

    @classmethod
    def connector(cls, fn):
        def decorator(*args, **kwargs):
            with cls.login_mutex:
                if not cls.is_login and cls.is_decorator:
                    lg = bs.login()
                    if lg.error_code != '0':
                        print('error_code:' + lg.error_code)
                        print('error_msg:' + lg.error_msg)
                        raise
                    cls.is_login = True
                ret = fn(*args, **kwargs)
                if cls.is_login and cls.is_decorator:
                    bs.logout()
                    cls.is_login = False
            return ret
        return decorator

    @classmethod
    def login(cls):
        with cls.login_mutex:
            if not cls.is_login:
                lg = bs.login()
                if lg.error_code != '0':
                    print('error_code:' + lg.error_code)
                    print('error_msg:' + lg.error_msg)
                    raise
                cls.is_login = True
                cls.is_decorator = False

    @classmethod
    def logout(cls):
        with cls.login_mutex:
            if cls.is_login:
                bs.logout()
                cls.is_login = False
                cls.is_decorator = True
