"""
策略模块 - 包含各种交易策略
"""
import pandas as pd
import numpy as np


class MAStrategy:
    """移动平均线策略"""
    
    @staticmethod
    def ma_cross(df: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.DataFrame:
        """
        均线金叉死叉策略
        
        Args:
            df: 包含收盘价的DataFrame
            fast: 快线周期
            slow: 慢线周期
        
        Returns:
            带信号列的DataFrame
        """
        df = df.copy()
        df['ma_fast'] = df['close'].rolling(window=fast).mean()
        df['ma_slow'] = df['close'].rolling(window=slow).mean()
        
        # 金叉买入，死叉卖出
        df['position'] = 0
        df.loc[df['ma_fast'] > df['ma_slow'], 'position'] = 1
        df.loc[df['ma_fast'] <= df['ma_slow'], 'position'] = -1
        
        # 只在状态变化时交易
        df['signal'] = df['position'].diff()
        
        return df
    
    @staticmethod
    def triple_ma(df: pd.DataFrame) -> pd.DataFrame:
        """三均线策略"""
        df = df.copy()
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        df['position'] = 0
        # 多头排列买入
        df.loc[(df['ma5'] > df['ma20']) & (df['ma20'] > df['ma60']), 'position'] = 1
        df['signal'] = df['position'].diff()
        
        return df


class RSIStrategy:
    """RSI 策略"""
    
    @staticmethod
    def rsi_strategy(df: pd.DataFrame, period: int = 14, 
                      oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
        """
        RSI 超买超卖策略
        
        Args:
            df: 包含收盘价的DataFrame
            period: RSI周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        df = df.copy()
        
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 生成信号
        df['position'] = 0
        df.loc[df['rsi'] < oversold, 'position'] = 1   # 超卖买入
        df.loc[df['rsi'] > overbought, 'position'] = -1  # 超买卖出
        
        df['signal'] = df['position'].diff()
        
        return df


class MACDStrategy:
    """MACD 策略"""
    
    @staticmethod
    def macd_strategy(df: pd.DataFrame,
                      fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        MACD 金叉死叉策略
        
        Args:
            df: 包含收盘价的DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        """
        df = df.copy()
        
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        
        df['macd'] = exp1 - exp2
        df['signal_line'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal_line']
        
        # 金叉买入，死叉卖出
        df['position'] = 0
        df.loc[df['histogram'] > 0, 'position'] = 1
        df.loc[df['histogram'] <= 0, 'position'] = -1
        
        df['signal'] = df['position'].diff()
        
        return df


class BollingerBandStrategy:
    """布林带策略"""
    
    @staticmethod
    def bollinger_bands(df: pd.DataFrame, window: int = 20, 
                       num_std: float = 2.0) -> pd.DataFrame:
        """
        布林带策略
        
        Args:
            df: 包含收盘价的DataFrame
            window: 移动平均周期
            num_std: 标准差倍数
        """
        df = df.copy()
        
        df['middle'] = df['close'].rolling(window=window).mean()
        df['std'] = df['close'].rolling(window=window).std()
        df['upper'] = df['middle'] + num_std * df['std']
        df['lower'] = df['middle'] - num_std * df['std']
        
        # 突破上轨买入，跌破下轨卖出
        df['position'] = 0
        df.loc[df['close'] < df['lower'], 'position'] = 1   # 价格低于下轨买入
        df.loc[df['close'] > df['upper'], 'position'] = -1  # 价格高于上轨卖出
        
        df['signal'] = df['position'].diff()
        
        return df


class TurtleStrategy:
    """海龟交易策略"""
    
    @staticmethod
    def turtle(df: pd.DataFrame, entry: int = 20, exit: int = 10, 
               atr_period: int = 20) -> pd.DataFrame:
        """
        海龟交易法则
        
        Args:
            df: 包含HLCV的DataFrame
            entry: 入场通道周期
            exit: 出场通道周期
            atr_period: ATR周期
        """
        df = df.copy()
        
        # 计算 ATR
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        df['tr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = df['tr'].rolling(window=atr_period).mean()
        
        # 计算高低通道
        df['entry_high'] = df['high'].rolling(window=entry).max()
        df['exit_low'] = df['low'].rolling(window=exit).min()
        
        # 交易逻辑
        df['position'] = 0
        df.loc[df['high'] > df['entry_high'], 'position'] = 1   # 突破20日高点买入
        df.loc[df['low'] < df['exit_low'], 'position'] = 0       # 跌破10日低点卖出
        
        df['signal'] = df['position'].diff()
        
        return df


# 策略注册表
STRATEGIES = {
    'ma_cross': MAStrategy,
    'rsi': RSIStrategy,
    'macd': MACDStrategy,
    'bollinger': BollingerBandStrategy,
    'turtle': TurtleStrategy,
}


def get_strategy(name: str):
    """获取策略类"""
    return STRATEGIES.get(name)
