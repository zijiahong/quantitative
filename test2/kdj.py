import pandas as pd

# data = pd.DataFrame({
#     'high': [12.0, 13.0, 14.0, 15.0, 16.0],
#     'low': [8.0, 9.0, 10.0, 11.0, 12.0],
#     'close': [11.0, 12.0, 13.0, 14.0, 15.0],
# })


def KDJ(high, low, close, n=9, m1=3, m2=3):
    # 最近n天的最高价（HHV)、最低价（LLV）以及当日收盘价(close)
    hhv = high.rolling(n, min_periods=0).max()
    llv = low.rolling(n, min_periods=0).min()
    rsv = (close - llv) / (hhv - llv) * 100
    k = rsv.ewm(alpha=1/m1,ignore_na=True,min_periods=0,adjust=False).mean()    
    d = k.ewm(alpha=1/m2,ignore_na=True,min_periods=0,adjust=False).mean() 
    j = 3 * k - 2 * d
    return k, d, j


def calc_kdj(data_list,n=9, m1=3, m2=3):
    high_list = []
    low_list = []
    rsv_list = []
    k_list = []
    d_list = []
    j_list = []

    for bar in data_list:
        high, low, close = bar['high'], bar['low'], bar['close']
        print(high, low, close)
        high_list.append(high)
        low_list.append(low)

        if len(high_list) < n:
            continue

        if len(high_list) > n:
            high_list.pop(0)
            low_list.pop(0)

        high_n = max(high_list)
        low_n = min(low_list)
        rsv = (close - low_n) / (high_n - low_n) * 100

        rsv_list.append(rsv)

        if len(rsv_list) < m1 + m2 - 1:
            continue

        if len(rsv_list) > m1 + m2 - 1:
            rsv_list.pop(0)

        k = sma(rsv_list, m1)
        d = sma(k_list, m2)
        j = 3 * k - 2 * d

        print(k,d,j)
        k_list.append(k)
        d_list.append(d)
        j_list.append(j)

    return k_list, d_list, j_list

def sma(lst, n):
    if len(lst) < n:
        return None
    return sum(lst[-n:]) / n

def calculate_kdj(data, n=9, m1=3, m2=3):
    """
    计算KDJ指标值
    :param data: pandas DataFrame对象，包含历史收盘价数据
    :param n: 周期数，默认为9
    :param m1: K值的平滑系数，默认为3
    :param m2: D值的平滑系数，默认为3
    :return: pandas DataFrame对象，包含计算得到的KDJ指标值
    """
    low_list = data['low'].rolling(window=n, min_periods=1).min()  # 计算n天内的最低价
    high_list = data['high'].rolling(window=n, min_periods=1).max()  # 计算n天内的最高价
    rsv = (data['close'] - low_list) / (high_list - low_list) * 100  # 计算未成熟随机值RSV
    k = pd.DataFrame({'k': rsv.ewm(com=m1).mean()})  # 计算K值
    d = pd.DataFrame({'d': k['k'].ewm(com=m2).mean()})  # 计算D值
    j = pd.DataFrame({'j': 3 * k['k'] - 2 * d['d']})  # 计算J值
    kdj_data = pd.concat([k, d, j], axis=1)  # 合并KDJ值
    return kdj_data




def buy_signal(list1,list2):
    if len(list2)<6:
        return False
    if list1[-2] > list1[-1] or list1[-3]>list1[-1]:
        return False
    dayuLast = 0
    Low = 0
    dayuLow = 0
    for i,v in list2:
        if dayuLast >=2: 
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