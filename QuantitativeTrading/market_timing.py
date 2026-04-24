# -*- coding: utf-8 -*-
"""
大盘择时系统 - 判断牛熊，动态调整仓位
一切以盈利为导向
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

import pandas as pd
import numpy as np


class MarketTiming:
    """大盘择时系统"""
    
    def __init__(self):
        self.index_code = '000300'  # 沪深300
        self.bull_threshold = 0.05   # 牛市阈值
        self.bear_threshold = -0.05  # 熊市阈值
    
    def get_index_data(self, days=60):
        """获取大盘指数数据"""
        try:
            import akshare as ak
            df = ak.index_zh_a_hist(symbol=self.index_code, period='daily',
                                     start_date='20250101', end_date='20250325')
            df.columns = [c.strip() for c in df.columns]
            df = df.rename(columns={'收盘': 'close', '日期': 'date'})
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            return df
        except Exception as e:
            print(f"[WARN] 获取大盘数据失败: {e}")
            # 返回模拟数据
            return self._mock_index_data()
    
    def _mock_index_data(self):
        """模拟大盘数据（用于测试）"""
        dates = pd.date_range('2025-01-01', '2025-03-25', freq='B')
        # 模拟沪深300在3800-4000区间震荡
        base = 3900
        closes = base + np.cumsum(np.random.randn(len(dates)) * 20)
        return pd.DataFrame({
            'date': dates,
            'close': closes
        })
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def get_market_status(self):
        """
        判断当前市场状态
        
        Returns:
            dict: {
                'status': 'BULL'/'BEAR'/'OSCILLATION',
                'position_suggestion': 0.0-1.0,
                'reason': str,
                'indicators': dict
            }
        """
        df = self.get_index_data()
        df = self.calculate_indicators(df)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        close = latest['close']
        ma20 = latest['ma20']
        ma60 = latest['ma60']
        macd = latest['macd']
        macd_signal = latest['macd_signal']
        rsi = latest['rsi']
        
        # 判断趋势
        trend_score = 0
        reasons = []
        
        # MA判断
        if close > ma20 > ma60:
            trend_score += 3
            reasons.append("均线多头排列")
        elif close > ma20:
            trend_score += 2
            reasons.append("价格在MA20上方")
        elif close < ma20 < ma60:
            trend_score -= 3
            reasons.append("均线空头排列")
        elif close < ma20:
            trend_score -= 2
            reasons.append("价格在MA20下方")
        
        # MACD判断
        if macd > macd_signal and macd > 0:
            trend_score += 2
            reasons.append("MACD水上金叉")
        elif macd > macd_signal:
            trend_score += 1
            reasons.append("MACD金叉")
        elif macd < macd_signal and macd < 0:
            trend_score -= 2
            reasons.append("MACD水下死叉")
        elif macd < macd_signal:
            trend_score -= 1
            reasons.append("MACD死叉")
        
        # RSI判断
        if rsi > 70:
            trend_score -= 1
            reasons.append("RSI超买")
        elif rsi < 30:
            trend_score += 1
            reasons.append("RSI超卖")
        elif 40 < rsi < 60:
            trend_score += 1
            reasons.append("RSI健康")
        
        # 确定市场状态
        if trend_score >= 4:
            status = 'BULL'
            position = 0.90
        elif trend_score >= 2:
            status = 'BULL_WEAK'
            position = 0.70
        elif trend_score <= -4:
            status = 'BEAR'
            position = 0.30
        elif trend_score <= -2:
            status = 'BEAR_WEAK'
            position = 0.50
        else:
            status = 'OSCILLATION'
            position = 0.60
        
        return {
            'status': status,
            'position_suggestion': position,
            'reason': '，'.join(reasons),
            'trend_score': trend_score,
            'indicators': {
                'close': close,
                'ma20': ma20,
                'ma60': ma60,
                'macd': macd,
                'rsi': rsi
            }
        }
    
    def get_sector_rotation(self):
        """行业轮动建议"""
        # 基于当前市场状态给出行业配置建议
        market = self.get_market_status()
        status = market['status']
        
        if status == 'BULL':
            return {
                'overweight': ['科技', '券商', '新能源'],  # 进攻
                'underweight': ['银行', '公用事业'],  # 防御
                'reason': '牛市进攻，配置高弹性板块'
            }
        elif status == 'BEAR':
            return {
                'overweight': ['银行', '医药', '消费'],  # 防御
                'underweight': ['科技', '券商', '周期'],  # 回避
                'reason': '熊市防御，配置低估值板块'
            }
        else:
            return {
                'overweight': ['消费', '医药', '科技'],  # 均衡
                'underweight': ['周期', '券商'],
                'reason': '震荡市均衡配置，精选个股'
            }


def print_market_report():
    """打印市场报告"""
    timing = MarketTiming()
    market = timing.get_market_status()
    sector = timing.get_sector_rotation()
    
    print("=" * 70)
    print("  大盘择时报告")
    print("=" * 70)
    
    status_map = {
        'BULL': '牛市',
        'BULL_WEAK': '弱牛市',
        'BEAR': '熊市',
        'BEAR_WEAK': '弱熊市',
        'OSCILLATION': '震荡市'
    }
    
    print(f"\n  当前市场状态: {status_map.get(market['status'], market['status'])}")
    print(f"  趋势评分: {market['trend_score']}/5")
    print(f"  建议仓位: {market['position_suggestion']*100:.0f}%")
    print(f"\n  判断依据:")
    print(f"    {market['reason']}")
    
    print(f"\n  技术指标:")
    ind = market['indicators']
    print(f"    沪深300: {ind['close']:.2f}")
    print(f"    MA20: {ind['ma20']:.2f}")
    print(f"    MA60: {ind['ma60']:.2f}")
    print(f"    MACD: {ind['macd']:.4f}")
    print(f"    RSI: {ind['rsi']:.2f}")
    
    print(f"\n  行业配置建议:")
    print(f"    超配: {', '.join(sector['overweight'])}")
    print(f"    低配: {', '.join(sector['underweight'])}")
    print(f"    理由: {sector['reason']}")
    
    print("=" * 70)


if __name__ == "__main__":
    print_market_report()
