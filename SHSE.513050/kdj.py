import pandas as pd
import numpy as np

# data = pd.DataFrame({
#     'high': [12.0, 13.0, 14.0, 15.0, 16.0],
#     'low': [8.0, 9.0, 10.0, 11.0, 12.0],
#     'close': [11.0, 12.0, 13.0, 14.0, 15.0],
# })


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



