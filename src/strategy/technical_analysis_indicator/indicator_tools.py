# -*- encoding:utf-8 -*-
"""
date: 2022/11/22
author: Berserker
"""
import numpy as np
from enum import IntEnum
# from contextlib import contextmanager


class IndicatorToolsProcessType(IntEnum):
    ACCUMALATE = 1
    WINDOW_MOVE_ACCUMALATE = 2
    WINDOW_MOVE_AVG = 3
    

class IndicatorToolsProcess(object):
    
    @staticmethod
    def accumalate(data, begin, end):
        data_sctn = data[begin: end]
        ret = 0
        for id in range(len(data_sctn)):
            ret += data_sctn[id]
            yield [ret, id+begin]
            

class IndicatorTools(object):
    
    _process_dic = {
        IndicatorToolsProcessType.ACCUMALATE: IndicatorToolsProcess.accumalate
    }
    
    @staticmethod
    def section_search(process_type, condition_fn, data, begin=0, end=None):
        for ret in IndicatorTools._process_dic[process_type](data, begin, end):
            if condition_fn(ret[0]):
                return ret[1]

             

                     
            
