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

high = []
low = []
close = []
min = 0
max = 0
tick_kd = 0
bar_dk = 0
last_macd = 0
flag = False
macd_list =[]

# symbol	str	标的代码
# open	float	日线开盘价
# high	float	日线最高价
# low	float	日线最低价
# price	float	最新价
# cum_volume	long	成交总量/最新成交量,累计值（日线成交量）
# cum_amount	float	成交总金额/最新成交额,累计值 （日线成交金额）
# cum_position	int	合约持仓量(只适用于期货),累计值（股票此值为0）
# trade_type	int	交易类型（只适用于期货） 1: ‘双开’, 2: ‘双平’, 3: ‘多开’, 4: ‘空开’, 5: ‘空平’, 6: ‘多平’, 7: ‘多换’, 8: ‘空换’
# last_volume	int	瞬时成交量
# last_amount	float	瞬时成交额（郑商所last_amount为0）
# quotes	[] (list of dict)
    # bid_p	float	买价
    # bid_v	int	买量
    # ask_p	float	卖价
    # ask_v	int	卖量
def on_tick(context,tick):
    global tick_kd,flag,macd_list
    
    # # 考虑把 price 改成买一卖一
    # global min,max,tick_kd,bar_dk
    # if min == 0 or  tick.quotes[0]['ask_p'] < min:
    #     min = tick.quotes[0]['ask_p']
    # if max == 0 or tick.quotes[0]['bid_p'] > max:
    #     max = tick.quotes[0]['bid_p']

    if len(high) < 30:
        return 

    # k,d,j = KDJ(pd.Series(high+[max]),pd.Series(low+[min]),pd.Series(close+[tick.price]))
    # dd  = {'t': tick.created_at.strftime('%Y-%m-%d %H:%M:%S'),'k':k.iloc[-1],'d':d.iloc[-1],'j':j.iloc[-1]}
    # df = pd.DataFrame(dd,index=[len(high)])
    # with open('data.csv', mode='a', newline='') as file:
    #     df.to_csv(file, header=file.tell()==0, index=False)


    # 09:10 之后再开始交易
    if tick.created_at < tick.created_at.replace(hour=9, minute=10, second=0, microsecond=0):
        return 
    
    position = context.account().position(symbol='SHSE.513050', side=PositionSide_Long)
    
    # 添加逃跑策略，跌了多少或者到达某个时间点
    if position != None and position.vwap - tick.quotes[0]['bid_p'] > 0.04:
        print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
        bar_dk=0
        tick_kd=0
        order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p'])
        return
    
    if position != None and position.available_now:
        # 符合预期定量卖出，买一的价格比当前持仓高1毫以上
        if tick.quotes[0]['bid_p'] > position.vwap:
            print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
            bar_dk=0
            tick_kd=0
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p']+0.001)
            return

        # 不持仓过夜
        # print(tick.created_at,tick.created_at.replace(hour=14, minute=58, second=0, microsecond=0))
        # print(tick.created_at < tick.created_at.replace(hour=14, minute=58, second=0, microsecond=0))
        if tick.created_at > tick.created_at.replace(hour=14, minute=58, second=0, microsecond=0):
            print(tick.created_at,"卖出",tick.quotes[0]['bid_p'])
            bar_dk=0
            tick_kd=0
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p'])
            return
        return 
   
    # 时间判断 14:40 之后就不买了
    if tick.created_at > tick.created_at.replace(hour=14, minute=40, second=0, microsecond=0):
        return 
     
    macd, signal, hist = talib.MACD(np.array(close+[tick.quotes[0]['ask_p']]),fastperiod=12,slowperiod=26,signalperiod=9)
    # k 和 d 收敛,d 大于 k 
    # if  k.iloc[-1] > d.iloc[-1]:
    #     tick_kd +=1
    if len(macd_list) < 4:
        return 
    if macd_list[-1] >0:
        flag = True
    if buy_signal(macd_list+macd[-1:]):
        print(macd_list[-3],macd_list[-2],macd_list[-1],macd[-1:])
        tick_kd+=1
    if tick_kd >=5 and flag == True:
        # 买进
        print(tick.created_at,"买进",tick.quotes[0]['ask_p'])
        order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.quotes[0]['ask_p'])
        tick_kd=0
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
    global min,max,bar_dk,tick_kd,high,low,close,macd_list
    min = 0
    max = 0
    tick_kd = 0

    if bars[0].bob <= bars[0].eob.replace(hour=9, minute=1, second=0, microsecond=0):
        high = []
        low = []
        close = []
        bar_dk = 0
        macd_list = []
    
    high.append(bars[0].high)
    low.append(bars[0].low)
    close.append(bars[0].close)
    if len(high) > 30 :
        macd, signal, hist = talib.MACD(np.array(close),fastperiod=12,slowperiod=26,signalperiod=9)
        macd_list.append(macd[-1])

        k,d,j = KDJ(pd.Series(high),pd.Series(low),pd.Series(close))
        if d.iloc[-1]>k.iloc[-1] and abs(d.iloc[-1]-k.iloc[-1])>5:
            if bar_dk == 0 and abs(d.iloc[-1]-k.iloc[-1])>15:
                bar_dk +=1
            elif bar_dk == 1 and abs(d.iloc[-1]-k.iloc[-1])>10:
                bar_dk +=1
            else:
                bar_dk +=1
            
        else:
            bar_dk = 0
        d  = {'t': bars[0].bob.strftime('%Y-%m-%d %H:%M:%S'),'k':k.iloc[-1],'d':d.iloc[-1],'j':j.iloc[-1]}
        df = pd.DataFrame(d,index=[len(high)])
        with open('data.csv', mode='a', newline='') as file:
            df.to_csv(file, header=file.tell()==0, index=False)
    return 


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

