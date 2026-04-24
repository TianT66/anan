# -*- coding: utf-8 -*-
"""
周期策略 - 适用于周期股（煤炭/钢铁/有色/化工/房地产）
PB择时 + 商品价格驱动策略
"""

import sys
sys.path.insert(0, 'C:/Users/12408/.qclaw/workspace/QuantitativeTrading')


class CycleStrategy:
    """周期股投资策略"""
    
    def __init__(self):
        self.name = "周期策略"
        self.description = "PB择时 + 商品驱动，适合强周期股票"
        self.buy_pb_threshold = 1.0   # PB<1时逆向布局
        self.sell_pb_threshold = 2.0  # PB>2时减仓
        self.max_position = 0.50      # 周期股仓位可以较重
        self.stop_loss = -0.12        # 止损12%（波动大）
        self.take_profit = 0.30       # 止盈30%
        self.hold_period = 120        # 建议持有期120天
    
    def analyze(self, stock_data, fundamentals):
        """分析信号"""
        signals = {
            'strategy': self.name,
            'stock_type': 'CYCLICAL',
            'score': 50,
            'signal': 'HOLD',
            'confidence': 0,
            'reasons': [],
            'position': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'hold_period': self.hold_period
        }
        
        current_pb = fundamentals.get('pb', 1.5)
        current_pe = fundamentals.get('pe', 15)
        current_price = stock_data.get('close', 0)
        ma20 = stock_data.get('ma20', current_price)
        ma60 = stock_data.get('ma60', current_price)
        ppi_trend = stock_data.get('ppi_trend', 0)  # PPI趋势
        commodity_price = stock_data.get('commodity_price', 0)  # 商品价格
        roe = fundamentals.get('roe', 10)
        
        # 1. PB估值评分（最重要！满分40分）
        pb_score = 0
        
        if current_pb < 0.8:
            pb_score = 40
            signals['reasons'].append(f"深度破净PB={current_pb:.2f}，极度低估")
        elif current_pb < 1.0:
            pb_score = 35
            signals['reasons'].append(f"破净PB={current_pb:.2f}，低估")
        elif current_pb < 1.2:
            pb_score = 30
            signals['reasons'].append(f"PB={current_pb:.2f}，相对低估")
        elif current_pb < 1.5:
            pb_score = 20
            signals['reasons'].append(f"PB={current_pb:.2f}，估值合理")
        elif current_pb < 2.0:
            pb_score = 10
            signals['reasons'].append(f"PB={current_pb:.2f}，估值偏高")
        else:
            signals['reasons'].append(f"PB={current_pb:.2f}，高估")
        
        # 2. 商品价格/宏观环境评分（满分30分）
        macro_score = 0
        
        if ppi_trend > 0:
            macro_score += 20
            signals['reasons'].append("PPI上行期，经济复苏利好周期股")
        elif ppi_trend == 0:
            macro_score += 10
        
        if commodity_price > 0:
            macro_score += 10
            signals['reasons'].append("商品价格上涨，周期股受益")
        
        # 3. ROE评分（满分15分）
        roe_score = 0
        if roe > 20:
            roe_score = 15
            signals['reasons'].append(f"ROE={roe:.1f}%，盈利能力强")
        elif roe > 15:
            roe_score = 10
            signals['reasons'].append(f"ROE={roe:.1f}%，盈利能力良好")
        elif roe > 10:
            roe_score = 5
            signals['reasons'].append(f"ROE={roe:.1f}%，一般")
        
        # 4. 趋势评分（满分15分）
        trend_score = 0
        if current_price > ma20 > ma60:
            trend_score = 15
            signals['reasons'].append("均线多头，上升趋势")
        elif current_price > ma20:
            trend_score = 10
            signals['reasons'].append("价格站上MA20")
        elif current_price > ma60:
            trend_score = 5
        
        # 计算总分
        total_score = pb_score + macro_score + roe_score + trend_score
        signals['score'] = min(100, total_score)
        
        # 5. 生成信号
        if current_pb < self.buy_pb_threshold and trend_score > 20:
            signals['signal'] = 'STRONG_BUY'
            signals['confidence'] = 0.85
            signals['position'] = self.max_position
            signals['reasons'].append("强烈买入：低PB+趋势向上")
        
        elif current_pb < 1.5 and macro_score > 20:
            signals['signal'] = 'BUY'
            signals['confidence'] = 0.75
            signals['position'] = 0.35
            signals['reasons'].append("建议买入：商品景气+估值合理")
        
        elif current_pb > self.sell_pb_threshold:
            signals['signal'] = 'SELL'
            signals['confidence'] = 0.8
            signals['position'] = 0
            signals['reasons'].append("建议卖出：PB偏高")
        
        elif total_score > 65:
            signals['signal'] = 'HOLD'
            signals['confidence'] = 0.6
            signals['position'] = 0.25
        
        signals['stop_loss'] = self.stop_loss
        signals['take_profit'] = self.take_profit
        
        return signals


def create_strategy():
    return CycleStrategy()
