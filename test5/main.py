# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import datetime
import numpy as np
import pandas as pd
import sys
import logging

def init(context):

    # 配置日志格式和级别
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    # 上交所	SHSE
    # 深交所	SZSE
    context.symbols_list = {
        'SHSE.513050':  '中概互联',
        'SHSE.512800':  '银行',
        'SHSE.516080':  '创新药',
        'SHSE.512900':  '证券基金',
        'SHSE.510880':  '红利ETF',
        'SHSE.512170':  '医药ETF',
        'SHSE.501029':  '红利基金',
        'SHSE.512580':  '环保ETF',
        'SHSE.512680':  '中证军工ETF',
        'SHSE.515300':  '红利300',
        'SHSE.510900':  'H股ETF',
        'SHSE.512980':  '中证传媒',
        'SHSE.516950':  '中证基建',
        'SHSE.515000':  '科技龙头',

        'SZSE.159996':  '家电',
        'SZSE.159913':  '深价值',
        'SZSE.159938':  '医药',
        'SZSE.159837':  '生物科技',
        'SZSE.159938':  '广发医药',
        }
    
    context.macd = {}
    context.closes= {}
    context.today_ignore= {}
    context.buy_signal= {}

    # subscribe(symbols=context.symbols_list.keys(), frequency='tick')
    subscribe(symbols=context.symbols_list.keys(), frequency='60s')
    schedule(schedule_func=algo_1, date_rule='1d', time_rule='09:00:00')


def init_params(context):
    context.macd = {}
    context.closes= {}
    context.today_ignore= {}
    context.buy_signal= {}
    for k in context.symbols_list.keys():
        context.macd.setdefault(k,[])
        context.closes.setdefault(k,[])
        context.today_ignore.setdefault(k,False)
        context.buy_signal.setdefault(k,0)

def algo_1(context):
    init_params(context)
    for symbol in context.symbols:
        history_n_data = history_n(symbol=symbol, frequency='1d', count=36, end_time=context.now-datetime.timedelta(days=1) , fields='close', adjust=ADJUST_PREV, df=True)
        close_list = history_n_data['close'].tolist()
        context.closes[symbol] = close_list
        context.macd[symbol] = MACD_CN(close_list)
        logging.info("{} {} {}".format(symbol,context.now,context.macd[symbol][-1]))


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
    for bar in bars:
        if context.today_ignore[bar.symbol] ==True:
            return 
        position = context.account().position(symbol=bar.symbol, side=PositionSide_Long)
        if position != None and sell_signal(context,bar):
            logging.info("{} {} {} {} {}".format(bar.symbol,context.symbols_list[bar.symbol],bar.eob,"卖出",bar.close,position.volume,"股"))
            order_volume(symbol=bar.symbol, volume=position.volume, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=bar.close)
            context.today_ignore[bar.symbol] = True
            return
        
        if len(context.account(account_id=None).positions()) > 10:
            return  
        if buy_signal(context,bar):
            logging.info("{} {} {} {} {}".format(bar.symbol,context.symbols_list[bar.symbol],bar.eob,"买进",bar.close, calcu_count(10000,bar.close) ,"股"))
            order_volume(symbol=bar.symbol, volume=calcu_count(10000,bar.close), side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=bar.close)
            context.today_ignore[bar.symbol] = True


if __name__ == '__main__':
    run(strategy_id='90ce0128-bbe0-11ed-bb17-5254008182e9',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='94ac22c44bf4d986d79e90bf6519f880b4b60411',
        backtest_start_time='2022-01-027 09:00:00',
        backtest_end_time='2023-02-05 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=110000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)


def calcu_count(cash,price):
    return int(cash/price/100) * 100

def sell_signal(context,bar):
    position = context.account().position(symbol=bar.symbol,side = PositionSide_Long)
    # 股票涨幅在1个点以上或者跌3个点就跑路
    logging.info("{} {} 当前{} 买入{} 涨跌{}".format(bar.symbol,context.symbols_list[bar.symbol],bar.close,position.vwap,(bar.close - position.vwap)/position.vwap))
    if (bar.close - position.vwap)/position.vwap > 0.01 or (position.vwap - bar.close )/position.vwap >0.03:
        return True
    # 昨天是负数今天也是负数,买入的时机不对
    if MACD_CN(context.closes[bar.symbol])[-1]<0 and MACD_CN(context.closes[bar.symbol]+[bar.close])[-1] < 0:
        return True
    return False

def buy_signal(context,bar):
    cur_macd = MACD_CN(context.closes[bar.symbol]+[bar.close])
    # 前天和大前天存在指标大于 0 的不能买
    if context.macd[bar.symbol][-2]>0 or context.macd[bar.symbol][-3] > 0:
        return False
    # 前天和大前天存在指标小于 0，昨天大于 0 且今天 大于 0
    if context.macd[bar.symbol][-2]<0 and  context.macd[bar.symbol][-3] < 0 and context.macd[bar.symbol][-1] > 0 and cur_macd[-1]>0:
        return True
    
    # 前三天小于 0，今天连续很多次大于 0
    if cur_macd[-1]>0:
        context.buy_signal[bar.symbol] +=1
    else:
        context.buy_signal[bar.symbol] = 0
    if context.buy_signal[bar.symbol] > 180:
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