# -*- encoding:utf-8 -*-
"""
date: 2023/3/10
author: Berserker
"""
import pandas as pd

def read_from_csv(file_full_name):
    data_df = pd.read_csv(file_full_name)
    return data_df



def static_captial(data_df):
    data_dic = {}
    for id, data in data_df.iterrows():
        captial_str = data['capital']
        name = data['name']
        tem_str = captial_str.split("/", 1)
        capital = float(tem_str[0])*float(tem_str[1])
        if name in data_dic.keys():
            data_dic[name] += capital
        else:
            data_dic[name] = capital
            
    return data_dic
            


def main_capital_static(name, ret_dict=None, get_ret=True):
    data_b = read_from_csv('./test/cache/capital'+name+'-buy.csv')
    ret_b = static_captial(data_b)
    data_s = read_from_csv('./test/cache/capital'+name+'-sell.csv')
    ret_s = static_captial(data_s)
    for key in ret_b.keys():
        if not get_ret:
            if key in ret_dict:
                ret_dict[key] += ret_b[key]
            else:
                ret_dict[key] = ret_b[key]
        if key in ret_s.keys():
            ret_b[key] -= ret_s[key]
            if not get_ret:     
                ret_dict[key] -= ret_s[key]
            

    if get_ret:
        name_list = []
        capital_list = []
        for key in ret_b:
            name_list.append(key)
            capital_list.append(ret_b[key])
        pd_dict = {
            'name':name_list,
            'capital':capital_list
        }   
        ret_df = pd.DataFrame(pd_dict)
        ret_df.to_csv('./test/cache/ret-'+name+'.csv')
    
    
    
def main_static_ret():
    data_df_1 = read_from_csv('./test/cache/ret-3-9.csv')
    data_df_2 = read_from_csv('./test/cache/ret-3-10.csv')
    name_list_1 = data_df_1['name'].tolist()
    name_list_2 = data_df_2['name'].tolist()
    ret_list = []
    for name in name_list_1:
        if name in name_list_2:
            ret_list.append(name)
            
    for ret in ret_list:
        print(ret)

def static_all_name_list(file_name_list):
    ret_dict = {}
    for name in file_name_list:
        main_capital_static(name,ret_dict,False )
        
    name_list = []
    capital_list = []
    for key in ret_dict:
        name_list.append(key)
        capital_list.append(ret_dict[key])
    
    pd_dict = {
        'name':name_list,
        'capital':capital_list
    }   
    ret_df = pd.DataFrame(pd_dict)
    ret_df.to_csv('./test/cache/ret-'+file_name_list[0]+'=='+file_name_list[-1]+'.csv')
   
    
if __name__ == "__main__":
    # main_capital_static('3-9')
    name_list = ['3-9','3-10','3-13','3-14']
    static_all_name_list(name_list)