# -*- encoding:utf-8 -*-
"""
date: 2020/8/23
author: Berserker
"""
from quant.strategy.base import Variable, VariableTypeEnum
from quant.tool.database.base import SQLAlchemy
from quant.models.stock import Stock
from quant.strategy.factor.select_stock_factor import StockBuildPositionFactor, StockOversoldFactor, StockLivelyFactor
from quant.libs.enums import StockTypeEnum
from quant.tool.sel_stock_file_builder import SelStockFileBuilder
from quant.tool.database.data_models.block import BlockData
from quant.models.block import Block


def found_lively_stock(except_code_list=None):
    factor = StockLivelyFactor(-20, None)
    ret_list = []
    with SQLAlchemy.session_context() as session:
        stock_list = session.query(Stock).filter(Stock._stock_type == StockTypeEnum.STOCK_SHARES.value).all()
    for stock in stock_list:
        if stock.is_st() or stock.is_delisted():
            continue
        if except_code_list and stock.id in except_code_list:
            continue
        with SQLAlchemy.session_context() as session:
            stock = session.merge(stock)
            k_data_list = stock.k_data_daily
            shareholder_list = stock.shareholders
            float_shareholder_list = stock.float_shareholders
            k_data_hourly_list = stock.k_data_hourly
        coe_recent_mini = 1.13
        ret = factor.estimate(
            data_list=k_data_list, shareholder_list=shareholder_list, float_shareholder_list=float_shareholder_list,
            coe_recent_mini=coe_recent_mini, k_data_hourly_list=k_data_hourly_list)
        if not ret:
            continue

        ret_list.append(stock)
    return ret_list


def found_establish_position_stock(except_code_list=None):
    factor = StockBuildPositionFactor(-20, None)
    ret_list = []
    with SQLAlchemy.session_context() as session:
        stock_list = session.query(Stock).filter(Stock._stock_type == StockTypeEnum.STOCK_SHARES.value).all()
        for stock in stock_list:
            if stock.is_st() or stock.is_delisted():
                continue
            if except_code_list and stock.id in except_code_list:
                continue
            k_data_list = stock.k_data_daily
            shareholder_list = stock.shareholders
            float_shareholder_list = stock.float_shareholders
            coe_recent_fluctuation = 1.0
            coe_fluctuation = 1.5
            coe_recent_mini = 1.5
            ret = factor.estimate(
                data_list=k_data_list, shareholder_list=shareholder_list, float_shareholder_list=float_shareholder_list,
                coe_recent_fluctuation=coe_recent_fluctuation, coe_fluctuation=coe_fluctuation,
                coe_recent_mini=coe_recent_mini)
            if not ret:
                continue
            ret_list.append(stock)
    return ret_list


def found_oversold_stock(except_code_list=None):
    factor = StockOversoldFactor(-15, None)
    ret_list = []
    block_temp_list = []
    with SQLAlchemy.session_context() as session:
        block_list = session.query(Block).all()
        for block in block_list:
            block_data_list = BlockData.query_block_data(session, block)[-15:]
            if not block_data_list:
                continue
            data_max = max(block_data_list, key=Variable.get_fun(VariableTypeEnum.K_DATA_CLOSE))
            data_min = min(block_data_list, key=Variable.get_fun(VariableTypeEnum.K_DATA_CLOSE))
            index_max = block_data_list.index(data_max)
            index_min = block_data_list.index(data_min)
            if index_max > index_min:
                continue
            coe_pct_chg = data_min.close / data_max.close - 1
            block_temp_list.append((coe_pct_chg, block))

        block_temp_list.sort(key=lambda elem: elem[0])
        for pct_chg, block in block_temp_list:
            print(block, pct_chg)
            stock_list = block.stocks
            for stock in stock_list:
                if stock.is_st() or stock.is_delisted():
                    continue
                if except_code_list and stock.id in except_code_list:
                    continue
                shareholder_list = stock.shareholders
                float_shareholder_list = stock.float_shareholders
                k_data_list = stock.k_data_daily
                ret = factor.estimate(
                    data_list=k_data_list, coe_pct_chg=pct_chg, shareholder_list=shareholder_list,
                    float_shareholder_list=float_shareholder_list
                )
                if not ret:
                    continue

                if stock not in ret_list:
                    ret_list.append(stock)
    return ret_list


def main():

    stocks = found_lively_stock()

    # stocks = found_oversold_stock()

    with SelStockFileBuilder('.', 'temp') as builder:
        for s in stocks:
            builder.append_stock_code(s.code)

    for s in stocks:
        str_list = s.code.split(".")
        code = str_list[1] + "." + str_list[0].upper()
        print(code)


if __name__ == '__main__':
    main()
    pass

