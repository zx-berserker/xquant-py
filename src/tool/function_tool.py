# -*- encoding:utf-8 -*-
"""
date: 2020/8/30
author: Berserker
"""
from src.libs.error import XException
from src.libs.enums import ErrorCodeEnum


def check_df_value(value, default):
    return default if (value == '' or value is None) else value


def get_fn_arg_count(fn):
    return fn.__code__.co_argcount


def get_fn_arg_names(fn):
    return fn.__code__.co_varnames


def check_dic_key_legal(dic_obj, key):
    if key not in dic_obj.keys():
        raise XException(ErrorCodeEnum.CODE_INVALID, "The value:" + key + " is not dict key !")


