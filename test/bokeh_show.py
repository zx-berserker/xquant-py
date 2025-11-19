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




def block_k_data_daily_bokeh(block_name_list = None, start_date="2025-01-01", end_date="2025-01-02", title_name="block", file_path = "./test/cache/html/",cacl_type=1):
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
            k_data_df = None
            if cacl_type == 1: # AVG
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
                k_data_df.drop(["close"],axis=1,inplace=True)
            elif cacl_type == 2: # amount/volume

                k_data_list = session.query(
                    KDataDaily.date,
                    func.sum(KDataDaily.amount),
                    func.sum(KDataDaily.volume)
                ).filter(
                    KDataDaily.stock_id.in_(stock_id_list) &
                    KDataDaily.date.between(start_date,end_date)
                ).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
                k_data_df = pd.DataFrame(k_data_list,columns=['date','amount','volume'])
                # k_data_df = k_data_df.set_index(k_data_df['date'])
                if k_data_df.empty:
                    continue
                k_data_df.loc[:, 'name'] = block.name
                close = float(k_data_df["amount"][0])/float(k_data_df["volume"][0])
                k_data_df["chg"] = k_data_df.apply(
                    lambda x: (float(x["amount"])/float(x["volume"])-close)/close*100,
                    axis=1)
                k_data_df.drop(["amount","volume"],axis=1,inplace=True)
            else: # chg
                k_data_list = session.query(
                    KDataDaily.date,
                    func.avg(KDataDaily.pct_chg),
                ).filter(
                    KDataDaily.stock_id.in_(stock_id_list) &
                    KDataDaily.date.between(start_date,end_date)
                ).order_by(KDataDaily.date).group_by(KDataDaily.date).all()
            
                k_data_df = pd.DataFrame(k_data_list,columns=['date','pct_chg'])
                # k_data_df = k_data_df.set_index(k_data_df['date'])
                chg_list = [1.0] 
                if k_data_df.empty:
                    continue
                for i in range(1, len(k_data_df['pct_chg'])):
                    chg_list.append(chg_list[i-1]*(1+k_data_df['pct_chg'][i]/100))
                k_data_df['chg'] = chg_list
                k_data_df['chg'] = (k_data_df['chg'] - 1) * 100
                k_data_df.loc[:, 'name'] = block.name
                k_data_df.drop(["pct_chg"],axis=1,inplace=True)

            
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
    
    x_o_name_list = ['其他自动化设备', '涤纶','畜禽养殖','养鸡','猪肉','染料','涂料油墨',
                     '有线电视网络','互联网彩票','磁性材料','种子生产','WIFI 6','培育钻石','磨具磨料','超导概念','环保设备',
                     '其他社会服务III','互联网电商III','房地产服务III','集成电路制造','华为欧拉','集成电路封测',
                     '房地产服务III','集成电路制造','集成电路封测','航海装备','半导体设备',
                     '基础建设','改性塑料','其他纤维','线缆部件及其他','餐饮','碳交易','粮食种植','粮油加工',
                     '油品石化贸易','芬太尼','重组蛋白','旅游零售','电子化学品III','半导体设备','医疗美容','高压氧舱',
                     '广告营销','动物疫苗','其他纤维','旅游零售',
                     '疫苗','动物疫苗','餐饮','地面兵装','其他纺织','个护用品','养老概念','医疗美容',
                     '乘用车','粮油加工','能源金属','钴','金属镍','炭黑']
    
    chg_o_name_list = ["其他电池","风电整机","肉鸡养殖","养鸡",
                       "商用载货车","模拟芯片设计","种子生产","磁性材料","航天装备",
                       "宠物食品","横向通用软件","集成电路制造","互联网电商III","医疗美容","品牌消费电子","集成电路封测",
                       "房地产服务","集成电路制造","半导体设备","集成电路封测","分立器件",
                       "集成电路制造","基础建设","改性塑料","线缆部件及其他","餐饮","粮食种植","粮油加工",
                       "油品石化贸易","芬太尼","集成电路封测","个护用品","旅游零售","逆变器","化妆品","半导体设备","分立器件","半导体材料","国家大基金持股","宠物用品","光伏辅材",
                       "旅游零售","激光设备","其他生物制品","证券III","钴","疫苗",
                       "机器人","餐饮","集成电路制造","疫苗","航空装备","模拟芯片设计","其他养殖","个护用品","逆变器",
                       "医疗美容","白酒III","钴","逆变器",
                       "半导体设备","集成电路制造","医疗耗材","模拟芯片设计","逆变器","数字芯片设计","电池化学品"]

    o_date_dic = dict(p1=("2019-01-08","2019-04-08"),
                 p2=("2019-04-08","2019-08-12"),
                 p3=("2019-08-12","2020-01-16"),
                 p4=("2019-12-02","2020-02-25"),
                 p5=("2020-02-25","2020-03-31"),
                 p6=("2020-03-31","2020-05-27"),
                 p7=("2020-05-27","2020-07-13"),
                 p8=("2020-07-14","2020-09-28"),
                 p9=("2020-09-28","2021-02-10"))
    o1 = ("2020-02-24","2020-05-11")
    
    now_date_dic = dict(
        p1=("2024-09-18","2024-10-17"),
        p2=("2024-10-17","2024-12-12"),
        p3=("2024-12-12","2025-01-13"),
        p4=("2025-01-13","2025-13-18"),
        p5=("2025-03-18","2025-04-08"),
        p6=("2025-04-08","2025-05-14"),
        p7=("2025-05-14","2025-06-20"),
        p8=("2025-06-20","2025-08-01"),
        p9=("2025-08-01","2025-08-25"),
        p10=("2025-08-25","2025-09-19")
    )
    
    now_name_p10_list = ["钾肥","医疗研发外包","普钢","稀土","网络游戏","磨具磨料","彩电","冶钢原料","金属回收","住宅开发","小金属概念","金属铜","铜","金属钴","金属镍","影视院线III","黄金概念","钼","金属铅","铅锌","贵金属III"]



    date_dic = now_date_dic
    name_list = now_name_p10_list
    title_flex = "now_p10_Chg_block_"
    
    block_list = []
    for name in name_list:
        if name not in block_list:
            block_list.append(name)
    print(len(block_list))

    ## P
    # for key in date_dic:
    #     start_date = date_dic[key][0]
    #     end_date = date_dic[key][1]
    #     title = title_flex + start_date + "~" + end_date
    #     block_k_data_daily_bokeh(None,start_date,end_date,title_name=title,cacl_type=3)


    ## NUM
    # for i in range(0, len(date_dic)-1):
    #     key1 = "p%d" % (i+1)
    #     key2 = "p%d" % (i+2)
    #     start_date = date_dic[key1][0]
    #     end_date = date_dic[key2][1]
    #     title = "%d%d" % (i+1,i+2) + title_flex + start_date + "~" + end_date
    #     block_k_data_daily_bokeh(block_list,start_date,end_date,title_name=title,cacl_type=3)

    ## S
    start_date = date_dic['p10'][0]
    end_date = date_dic["p10"][1]
    title = title_flex + start_date + "~" + end_date
    block_k_data_daily_bokeh(None,start_date,end_date,title_name=title,cacl_type=3)
    




    # industry_list = ['通信设备','电力','汽车零部件', '汽车整车', '证券']
    # industry_k_data_daily_bokeh(industry_list, 'hot-industry', file_path)
    # for industry in industry_list:
    #         stocks_in_industry_bokeh(industry, file_path)
   
    # block_list = ['航天装备', 'PET铜箔', '光伏概念']
    # block_k_data_daily_bokeh(block_list, 'hot-block', file_path)
    # for block in block_list:
    #     stocks_in_block_bokeh(block,file_path)

        # candlestick_with_turn_dma('sh.603533')
    # code_list = ['sz.300059', 'sh.600320', 'sh.600010', 'sz.300355', 'sh.688303', 'sh.600797',
    #              'sz.002415', 'sz.300021', 'sh.600477']
    # for code in code_list:
    #     candlestick_with_turn_dma(code)
    # industry_k_data_daily_bokeh()
    
    # file_path = "C:/server/nginx/html/"

    # candlestick_with_turn_dma('sz.300021', 65)