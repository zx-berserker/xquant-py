# -*- encoding:utf-8 -*-
"""
date: 2022/11/24 
author: Berserker
"""
from quant.models import Shareholder, FloatShareholder, Stock, KDataDaily, KDataWeekly, KDataMonthly, KDataHourly, StockInfo, Block, Industry
from quant.tool.figure_bokeh import FigureBokeh
from quant.tool.database.base import SQLAlchemy
from quant.tool.database.database_tools import DatabaseTools
from quant.strategy.technical_analysis_indicator.price_indicator import PriceIndicator, IndicatorData
from sqlalchemy import Date
import numpy as np
import pandas as pd
from sqlalchemy import func
from operator import and_
from quant.models.many_to_many_table import stock_block_table

def candlestick_with_turn_dma(code='sh.600797', turn_cycles=100, file_path = "./test/cache/html/"):
    # 周期数因子
    coe = turn_cycles / 100 
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == code).first()
        print(stock)
        k_data_list = stock.k_data_daily[-1000:]
    stock_name = stock.name        
    k_data_df = DatabaseTools.CollectionsToDataFrame(k_data_list, ['date', 'close', 'open', 'high', 'low'])
    print(k_data_df)
    ind_data = IndicatorData(k_data_list)
    dma_dic = dict(dma_turn_100=PriceIndicator.dma_coe_by_turn(ind_data, 100/coe),
                   dma_turn_61=PriceIndicator.dma_coe_by_turn(ind_data, 61/coe),
                   dma_up_37=PriceIndicator.dma_coe_by_turn(ind_data, 37/coe),
                   dma_up_13=PriceIndicator.dma_coe_by_turn(ind_data, 22/coe),
                   dma_up_8=PriceIndicator.dma_coe_by_turn(ind_data, 13/coe))
    line_data_df = pd.DataFrame(dma_dic)
    print(line_data_df)
    figure_bokeh = FigureBokeh(file_path)
    with figure_bokeh.candlestick_show(k_data_df, stock_name, 'date') as fb:
        for key in dma_dic.keys():
            fb.candlestick_add_a_line(line_data_df, key, legend_label=key)



def block_k_data_daily_bokeh(block_name_list = None, start_date="2025-01-01", end_date="2025-01-02", title_name="block", file_path = "./test/cache/html/"):
    block_k_data_dic = {}
    temp_df = None
    block_list = []
    with SQLAlchemy.session_context() as session:
        if block_name_list is None:
            block_list = session.query(Block).all()
        else:
            for name in block_name_list:
                block = session.query(Block).filter(Block.name == name).first()
                if not block is None:
                    block_list.append(block)
        for block in block_list:
            stock_id_q_list = session.query(
                stock_block_table.c.stock_id
            ).filter(
                block.id == stock_block_table.c.block_id
            ).all()
            stock_id_list = [a[0] for a in stock_id_q_list]
            k_data_list = session.query(
                KDataDaily.date,
                func.avg(KDataDaily.close)
            ).filter(
                KDataDaily.stock_id.in_(stock_id_list) &
                KDataDaily.date.between(start_date,end_date)
            ).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
            k_data_df = pd.DataFrame(k_data_list,columns=['date','close'])
            # k_data_df = k_data_df.set_index(k_data_df['date'])
            if k_data_df.empty:
                continue
            k_data_df.loc[:, 'name'] = block.name
            close = k_data_df["close"][0]
            k_data_df["chg"] = k_data_df.apply(
                lambda x: (x["close"]-close)/close*100,
                axis=1)
            # print(k_data_df)
            block_k_data_dic[block.name] = k_data_df
            temp_df = k_data_df
    if temp_df is None:
        print('temp_df is None!!!')
        return
    print("block_k_data_dic:%d" % (len(block_k_data_dic)))
    figure_bokeh = FigureBokeh(file_path)
    with figure_bokeh.line_show(temp_df=temp_df, index_type='date', title=title_name) as fb:
        for key in block_k_data_dic:
            print(key)
            fb.add_a_line(block_k_data_dic[key], 'chg', legend_label=key)




def stocks_in_block_bokeh(block_name, file_path="./test/cache/"):
    stock_k_data_dic = {}
    temp_df = None
    with SQLAlchemy.session_context() as session:
        block = session.query(Block).filter(Block.name == block_name).first()
        if block is None:
            print("block is None!!!")
            return
        stock_list = block.stocks
        if stock_list is None:
            print('stock list is None!!!')
            return
        for stock in stock_list:
            k_data_list = stock.k_data_daily[-500:]
            k_data_df = DatabaseTools.CollectionsToDataFrame(k_data_list, ['date', 'close'])
            k_data_df.loc[:,'name'] = stock.name
            stock_k_data_dic[stock.name] = k_data_df
            if len(k_data_list) == 500:
                temp_df = k_data_df
    if temp_df is None:
        print('temp_df is None!!!')
        return
    figuer_bokeh = FigureBokeh(file_path)
    with figuer_bokeh.line_show(temp_df=temp_df, index_type='date', title=block_name) as fb:
        for key in stock_k_data_dic:
            fb.add_a_line(stock_k_data_dic[key], 'close')
            
            
            
def stocks_in_industry_bokeh(industry_name, file_path='./test/cache'):
    stock_k_data_dic = {}
    temp_df = None
    with SQLAlchemy.session_context() as session:
        industry = session.query(Industry).filter(Industry.name == industry_name).first()
        if industry is None:
            print("industry is None!!!")
            return
        stock_list = industry.stocks
        if stock_list is None:
            print("stock list is None!!!")
            return
        for stock in stock_list:
            k_data_list = stock.k_data_daily[-500:]
            k_data_df = DatabaseTools.CollectionsToDataFrame(k_data_list, ['date', 'close'])
            k_data_df.loc[:, 'name'] = stock.name
            stock_k_data_dic[stock.name] = k_data_df
            if len(k_data_list) == 500:
                temp_df = k_data_df
    if temp_df is None:
        print('temp_df is None!!!')
        return
    figuer_bokeh = FigureBokeh(file_path)
    with figuer_bokeh.line_show(temp_df=temp_df, index_type='date', title=industry_name) as fb:
        for key in stock_k_data_dic:
            fb.add_a_line(stock_k_data_dic[key], 'close')         
        

def industry_k_data_daily_bokeh(industry_name_list = None, title_name="industry", file_path = "./test/cache/html/"):
    Industry_k_data_dic = {}
    temp_df = None
    Industry_list = []
    with SQLAlchemy.session_context() as session:
        if industry_name_list is None:
            Industry_list = session.query(Industry).all()
        else:
            for name in industry_name_list:
                industry = session.query(Industry).filter(Industry.name == name).first()
                if not industry is None:
                    Industry_list.append(industry)
        for industry in Industry_list:
            k_data_list = session.query(
                KDataDaily.date,
                func.avg(KDataDaily.close)
            ).filter(and_(
                industry.id == Stock.industry_id,
                Stock.id == KDataDaily.stock_id
            )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
            k_data_df = pd.DataFrame(k_data_list[-500:],columns=['date','close'])
            if k_data_df.empty:
                continue
            k_data_df.loc[:, 'name'] = industry.name
            print(k_data_df)
            Industry_k_data_dic[industry.name] = k_data_df
            temp_df = k_data_df
    if temp_df is None:
        print('temp_df is None!!!')
        return           
    figure_bokeh = FigureBokeh(file_path)
    with figure_bokeh.line_show(temp_df=temp_df, index_type='date', title=title_name) as fb:
        for key in Industry_k_data_dic:
            print(key)
            fb.add_a_line(Industry_k_data_dic[key],  'close') 
        
        
if __name__ == '__main__':
    
    name_list = ['其他自动化设备', '涤纶','畜禽养殖','养鸡','猪肉','染料','涂料油墨','有线电视网络','互联网彩票','磁性材料',
                 '种子生产','WIFI 6','培育钻石','磨具磨料','超导概念','环保设备','其他社会服务III','互联网电商III','房地产服务III',
                 '集成电路制造','华为欧拉','集成电路封测','集成电路制造','航海装备','半导体设备','基础建设','改性塑料','其他纤维',
                 '线缆部件及其他','餐饮','碳交易','粮食种植','粮油加工','油品石化贸易','芬太尼','重组蛋白','旅游零售','电子化学品III','医疗美容','高压氧舱',
                 '广告营销','动物疫苗','其他纤维','旅游零售','疫苗','餐饮','地面兵装','其他纺织','个护用品','养老概念','医疗美容','乘用车','粮油加工','能源金属',
                 '钴','金属镍','炭黑']
    block_list = []
    for name in name_list:
        if name not in block_list:
            block_list.append(name)

    print(len(block_list))
    # block_k_data_daily_bokeh(name_list)
    # stocks_in_block_bokeh('减速器')
    # candlestick_with_turn_dma('sh.603533')
    # code_list = ['sz.300059', 'sh.600320', 'sh.600010', 'sz.300355', 'sh.688303', 'sh.600797',
    #              'sz.002415', 'sz.300021', 'sh.600477']
    # for code in code_list:
    #     candlestick_with_turn_dma(code)
    # industry_k_data_daily_bokeh()
    
    # file_path = "C:/server/nginx/html/"

    # candlestick_with_turn_dma('sz.300021', 65)
    start_date = "2019-01-08"
    end_date = "2019-04-08"
    title = "block_" + start_date + "~" + end_date
    block_k_data_daily_bokeh(None,start_date,end_date,title_name=title)
    
    # industry_list = ['通信设备','电力','汽车零部件', '汽车整车', '证券']
    # industry_k_data_daily_bokeh(industry_list, 'hot-industry', file_path)
    # for industry in industry_list:
    #         stocks_in_industry_bokeh(industry, file_path)
   
    # block_list = ['航天装备', 'PET铜箔', '光伏概念']
    # block_k_data_daily_bokeh(block_list, 'hot-block', file_path)
    # for block in block_list:
    #     stocks_in_block_bokeh(block,file_path)