# -*- encoding:utf-8 -*-
"""
date: 2020/9/12
author: Berserker
"""
import numpy as np
import pandas as pd

def test():
    data_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print(data_list[-3:])
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


def test_str():
    str_list = ["aa", "ss", "cc"]
    temp = None
    print(str_list[0:temp])
    if "aa" in str_list:
        print("OK")
        
    li = []
    temp = []
    for i in str_list:
        temp.append(i)
        print(temp)


def test_str_reset():
    s = "<p>　　世界气象组织23日发布了《2024年亚洲气候状况》报告。报告指出，去年是亚洲有记录以来最热或第二热的年份，升温导致更多极端天气事件发生，给亚洲的经济、生态系统和社会造成严重损失。</p><p>　　报告称，2024年，热浪席卷的海洋面积创纪录，海洋表面温度达到有记录以来最高水平，其中，<strong>亚洲海面十年升温率几乎是全球平均值的两倍</strong>。靠近亚洲大陆一侧的<span id=\"stock_1.601099\"><a href=\"http://quote.eastmoney.com/unify/r/1.601099\" class=\"keytip\" data-code=\"1,601099\">太平洋</a></span><span id=\"quote_1.601099\"></span>和印度洋的海平面上升水平超过全球平均水平。</p><p>　　此外，冬季降雪减少和夏季极端高温对冰川造成重创。冰湖溃决洪水、山体滑坡等灾害风险上升。极端降雨、热带气旋、干旱等极端天气事件在亚洲许多国家造成严重破坏和重大伤亡。</p><p>　　报告还以去年9月尼泊尔破纪录的降雨引发严重洪水为例，强调加强预警系统和预见性行动防备以应对气候变化、保护生命和生计的重要性。</p><p class=\"em_media\">（文章来源：央视新闻）</p>"
    temp = s.replace("<","@@<").replace(">",">@@").split("@@")
    
    string = ""
    for slice in temp:
        if "<" in slice and ">" in slice:
            continue
        string += slice
    print(string)



def test_list():
    li = """
    | 行业 | 标题 | 日期 | 股票 | 机构名称 | 评级 |
    |------|------|------|----------|------|------|
    """
    li += "adfadsfadsfadsffdas"
    print(li)
    # for i in range(-1,0-len(li),-1):
    #     print(i)


if __name__ == '__main__':
    print(np.__version__)
    
    test()
    test = {}
    # test["test"] = 1
    # if "test" in test:
    #     print("ok")
    # if type(test).__name__ == "dict":
    #     print("is")
    # if isinstance(test,dict):
    #     print("is")
    if "a" not in test:
        print("Not")

for i in range(1,10):
    if i == 5:
        print("continue")
        continue
    print(i)