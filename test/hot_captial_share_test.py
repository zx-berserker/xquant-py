# -*- encoding:utf-8 -*-
"""
date: 2023/3/10
author: Berserker
"""
import pandas as pd

def read_from_csv(file_dir, file_name):
    file_full_name = file_dir + file_name
    data_df = pd.read_csv(file_full_name)
    return data_df



def static_capital(data_df):
    data_dic = {}
    for id, data in data_df.iterrows():
        capital_str = data['capital']
        name = data['name']
        tem_str = capital_str.split("/", 1)
        capital = float(tem_str[0])*float(tem_str[1])
        if name in data_dic.keys():
            data_dic[name] += capital
        else:
            data_dic[name] = capital
            
    return data_dic
            
def capital_static_to_csv(year, date):
    capital_buy_df = read_from_csv('./test/cache/'+year+'/capital/', date+'-buy.csv')
    capital_sell_df = read_from_csv('./test/cache/'+year+'/capital/', date+'-sell.csv')
    buy_dic = static_capital(capital_buy_df)
    sell_dic = static_capital(capital_sell_df)
    static_dic = {}
    for key in buy_dic:
        static_dic[key] = buy_dic[key]            
        if key in sell_dic.keys():
            static_dic[key] -= sell_dic[key]
    name_list = []
    capital_list = []
    buy_list = []
    sell_list = []
    for key in static_dic:
        name_list.append(key)
        capital_list.append(static_dic[key])
        buy_list.append(buy_dic[key])
        if key in sell_dic:
            sell_list.append(sell_dic[key])
        else:
            sell_list.append(0.0)
    pd_dic  = {
        'name':name_list,
        'buy':buy_list,
        'sell':sell_list,
        'capital':capital_list
    }
    ret_df = pd.DataFrame(pd_dic)
    ret_df.to_csv('./test/cache/'+year+'/'+date+'.csv')



def csv_static(year, date_list):
    buy_dic = {}
    sell_dic = {}
    capital_dic = {}
    times_dic = {}
    for date in  date_list:
        capital_df = read_from_csv('./test/cache/'+year+'/', date+'.csv')
        for id, date in capital_df.iterrows():
            name = date['name']
            if name not in buy_dic:
                buy_dic[name] = date['buy']
                sell_dic[name] = date['sell']
                capital_dic[name] = date['capital']
                times_dic[name] = 1
            else:
                buy_dic[name] += date['buy']
                sell_dic[name] += date['sell']
                capital_dic[name] += date['capital']
                times_dic[name] += 1
    name_list = []
    buy_list = []
    sell_list = []
    capital_list = []
    times_list = []
    sell_buy_list = []
    for key in buy_dic:
        name_list.append(key)
        buy_list.append(buy_dic[key])
        sell_list.append(sell_dic[key])
        capital_list.append(capital_dic[key])
        times_list.append(times_dic[key])
        sell_buy_list.append(sell_dic[key]/buy_dic[key])
    
    pd_dic = {
        'name': name_list,
        'buy': buy_list,
        'sell': sell_list,
        'capital': capital_list,
        'times': times_list,
        's/b':sell_buy_list
    }   
    ret_df = pd.DataFrame(pd_dic)
    ret_df.to_csv('./test/cache/ret_'+date_list[0]+'=='+date_list[-1]+'.csv')

    
def main_capital_static_csv():
    date_list = ['4-24','4-25','4-26','4-29','4-30','5-6']
    for date in date_list:
        capital_static_to_csv('2024',date)



def main_csv_static():
    date_list = ['3-29','4-2','4-3','4-8','4-9','4-10','4-11','4-12','4-15','4-16','4-17','4-18','4-19','4-22','4-23','4-24','4-25','4-26','4-29','4-30','5-6']
    csv_static('2024', date_list[0:-4])
    
    
      
    
if __name__ == "__main__":
    # main_capital_static_csv()
    main_csv_static()