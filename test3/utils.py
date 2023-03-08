import talib
def qianzhi(list1):
    if list1[-1]<0 or list1[-2]<0 or list1[-3] <0 and list1[-1] < list1[-2] and list1[-3] < list1[-2]:
        return True
    return False


def buy_signal(list1,list2):

    if len(list2)<6:
        return False
    if list1[-2] < list1[-1] or list1[-3] < list1[-1] or list1[-3] < list1[-2] or list1[-1]>0 or list1[-2]>0 or list1[-3] >0 :
        return False

    
    dayuLast = 0
    Low = 0
    dayuLow = 0
    for v in list2:
        if dayuLast >=5: 
            if Low == 0:
                Low = v
                continue
            if v > Low:dayuLow+=1
            else: 
                dayuLast = 0
                dayuLow=0
        if v >= list1[-1]:dayuLast = 0
        else: dayuLast +=1
        
    return dayuLow>=4

import numpy as np
import pandas as pd
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

