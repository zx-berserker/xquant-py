# -*- encoding:utf-8 -*-
"""
date: 2022/11/24 
author: Berserker
"""
from src.models import Shareholder, FloatShareholder, Stock, KDataDaily, KDataWeekly, KDataMonthly, KDataHourly, StockInfo
from src.tool.figure_bokeh import FigureBokeh
from src.tool.database.base import SQLAlchemy
from src.tool.database.database_tools import DatabaseTools
from src.strategy.technical_analysis_indicator.price_indicator import PriceIndicator, IndicatorData
import numpy as np
import pandas as pd


def test_main():
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == 'sz.002349').first()
        print(stock)
        k_data_list = stock.k_data_daily        
    k_data_df = DatabaseTools.CollectionsToDataFrame(k_data_list, ['date', 'close', 'open', 'high', 'low'])
    ind_data = IndicatorData(k_data_list)
    dma_dic = dict(dma_turn_100=PriceIndicator.dma_coe_by_turn(ind_data),
                   dma_up_62=PriceIndicator.dma_coe_by_turn(ind_data, 87),
                   dma_up_38=PriceIndicator.dma_coe_by_turn(ind_data, 59),
                   dma_up_10=PriceIndicator.dma_coe_by_turn(ind_data, 17))
    line_data_df = pd.DataFrame(dma_dic)
    figure_bokeh = FigureBokeh()
    with figure_bokeh.candlestick_show(k_data_df, 'sz002349', 'date') as fb:
        for key in dma_dic.keys():
            fb.add_a_line(line_data_df, key, legend_label=key)

    
    
if __name__ == '__main__':
    test_main()