
# -*- encoding:utf-8 -*-
"""
date: 2022/11/23 
author: Berserker
"""
import pandas as pd


class DatabaseTools():
    
    @staticmethod
    def CollectionsToDataFrame(collections, columns):
        data_dic = {}
        for colu in columns:
            if hasattr(collections[0], colu):
                data_dic[colu] = [getattr(colle, colu) for colle in collections]        
        return pd.DataFrame(data_dic)