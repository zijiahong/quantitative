# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import datetime
import numpy as np
import pandas as pd

def init(context):
    context.macd = {'SHSE.513050':[]}
    context.closes = {'SHSE.513050':[]}
    context.today_ignore = {'SHSE.513050':False}
    context.buy_signal = {'SHSE.513050':0}
    subscribe(symbols='SHSE.513050', frequency='tick')
    subscribe(symbols='SHSE.513050', frequency='60s')
    schedule(schedule_func=algo_1, date_rule='1d', time_rule='09:00:00')

    # subscribe(symbols='SHSE.513050', frequency='60s')

def on_tick(context, tick):
    print(tick)

def algo_1(context):
    for symbol in context.symbols:
        context.macd = {'SHSE.513050':[]}
        context.closes = {'SHSE.513050':[]}
        context.today_ignore = {'SHSE.513050':False}
        context.buy_signal = {'SHSE.513050':0}
        history_n_data = history_n(symbol=symbol, frequency='1d', count=36, end_time=context.now-datetime.timedelta(days=1) , fields='close', adjust=ADJUST_PREV, df=True)
        close_list = history_n_data['close'].tolist()
        context.closes[symbol] = close_list
        context.macd[symbol] = MACD_CN(close_list)
        print(symbol,context.now,context.macd[symbol][-1])

def on_tick(context, tick):
    if len(context.today_ignore) >0 and context.today_ignore[tick.symbol] ==True:
        return 
    position = context.account().position(symbol=tick.symbol, side=PositionSide_Long)
    if position != None and sell_signal(context,tick):
        print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
        order_volume(symbol=tick.symbol, volume=position.volume, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p'])
        context.today_ignore[tick.symbol] = True
        return
    
    if len(context.account(account_id=None).positions()) > 10:
        return  
    if buy_signal(context,tick):
        print(tick.created_at,"买进",tick.price)
        # 计算持仓
        order_volume(symbol=tick.symbol, volume=100000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.quotes[0]['bid_p'])
        context.today_ignore[tick.symbol] = True





if __name__ == '__main__':
    run(strategy_id='ee4a20af-bb3b-11ed-a0a6-d8bbc1dbf93d',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='94ac22c44bf4d986d79e90bf6519f880b4b60411',
        backtest_start_time='2022-01-05 09:00:00',
        backtest_end_time='2023-02-05 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=110000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)


def sell_signal(context,tick):
    position = context.account().position(symbol=tick.symbol,side = PositionSide_Long)
    if tick.price - position.vwap/position.vwap > 0.015:
        return True
    if MACD_CN(context.closes[tick.symbol]+[tick.quotes[0]['bid_p']])[-1] < 0:
        return True
    return False

def buy_signal(context,tick):
    if context.macd[tick.symbol][-1]>0 or context.macd[tick.symbol][-2]>0 or context.macd[tick.symbol][-3] > 0:
        return False
    # print(tick.created_at,MACD_CN(context.closes[tick.symbol]+[tick.quotes[0]['bid_p']])[-1])
    if MACD_CN(context.closes[tick.symbol]+[tick.quotes[0]['bid_p']])[-1]>0:
        # print(tick.create_at,context.buy_signal[tick.symbol])
        context.buy_signal[tick.symbol] +=1
        print(context.buy_signal[tick.symbol])
    if context.buy_signal[tick.symbol] > 20:
        return True
    return False

def MACD_CN(close,  fast_period=12, slow_period=26, signal_period=9):
    # 计算EMA12和EMA26
    ema12 = pd.Series(close).ewm(span=fast_period).mean()
    ema26 = pd.Series(close).ewm(span=slow_period).mean()
    # 计算DIF
    dif = ema12 - ema26
    # 计算DEM9
    dem9 = dif.ewm(span=signal_period).mean()
    # 计算MACD
    macd = (dif - dem9)*2
    # 返回MACD柱状图的值
    return np.array(macd)