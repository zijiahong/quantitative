# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
from  kdj  import *
from datetime import datetime


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


tick_high = []
tick_low = []
tick_close = []

high = []
low = []
close = []
min = 0
max = 0
kgtdc = 0
sdfk = 0
bardk = 0


def on_tick(context,tick):
    # 添加逃跑策略，跌了多少或者到达某个时间点

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

    # 考虑把 price 改成买一卖一
    global min,max,kgtdc,bardk
    if min == 0 or  tick.price < min:
        min = tick.price
    if max == 0 or tick.price > max:
        max = tick.price

    # 这个是当天的意识吗？数据不对
    position = context.account().position(symbol='SHSE.513050', side=PositionSide_Long)
    if position != None and position.available_now:
        # 符合预期定量卖出，买一的价格比当前持仓高1毫以上
        if tick.quotes[0]['bid_p'] > position.vwap+0.001:
            print(tick.created_at,"卖出",tick.quotes[0]['bid_p']+0.001)
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Sell, order_type=OrderType_Limit, position_effect=PositionEffect_Close,price=tick.quotes[0]['bid_p']+0.001)
        # 不持仓过夜
        return
    # 时间判断 14:40 之后就不买了
    print(tick.created_at)
    print(datetime.datetime.today().replace(hour=15, minute=0, second=0, microsecond=0))

    if tick.created_at < datetime.datetime.today().replace(hour=15, minute=0, second=0, microsecond=0):
        return 
    
     
    if len(high) > 15 :
        k,d,j = KDJ(pd.Series(high+[max]),pd.Series(low+[min]),pd.Series(close+[tick.price]))
        # k 和 d 收敛,d 大于 k 
        if abs(k.iloc[-1] - d.iloc[-1]) <=0.5:
            kgtdc+=1
        if  kgtdc > 1 and bardk > 2:
            # 买进
            print(tick.created_at,"买进",tick.quotes[0]['ask_p'])
            order_volume(symbol='SHSE.513050', volume=20000, side=OrderSide_Buy, order_type=OrderType_Limit, position_effect=PositionEffect_Open, price=tick.quotes[0]['ask_p'])
            kgtdc=0

def on_bar(context,bars):
    global min,max,bardk,kgtdc
    min = 0
    max = 0
    kgtdc = 0
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
    high.append(bars[0].high)
    low.append(bars[0].low)
    close.append(bars[0].close)
    if len(high) > 15 :
        k,d,j = KDJ(pd.Series(high),pd.Series(low),pd.Series(close))
        if d.iloc[-1]>k.iloc[-1]:
            bardk +=1
        else:
            bardk = 0
        d  = {'t': bars[0].eob.strftime('%Y-%m-%d %H:%M:%S'),'k':k.iloc[-1],'d':d.iloc[-1],'j':j.iloc[-1]}
        df = pd.DataFrame(d,index=[len(high)])
        with open('data.csv', mode='a', newline='') as file:
            df.to_csv(file, header=file.tell()==0, index=False)
    return 


if __name__ == '__main__':
    run(strategy_id='ee4a20af-bb3b-11ed-a0a6-d8bbc1dbf93d',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='94ac22c44bf4d986d79e90bf6519f880b4b60411',
        backtest_start_time='2023-02-06 09:00:00',
        backtest_end_time='2023-03-06 15:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

