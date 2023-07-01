# -*- encoding:utf-8 -*-
"""
date: 2022/11/23 
author: Berserker
"""

from bokeh.layouts import gridplot
from bokeh.plotting import figure, output_file, show
from bokeh.io import curdoc
from bokeh.transform import dodge
from bokeh.models.tickers import AdaptiveTicker
from bokeh.core.properties import Datetime
from bokeh.models import ColumnDataSource
from contextlib import contextmanager
from bokeh.models import HoverTool
import pandas as pd
import random


class FigureBokeh(object):
    TOOLS = 'crosshair,pan,wheel_zoom,xwheel_zoom,ywheel_zoom,box_zoom,reset,box_select,lasso_select,save,hover'
    BACKGROUND_COLOR = '#efefef'
    WIDTH = 1900
    HEIGHT = 1000
    LABLE_ORIENTATION = 0.8
    COLOR_LIST = ['deepskyblue', 'lime', 'gold', "pink", 'aqua', 'brown', 'burlywood', 'orangered', 'chartreuse', 'chocolate', 'magenta', 'red',  "lightsalmon", "skyblue", "azure", "tomato",  "yellow", "palegoldenrod", "powderblue", "mediumaquamarine", "turquoise", "lemonchiffon", "whitesmoke", "beige", "linen", "hotpink", 'silver']
    TOOLTIPS = []
    
    def __init__(self, output_path=None):
        self.output_path = output_path
        self.fb = None
        self.df_len = None
        self.df_base_data = None
        self.line_num = 0

    @contextmanager
    def line_show(self, temp_df, index_type, title):
        temp_df[index_type] = pd.to_datetime(temp_df[index_type])
        temp_df.loc[:, 'timestamp'] = temp_df[index_type].apply(lambda t: str(t))
        temp_df = temp_df.set_index(temp_df['timestamp'])
        self.df_len = len(temp_df.index)
        self.df_base_data = temp_df
        hover = HoverTool(tooltips=[("y", "$y"), ('index', "$index"), ("name", "@name")])
        self.fb = figure(x_range=temp_df.index.tolist(), tools=self.TOOLS, width=self.WIDTH, height=self.HEIGHT, 
                         title=title, background_fill_color=self.BACKGROUND_COLOR)
        self.fb.add_tools(hover)
        self.fb.xaxis.major_label_orientation = self.LABLE_ORIENTATION
        yield self
        if self.output_path:
            output_file(self.output_path+title+'.html', title=title)
        show(self.fb)
        
    @contextmanager
    def candlestick_show(self, k_data_df, title, index_type='date'):
        k_data_df[index_type] = pd.to_datetime(k_data_df[index_type])
        k_data_df.loc[:, 'timestamp'] = k_data_df[index_type].apply(lambda t: str(t))
        k_data_df = k_data_df.set_index(k_data_df['timestamp'])
        self.df_len = len(k_data_df.index)
        self.df_base_data = k_data_df
        inc = k_data_df['close'] >= k_data_df['open'] 
        dec = k_data_df['open'] > k_data_df['close']
        # w = 16*60*60*1000
        w = 0.6
        source_dec = dict(index=k_data_df.index[dec], high=k_data_df['high'][dec], low=k_data_df['low'][dec],
                          open=k_data_df['open'][dec], close=k_data_df['close'][dec])
        source_inc = dict(index=k_data_df.index[inc], high=k_data_df['high'][inc], low=k_data_df['low'][inc],
                          open=k_data_df['open'][inc], close=k_data_df['close'][inc])
        hover = HoverTool(tooltips=[("y", "$y"),("date", "@index"), ("high", "@high"), ("low", "@low"), ("open", "@open"), ("close", "@close")])
        self.fb = figure(x_range=k_data_df.index.tolist(), tools=self.TOOLS, width=self.WIDTH,
                         height=self.HEIGHT, tooltips=self.TOOLTIPS, title=title, background_fill_color=self.BACKGROUND_COLOR, width_policy="fixed")
        self.fb.xaxis.major_label_orientation = self.LABLE_ORIENTATION
        self.fb.add_tools(hover)
        self.fb.segment(k_data_df.index, k_data_df['high'], k_data_df.index, k_data_df['low'], color="black")
       
        self.fb.vbar(x='index', width=w, bottom='open', top='close', fill_color="white", line_color="#49a3a3",
                     line_width=2, source=source_dec, name='candlestick')
        self.fb.vbar(x='index', width=w, bottom='open', top='close', color="#eb3c40", source=source_inc,
                     name='candlestick')
        yield self
        
        if self.output_path:
            output_file(self.output_path+title+'.html', title=title)
        show(self.fb)
    
    def candlestick_add_a_line(self, data_df,col_name, **kwargs):
        if self.df_len:
            if self.df_len != len(data_df[col_name]):
                raise        
        if self.fb is None:
            raise
        # num = random.randint(0, len(self.COLOR_LIST))
        num = self.line_num % len(self.COLOR_LIST)
        param_dic = dict(line_width=2, color=self.COLOR_LIST[num], legend_label='%d' % num)
        for key in param_dic.keys():
            if key not in kwargs.keys():
                kwargs[key] = param_dic[key]
        data_df.loc[:, 'timestamp'] = self.df_base_data.index
        data_df = data_df.set_index(data_df['timestamp'])
        self.fb.line(data_df.index, data_df[col_name], **kwargs)
        self.line_num+=1
    
    def add_a_line(self, data_df, col_name, **kwargs):
        if self.df_len:
            print(len(data_df[col_name]))
            if self.df_len != len(data_df[col_name]):
                print("%s is %d not %d" % (col_name, len(data_df[col_name]), self.df_len))
                return        
        if self.fb is None:
            raise
        # num = random.randint(0, len(self.COLOR_LIST)-1)
        num = self.line_num % len(self.COLOR_LIST)
        param_dic = dict(line_width=2, color=self.COLOR_LIST[num], legend_label='%d' % num)
        for key in param_dic.keys():
            if key not in kwargs.keys():
                kwargs[key] = param_dic[key]
        
        data_df.loc[:, 'timestamp'] = self.df_base_data.index
        # data_df = data_df.set_index(data_df['timestamp'])
        
        print(data_df)
        source = ColumnDataSource(data_df)
        self.fb.line(x='timestamp', y=col_name, source=source, **kwargs)
        self.line_num+=1
