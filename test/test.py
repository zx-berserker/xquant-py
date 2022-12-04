# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""
import numpy as np


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


def test2():
    test_str = '0123456789'
    print(test_str[0:3])


if __name__ == '__main__':
    test()
