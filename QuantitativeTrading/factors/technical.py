# -*- coding: utf-8 -*-
"""
技术指标因子
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd


def calculate_ma(df, period=20):
    """计算移动平均线"""
    if df is None or len(df) < period:
        return None
    if 'close' in df.columns:
        return df['close'].rolling(window=period).mean()
    return None


def calculate_ema(df, period=20):
    """计算指数移动平均线"""
    if df is None or len(df) < period:
        return None
    if 'close' in df.columns:
        return df['close'].ewm(span=period, adjust=False).mean()
    return None


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    计算MACD指标
    返回: DIF, DEA, MACD
    """
    if df is None or len(df) < slow:
        return None, None, None
    
    if 'close' not in df.columns:
        return None, None, None
    
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd = 2 * (dif - dea)
    
    return dif, dea, macd


def calculate_rsi(df, period=14):
    """计算RSI指标"""
    if df is None or len(df) < period + 1:
        return None
    
    if 'close' not in df.columns:
        return None
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_bollinger(df, period=20, std_dev=2):
    """计算布林带"""
    if df is None or len(df) < period:
        return None, None, None
    
    if 'close' not in df.columns:
        return None, None, None
    
    ma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    
    upper = ma + std_dev * std
    lower = ma - std_dev * std
    
    return upper, ma, lower


def calculate_volume_ratio(df, period=20):
    """计算量比"""
    if df is None or len(df) < period + 1:
        return None
    
    if 'volume' not in df.columns:
        return None
    
    avg_volume = df['volume'].rolling(window=period).mean()
    volume_ratio = df['volume'] / avg_volume
    
    return volume_ratio


def calculate_atr(df, period=14):
    """计算真实波幅ATR"""
    if df is None or len(df) < period + 1:
        return None
    
    required = ['high', 'low', 'close']
    if not all(col in df.columns for col in required):
        return None
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def get_technical_signals(df):
    """
    综合技术信号
    返回: dict of signals
    """
    if df is None or len(df) < 30:
        return {}
    
    signals = {}
    
    # MA信号
    ma20 = calculate_ma(df, 20)
    ma60 = calculate_ma(df, 60)
    
    if ma20 is not None and ma60 is not None:
        last = df['close'].iloc[-1]
        signals['price_above_ma20'] = last > ma20.iloc[-1] if len(ma20) > 0 else False
        signals['price_above_ma60'] = last > ma60.iloc[-1] if len(ma60) > 0 else False
        signals['ma20_above_ma60'] = ma20.iloc[-1] > ma60.iloc[-1] if len(ma20) > 0 and len(ma60) > 0 else False
    
    # MACD信号
    dif, dea, macd = calculate_macd(df)
    if dif is not None and dea is not None:
        signals['macd_golden_cross'] = dif.iloc[-1] > dea.iloc[-1]
        signals['macd_red'] = macd.iloc[-1] > 0 if macd is not None else False
    
    # RSI信号
    rsi = calculate_rsi(df)
    if rsi is not None:
        signals['rsi'] = rsi.iloc[-1]
        signals['rsi_overbought'] = rsi.iloc[-1] > 70
        signals['rsi_oversold'] = rsi.iloc[-1] < 30
    
    # 成交量信号
    vol_ratio = calculate_volume_ratio(df)
    if vol_ratio is not None:
        signals['volume_ratio'] = vol_ratio.iloc[-1]
        signals['volume_increase'] = vol_ratio.iloc[-1] > 1.5
    
    # 20日涨幅
    if len(df) >= 20:
        change_20 = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
        signals['change_20d'] = change_20
    
    return signals