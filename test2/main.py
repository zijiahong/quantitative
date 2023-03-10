# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
from  kdj  import *
from datetime import datetime
import talib
import numpy as np


def init(context):
    subscribe(symbols='SHSE.513050', frequency='tick')
    subscribe(symbols='SHSE.513050', frequency='60s')

# def on_tick(context,tick):
#     # 仓位
#     position = context.account().position(symbol='SHSE.513050', side=PositionSide_Long)
#     if position != None and position.available_now:
#         # 符合预期定量卖出
#         if tick.price >position.vwap:
#             order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.price)
#             return
#         return 

#     # 判断相应的策略 定量买入
#     order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.price)

close = []
tick_kd = 0
flag = False
macd_list =[]
tick_macd_list = []

def on_tick(context,tick):
    global tick_macd_list,macd_list

    if len(high) < 30:
        return 

    
    # 09:10 之后再开始交易
    if tick.created_at < tick.created_at.replace(hour=9, minute=10, second=0, microsecond=0):
        return 
    
    
    position = context.account().position(symbol='SHSE.513050', side=PositionSide_Long)
    # 添加逃跑策略，跌了多少或者到达某个时间点
    if position != None and position.vwap - tick.quotes[0]['bid_p'] > 0.04:
        print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
        order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p'])
        return
    
    if position != None and position.available_now:
        # 符合预期定量卖出，买一的价格比当前持仓高1毫以上
        if tick.quotes[0]['bid_p'] > position.vwap:
            print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p']+0.001)
            return

        if tick.created_at > tick.created_at.replace(hour=14, minute=58, second=0, microsecond=0):
            print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p'])
            return
        return 


    # 时间判断 14:40 之后就不买了
    if tick.created_at > tick.created_at.replace(hour=14, minute=40, second=0, microsecond=0):
        return 
   
     
    macd, signal, hist = talib.MACD(np.array(close+[tick.quotes[0]['ask_p']]),fastperiod=12,slowperiod=26,signalperiod=9)
    
    if len(macd_list) < 4:
        return 
    if macd_list[-1] >0:
        flag = True

    tick_macd_list.append(macd[-1])
    if buy_signal(macd_list,tick_macd_list) and flag == True:
        # 买进
        print(tick.created_at,"买进",tick.quotes[0]['ask_p'])
        order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.quotes[0]['ask_p'])
        flag =False
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
def on_bar(context,bars):
    global tick_macd_list,macd_list,close

    if bars[0].bob <= bars[0].eob.replace(hour=9, minute=1, second=0, microsecond=0):
        close = []
        macd_list = []
    
    close.append(bars[0].close)
    if len(close) > 30 :
        macd, signal, hist = talib.MACD(np.array(close),fastperiod=12,slowperiod=26,signalperiod=9)
        macd_list.append(macd[-1])
       

if __name__ == '__main__':
    run(strategy_id='90ce0128-bbe0-11ed-bb17-5254008182e9',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='94ac22c44bf4d986d79e90bf6519f880b4b60411',
        backtest_start_time='2023-02-06 9:00:00',
        backtest_end_time='2023-03-06 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

