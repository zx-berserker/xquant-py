# -*- encoding:utf-8 -*-
"""
date: 2022/11/24 
author: Berserker
"""
from quant.models import Shareholder, FloatShareholder, Stock, KDataDaily, KDataWeekly, KDataMonthly, KDataHourly, StockInfo, Block
from quant.tool.figure_bokeh import FigureBokeh
from quant.tool.database.base import SQLAlchemy
from quant.tool.database.database_tools import DatabaseTools
from quant.strategy.technical_analysis_indicator.price_indicator import PriceIndicator, IndicatorData
import numpy as np
import pandas as pd
from sqlalchemy import func
from operator import and_
from quant.models.many_to_many_table import stock_block_table

def candlestick_with_turn_dma(code='sh.600797'):
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == code).first()
        print(stock)
        k_data_list = stock.k_data_daily[-500:-1]
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
    figure_bokeh = FigureBokeh("./test/cache/")
    with figure_bokeh.candlestick_show(k_data_df, stock_name, 'date') as fb:
        for key in dma_dic.keys():
            fb.candlestick_add_a_line(line_data_df, key, legend_label=key)



def block_k_data_daily_bokeh():
    block_k_data_dic = {}
    temp_df = None
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Block).all()
        for block in block_list:
            k_data_list = session.query(
                KDataDaily.date,
                func.avg(KDataDaily.close)
            ).filter(and_(
                block.id == stock_block_table.c.block_id,
                KDataDaily.stock_id == stock_block_table.c.stock_id
            )).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
            k_data_df = pd.DataFrame(k_data_list[-500:-1],columns=['date',block.name])
            # k_data_df = k_data_df.set_index(k_data_df['date'])
            if k_data_df.empty:
                continue
            print(k_data_df)
            block_k_data_dic[block.name] = k_data_df
            if block.id == 3:
                temp_df = k_data_df
            
    figure_bokeh = FigureBokeh("./test/cache/")
    with figure_bokeh.line_show(temp_df=temp_df, index_type='date', title='block') as fb:
        for key in block_k_data_dic:
            print(key)
            fb.add_a_line(block_k_data_dic[key],  key)

  
    
if __name__ == '__main__':
    
    candlestick_with_turn_dma()