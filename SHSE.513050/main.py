# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *

def init(context):
    subscribe(symbols='SHSE.513050', frequency='tick')
    subscribe(symbols='SHSE.513050', frequency='60s')

def on_tick(context,tick):
    # 仓位
    position = context.account().position(symbol='SHSE.513050', side=PositionSide_Long)
    if position != None and position.available_now:
        # 符合预期定量卖出
        if tick.price >position.vwap:
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.price)
            return
        return 

    # 判断相应的策略 定量买入
    order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.price)


def on_bar(context,bars):
    # symbol	str	标的代码
    # frequency	str	频率, 支持多种频率, 具体见股票行情数据和期货行情数据
    # open	float	开盘价
    # close	float	收盘价
    # high	float	最高价
    # low	float	最低价
    # amount	float	成交额
    # volume	long	成交量
    # position	long	持仓量（仅期货）
    # bob	datetime.datetime	bar开始时间
    # eob	datetime.datetime	bar结束时间
    # print("bars:",bars)    
    return 


if __name__ == '__main__':
    '''
        strategy_id策略ID, 由系统生成
        filename文件名, 请与本文件名保持一致
        mode运行模式, 实时模式:MODE_LIVE回测模式:MODE_BACKTEST
        token绑定计算机的ID, 可在系统设置-密钥管理中生成
        backtest_start_time回测开始时间
        backtest_end_time回测结束时间
        backtest_adjust股票复权方式, 不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
        backtest_initial_cash回测初始资金
        backtest_commission_ratio回测佣金比例
        backtest_slippage_ratio回测滑点比例
        '''
    run(strategy_id='90ce0128-bbe0-11ed-bb17-5254008182e9',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='94ac22c44bf4d986d79e90bf6519f880b4b60411',
        backtest_start_time='2023-03-06 14:50:00',
        backtest_end_time='2023-03-06 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

