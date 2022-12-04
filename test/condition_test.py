# -*- encoding:utf-8 -*-
"""
date: 2020/9/6
author: Berserker
"""
from src.tool.database.base import SQLAlchemy
from src.models.stock import Stock
from src.strategy.condition.base import ConditionTypeEnum
from src.strategy.condition.volume_condition import VolumeChartPatternCondition
from src.strategy.condition.price_condition import PriceChartPatternCondition


def volume_test():
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == "sz.002370").first()
        k_data_list = stock.k_data_daily
        condition = VolumeChartPatternCondition()
        shareholder_list = stock.shareholders
        float_shareholder_list = stock.float_shareholders
        condition.prepare(k_data_list, shareholder_list, float_shareholder_list)
        ret = condition.judge(
            condition_type=ConditionTypeEnum.COND_VOLUME_CHART_PATTERN_AV_HEAP, start_index=-44, end_index=None
        )
        if not ret:
            return
        ret_data = condition.get_ret_data()
        for data in ret_data:
            print('%s === %s' % (k_data_list[data['start']], k_data_list[data['end']]))


def price_peak_test():
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == "sh.600114").first()
        k_data_list = stock.k_data_daily
        condition = PriceChartPatternCondition()
        condition.prepare(k_data_list)
        ret = condition.judge(
            condition_type=ConditionTypeEnum.COND_PRICE_CHART_PATTERN_PEAK, start_index=-48, end_index=None
        )
        if not ret:
            return
        ret_data = condition.get_ret_data()
        for data in ret_data:
            print('%s =peak= %s' % (k_data_list[data['start']], k_data_list[data['end']]))
        ret = condition.judge(
            condition_type=ConditionTypeEnum.COND_PRICE_CHART_PATTERN_PEAK, start_index=-48, end_index=None
        )
        if not ret:
            return
        ret_data = condition.get_ret_data()
        for data in ret_data:
            print('%s === %s' % (k_data_list[data['start']], k_data_list[data['end']]))


def price_gap_test():
    with SQLAlchemy.session_context() as session:
        stock = session.query(Stock).filter(Stock.code == "sz.300163").first()
        k_data_list = stock.k_data_daily
        condition = PriceChartPatternCondition()
        condition.prepare(k_data_list)
        ret = condition.judge(
            condition_type=ConditionTypeEnum.COND_PRICE_CHART_PATTERN_GAP_DOWN, start_index=-60, end_index=None
        )
        if not ret:
            return
        ret_data = condition.get_ret_data()
        for data in ret_data:
            print('%s =GAP= %s' % (k_data_list[data['start']], k_data_list[data['end']]))




if __name__ == '__main__':
    price_peak_test()