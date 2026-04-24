# -*- coding: utf-8 -*-
"""
防御策略 - 适用于医药/食品等防御性股票
政策底买入 + 稳定增长策略
"""

import sys
sys.path.insert(0, 'C:/Users/12408/.qclaw/workspace/QuantitativeTrading')


class DefensiveStrategy:
    """防御性股票策略"""
    
    def __init__(self):
        self.name = "防御策略"
        self.description = "政策驱动 + 稳定增长，适合医药/食品等防御股"
        self.max_position = 0.35
        self.stop_loss = -0.10
        self.take_profit = 0.20
        self.hold_period = 150
    
    def analyze(self, stock_data, fundamentals):
        """分析信号"""
        signals = {
            'strategy': self.name,
            'stock_type': 'DEFENSIVE',
            'score': 50,
            'signal': 'HOLD',
            'confidence': 0,
            'reasons': [],
            'position': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'hold_period': self.hold_period
        }
        
        current_price = stock_data.get('close', 0)
        ma20 = stock_data.get('ma20', current_price)
        ma60 = stock_data.get('ma60', current_price)
        rsi6 = stock_data.get('rsi6', 50)
        macd = stock_data.get('macd', 0)
        
        pe = fundamentals.get('pe', 20)
        roe = fundamentals.get('roe', 12)
        revenue_growth = fundamentals.get('revenue_growth', 5)
        profit_growth = fundamentals.get('profit_growth', 5)
        policy_benefit = fundamentals.get('policy_benefit', 0)
        
        # 1. 估值评分（满分30分）
        val_score = 0
        if pe < 20:
            val_score += 20
            signals['reasons'].append(f"PE={pe:.1f}，估值合理偏低")
        elif pe < 30:
            val_score += 15
            signals['reasons'].append(f"PE={pe:.1f}，估值合理")
        elif pe < 40:
            val_score += 10
            signals['reasons'].append(f"PE={pe:.1f}，估值略高")
        
        # 2. 成长性评分（满分30分）
        growth_score = 0
        if revenue_growth > 20:
            growth_score += 20
            signals['reasons'].append(f"营收增长{revenue_growth:.1f}%，成长强劲")
        elif revenue_growth > 10:
            growth_score += 15
            signals['reasons'].append(f"营收增长{revenue_growth:.1f}%，稳健")
        elif revenue_growth > 5:
            growth_score += 10
        
        if profit_growth > revenue_growth:
            growth_score += 10
            signals['reasons'].append("利润增速>营收增速，规模效应好")
        
        # 3. 质量评分（满分25分）
        quality_score = 0
        if roe > 20:
            quality_score = 25
            signals['reasons'].append(f"ROE={roe:.1f}%，盈利质量极高")
        elif roe > 15:
            quality_score = 20
            signals['reasons'].append(f"ROE={roe:.1f}%，盈利质量良好")
        elif roe > 10:
            quality_score = 10
            signals['reasons'].append(f"ROE={roe:.1f}%，盈利一般")
        
        # 4. 技术面评分（满分15分）
        tech_score = 0
        if rsi6 < 35:
            tech_score += 10
            signals['reasons'].append("RSI超卖，技术反弹概率大")
        elif rsi6 < 50:
            tech_score += 5
        
        if macd > 0:
            tech_score += 5
            signals['reasons'].append("MACD水上，趋势向好")
        
        total_score = val_score + growth_score + quality_score + tech_score
        signals['score'] = min(100, total_score)
        
        # 生成信号
        if rsi6 < 35 and total_score > 55:
            signals['signal'] = 'STRONG_BUY'
            signals['confidence'] = 0.85
            signals['position'] = self.max_position
            signals['reasons'].append("强烈买入：超卖+基本面良好")
        elif total_score > 60:
            signals['signal'] = 'BUY'
            signals['confidence'] = 0.7
            signals['position'] = 0.25
        elif total_score < 40:
            signals['signal'] = 'SELL'
            signals['confidence'] = 0.6
            signals['position'] = 0
        
        signals['stop_loss'] = self.stop_loss
        signals['take_profit'] = self.take_profit
        
        return signals


def create_strategy():
    return DefensiveStrategy()
