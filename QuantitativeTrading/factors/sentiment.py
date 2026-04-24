# -*- coding: utf-8 -*-
"""
A股情绪因子模块 - A股短线量化系统 v3.0
包括板块效应、情绪周期等
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SentimentFactors:
    """A股情绪因子分析"""
    
    def __init__(self):
        self.market_sentiment = 0.0  # 市场情绪指标
        self.sector_strength = {}    # 板块强度
    
    def analyze_sentiment(self, df, stock_code, market_data=None):
        """
        分析市场情绪
        :param df: 个股数据
        :param stock_code: 股票代码
        :param market_data: 市场整体数据
        :return: 情绪得分
        """
        sentiment_score = 0
        details = []
        
        # 1. 市场情绪周期
        market_score, market_details = self._analyze_market_sentiment(market_data)
        sentiment_score += market_score
        details.extend(market_details)
        
        # 2. 板块效应
        sector_score, sector_details = self._analyze_sector_effect(df, stock_code)
        sentiment_score += sector_score
        details.extend(sector_details)
        
        # 3. 资金流向（如果数据可用）
        flow_score, flow_details = self._analyze_money_flow(df)
        sentiment_score += flow_score
        details.extend(flow_details)
        
        return {
            'score': sentiment_score,
            'details': details,
            'market_sentiment': self.market_sentiment,
            'sector_strength': self.sector_strength
        }
    
    def _analyze_market_sentiment(self, market_data=None):
        """
        分析市场情绪
        基于昨日涨停股今日表现
        """
        score = 0
        details = []
        
        # 默认市场情绪（中性）
        yzt_ratio = 0.02  # 昨日涨停股今日平均涨幅
        
        if market_data is not None and isinstance(market_data, dict):
            yzt_ratio = market_data.get('yzt_ratio', 0.02)
        
        self.market_sentiment = yzt_ratio
        
        # 情绪好：> 3%
        if yzt_ratio > 0.03:
            score += 10
            details.append(f"市场情绪好(涨停溢价+{yzt_ratio*100:.1f}%) [+10]")
        # 情绪差：< 0%
        elif yzt_ratio < 0:
            score -= 10
            details.append(f"市场情绪差(涨停溢价{yzt_ratio*100:.1f}%) [-10]")
        else:
            details.append(f"市场情绪中性(涨停溢价+{yzt_ratio*100:.1f}%)")
        
        return score, details
    
    def _analyze_sector_effect(self, df, stock_code):
        """
        分析板块效应
        """
        score = 0
        details = []
        
        if len(df) < 2:
            return score, details
        
        # 获取今日涨幅
        pct_change_today = df['pct_change'].iloc[-1]
        
        # 所属板块今日涨幅（模拟数据）
        sector_upgrade = self.sector_strength.get(stock_code, pct_change_today * 0.8)
        
        # 板块涨幅 > 2%：+15分
        if sector_upgrade > 2:
            score += 15
            details.append(f"所属板块强势(+{sector_upgrade:.1f}%) [+15]")
        elif sector_upgrade > 0:
            details.append(f"所属板块小幅上涨(+{sector_upgrade:.1f}%)")
        else:
            details.append(f"所属板块下跌({sector_upgrade:.1f}%)")
        
        # 龙头地位判断（成交量在板块前三）
        # 这里简化处理：涨幅超过板块均值则视为龙头
        if pct_change_today > sector_upgrade * 1.5:
            score += 10
            details.append("疑似板块龙头 [+10]")
        elif pct_change_today < sector_upgrade * 0.5 and sector_upgrade > 0:
            score -= 5
            details.append("跟风股迹象 [-5]")
        
        return score, details
    
    def _analyze_money_flow(self, df):
        """
        分析资金流向
        """
        score = 0
        details = []
        
        if len(df) < 5:
            return score, details
        
        # 计算5日/10日主力净流入占比趋势
        try:
            # 使用成交量变化模拟资金流向
            vol_ma5 = df['volume'].rolling(5).mean()
            vol_ma10 = df['volume'].rolling(10).mean()
            
            # 量能趋势
            vol_trend = (vol_ma5.iloc[-1] - vol_ma10.iloc[-1]) / vol_ma10.iloc[-1]
            
            # 5日主力净流入占比 > 3%：+20分
            # 这里用成交量占比模拟
            vol_ratio_5d = df['volume'].iloc[-5:].mean() / df['volume'].iloc[-10:-5].mean()
            if vol_ratio_5d > 1.03:
                score += 20
                details.append(f"资金持续净流入(+{(vol_ratio_5d-1)*100:.1f}%) [+20]")
            
            # 10日趋势上升：+15分
            if vol_trend > 0:
                score += 15
                details.append(f"量能趋势上升(+{vol_trend*100:.1f}%) [+15]")
            
            # 超大单迹象（放量且涨幅大）
            if df['pct_change'].iloc[-1] > 2 and df['vol_ratio'].iloc[-1] > 1.5 if 'vol_ratio' in df.columns else False:
                score += 10
                details.append("超大单净流入迹象 [+10]")
                
        except Exception as e:
            details.append(f"资金流向数据不足")
        
        return score, details
    
    def get_sector_movement(self, df):
        """
        获取板块日内走势
        用于判断板块联动效应
        """
        if len(df) < 1:
            return {}
        
        return {
            'sector_upgrade': df['pct_change'].mean() if len(df) > 0 else 0,
            'sector_strength': self._calculate_sector_strength(df),
        }
    
    def _calculate_sector_strength(self, df):
        """
        计算板块强度
        """
        if len(df) < 5:
            return 0
        
        # 使用涨跌幅和成交量综合判断
        upgrade_score = df['pct_change'].mean() * 10
        volume_score = (df['volume'].iloc[-1] / df['volume'].mean() - 1) * 5
        
        return upgrade_score + volume_score
    
    def update_market_sentiment(self, sentiment_data):
        """更新市场情绪数据"""
        if isinstance(sentiment_data, dict):
            self.market_sentiment = sentiment_data.get('yzt_ratio', 0.0)
    
    def update_sector_strength(self, stock_code, strength):
        """更新板块强度数据"""
        self.sector_strength[stock_code] = strength


# 全局实例
sentiment_analyzer = SentimentFactors()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    
    df = fetcher.get_daily_data('000528', '20240101', '20241231')
    
    # 需要先计算一些基础指标
    from factors.technical import tech_indicators
    df = tech_indicators.calculate_all(df)
    
    sa = SentimentFactors()
    result = sa.analyze_sentiment(df, '000528', {'yzt_ratio': 0.025})
    
    print(f"[OK] Sentiment Score: {result['score']}")
    print(f"Details: {result['details']}")
