# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""
import numpy as np
import pandas as pd

def test():
    data_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    data_ary = np.asanyarray(data_list)
    np_list = []
    for data in data_ary:
        np_list.append(data)
    data_list.extend(np_list)
    ary = np.asanyarray(data_list)
    print(len(ary))
    for it in ary:
        print(it)


def cache_file_find_all_in():
    num1_df = pd.read_csv('./test/cache/3-1.csv')
    num2_df = pd.read_csv('./test/cache/3-2.csv')
    num3_df = pd.read_csv('./test/cache/3-3.csv')
    data = []
    is_in = False
    for id3, data3 in num3_df.iterrows():
        is_in = False
        for id2, data2 in num2_df.iterrows():
            if data3['code'] == data2['code']:
                for id1, data1 in num1_df.iterrows(): 
                    if data3['code'] == data1['code']:
                        is_in = True
                        continue
                if not is_in:
                    data.append(data3)
    return data

def test_cache():
    data_list = cache_file_find_all_in()
    for dat in data_list: 
        print('%s %s %d' % (dat['code'], dat['name'], dat['count']))


        

if __name__ == '__main__':
    test_cache()
