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
import numpy as np
import pandas as pd
from sqlalchemy import func
from operator import and_
from quant.models.many_to_many_table import stock_block_table

def candlestick_with_turn_dma(code='sh.600797', file_path = "./test/cache/"):
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == code).first()
        print(stock)
        k_data_list = stock.k_data_daily[-500:]
    stock_name = stock.name        
    k_data_df = DatabaseTools.CollectionsToDataFrame(k_data_list, ['date', 'close', 'open', 'high', 'low'])
    print(k_data_df)
    ind_data = IndicatorData(k_data_list)
    dma_dic = dict(dma_turn_100=PriceIndicator.dma_coe_by_turn(ind_data),
                   dma_up_62=PriceIndicator.dma_coe_by_turn(ind_data, 87),
                   dma_up_38=PriceIndicator.dma_coe_by_turn(ind_data, 59),
                   dma_up_10=PriceIndicator.dma_coe_by_turn(ind_data, 17))
    line_data_df = pd.DataFrame(dma_dic)
    print(line_data_df)
    figure_bokeh = FigureBokeh(file_path)
    with figure_bokeh.candlestick_show(k_data_df, stock_name, 'date') as fb:
        for key in dma_dic.keys():
            fb.candlestick_add_a_line(line_data_df, key, legend_label=key)



def block_k_data_daily_bokeh(block_name_list = None, tile_name="block", file_path = "./test/cache/"):
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
            k_data_list = session.query(
                KDataDaily.date,
                func.avg(KDataDaily.close)
            ).filter(and_(
                block.id == stock_block_table.c.block_id,
                KDataDaily.stock_id == stock_block_table.c.stock_id
            )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
            k_data_df = pd.DataFrame(k_data_list[-500:],columns=['date','close'])
            # k_data_df = k_data_df.set_index(k_data_df['date'])
            if k_data_df.empty:
                continue
            k_data_df.loc[:, 'name'] = block.name
            print(k_data_df)
            block_k_data_dic[block.name] = k_data_df
            temp_df = k_data_df
    if temp_df is None:
        print('temp_df is None!!!')
        return
    figure_bokeh = FigureBokeh(file_path)
    with figure_bokeh.line_show(temp_df=temp_df, index_type='date', title=tile_name) as fb:
        for key in block_k_data_dic:
            print(key)
            fb.add_a_line(block_k_data_dic[key],  'close')




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
        

def industry_k_data_daily_bokeh(industry_name_list = None, tile_name="industry", file_path = "./test/cache/"):
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
    with figure_bokeh.line_show(temp_df=temp_df, index_type='date', title=tile_name) as fb:
        for key in Industry_k_data_dic:
            print(key)
            fb.add_a_line(Industry_k_data_dic[key],  'close') 
        
        
if __name__ == '__main__':
    
    # name_list = ['机器人', '减速器', '机器视觉', '人工智能']
    # block_k_data_daily_bokeh(name_list)
    # stocks_in_block_bokeh('减速器')
    # candlestick_with_turn_dma('sh.603533')
    # code_list = ['sz.300059', 'sh.600320', 'sh.600010', 'sz.300355', 'sh.688303', 'sh.600797',
    #              'sz.002415', 'sz.300021', 'sh.600477']
    # for code in code_list:
    #     candlestick_with_turn_dma(code)
    # industry_k_data_daily_bokeh()
    
    file_path = "C:/server/nginx/html/"
    industry_list = ['通信设备','电力','汽车零部件', '汽车整车', '证券']
    industry_k_data_daily_bokeh(industry_list, 'hot-industry', file_path)
    for industry in industry_list:
            stocks_in_industry_bokeh(industry, file_path)
   
    # block_list = ['航天装备', 'PET铜箔', '光伏概念']
    # block_k_data_daily_bokeh(block_list, 'hot-block', file_path)
    # for block in block_list:
    #     stocks_in_block_bokeh(block,file_path)