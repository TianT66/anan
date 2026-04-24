# -*- coding: utf-8 -*-
"""
动量因子
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')


def calculate_momentum(df, period=20):
    """计算动量（20日涨幅）"""
    if df is None or len(df) < period:
        return 0
    if 'close' not in df.columns:
        return 0
    
    current = df['close'].iloc[-1]
    past = df['close'].iloc[-period]
    
    if past <= 0:
        return 0
    
    return (current - past) / past


def is_momentum_stock(df, benchmark_change=0, period=20):
    """
    判断是否为动量强势股
    涨幅 > 基准涨幅
    """
    momentum = calculate_momentum(df, period)
    return momentum > benchmark_change


def calculate_relative_strength(stock_change, index_change):
    """计算相对强弱（超额收益）"""
    return stock_change - index_change


def is_breakout(df, period=20):
    """
    判断是否突破20日高点
    """
    if df is None or len(df) < period:
        return False
    if 'close' not in df.columns:
        return False
    
    current_price = df['close'].iloc[-1]
    high_20 = df['high'].iloc[-period:].max()
    
    return current_price >= high_20


def is_breakdown(df, period=10):
    """
    判断是否跌破10日低点
    """
    if df is None or len(df) < period:
        return False
    if 'close' not in df.columns:
        return False
    
    current_price = df['close'].iloc[-1]
    low_10 = df['low'].iloc[-period:].min()
    
    return current_price <= low_10


def detect_volume_surge(df, period=20, threshold=1.5):
    """
    检测成交量是否放大
    threshold: 量比阈值
    """
    if df is None or len(df) < period + 1:
        return False
    if 'volume' not in df.columns:
        return False
    
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].iloc[-period:].mean()
    
    return current_volume > avg_volume * threshold