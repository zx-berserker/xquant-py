# -*- encoding:utf-8 -*-
"""
date: 2020/11/3
author: Berserker
"""


class Dict(object):

    def __init__(self, data):
        if isinstance(data, dict):
            self.data_dict = data
        else:
            self.data_obj = data

    def __getattr__(self, item):
        if self.data_dict:
            if item in self.data_dict.keys():
                return self.data_dict[item]
        else:
            return self.data_obj.__getattribute__(item)
        return None
