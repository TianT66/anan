# -*- coding: utf-8 -*-
"""
价值策略 - 适用于价值蓝筹股（银行/保险/电力/石油）
均值回归 + 高股息再投资策略
"""

import sys
sys.path.insert(0, 'C:/Users/12408/.qclaw/workspace/QuantitativeTrading')


class ValueStrategy:
    """价值投资策略"""
    
    def __init__(self):
        self.name = "价值策略"
        self.description = "均值回归 + 高股息策略，适合低估值蓝筹股"
        self.buy_threshold = 30  # PE分位低于30%买入
        self.sell_threshold = 70  # PE分位高于70%卖出
        self.max_position = 0.4   # 最大40%仓位
        self.stop_loss = -0.08    # 止损8%
        self.take_profit = 0.20   # 止盈20%
        self.hold_period = 180    # 建议持有期180天
    
    def analyze(self, stock_data, fundamentals):
        """
        分析信号
        
        Args:
            stock_data: K线数据（含MA/PE历史等）
            fundamentals: 基本面数据
            
        Returns:
            dict: 信号结果
        """
        signals = {
            'strategy': self.name,
            'stock_type': 'VALUE',
            'score': 50,
            'signal': 'HOLD',
            'confidence': 0,
            'reasons': [],
            'position': 0,
            'stop_loss': 0,
            'take_profit': 0,
            'hold_period': self.hold_period
        }
        
        # 获取关键指标
        current_pe = fundamentals.get('pe', 15)
        current_pb = fundamentals.get('pb', 1.5)
        current_price = stock_data.get('close', 0)
        pe_history = stock_data.get('pe_history', [])
        ma20 = stock_data.get('ma20', current_price)
        ma60 = stock_data.get('ma60', current_price)
        dividend_yield = fundamentals.get('dividend_yield', 2)
        roe = fundamentals.get('roe', 10)
        
        # 1. PE分位计算
        pe_percentile = 50
        if pe_history:
            sorted_pes = sorted(pe_history)
            pe_percentile = sum(1 for p in sorted_pes if p < current_pe) / len(sorted_pes) * 100
        
        # 2. 估值评分（满分40分）
        valuation_score = 0
        
        if current_pe < 10:
            valuation_score += 20
            signals['reasons'].append(f"PE极低({current_pe:.1f})，严重低估")
        elif current_pe < 15:
            valuation_score += 15
            signals['reasons'].append(f"PE较低({current_pe:.1f})，相对低估")
        elif current_pe < 20:
            valuation_score += 10
            signals['reasons'].append(f"PE合理({current_pe:.1f})")
        elif current_pe < 30:
            valuation_score += 5
            signals['reasons'].append(f"PE偏高({current_pe:.1f})")
        else:
            signals['reasons'].append(f"PE偏高({current_pe:.1f})，估值较高")
        
        if current_pb < 1:
            valuation_score += 10
            signals['reasons'].append(f"破净(PB={current_pb:.2f})，安全边际高")
        elif current_pb < 2:
            valuation_score += 5
            signals['reasons'].append(f"PB较低({current_pb:.2f})")
        
        # PE分位评分（满分20分）
        if pe_percentile < 20:
            valuation_score += 20
            signals['reasons'].append(f"PE历史分位{pe_percentile:.0f}%，极度低估")
        elif pe_percentile < 30:
            valuation_score += 15
            signals['reasons'].append(f"PE历史分位{pe_percentile:.0f}%，低估")
        elif pe_percentile < 50:
            valuation_score += 10
        elif pe_percentile < 70:
            valuation_score += 5
        else:
            signals['reasons'].append(f"PE历史分位{pe_percentile:.0f}%，高估")
        
        # 3. 股息率评分（满分20分）
        dividend_score = 0
        if dividend_yield > 5:
            dividend_score = 20
            signals['reasons'].append(f"高股息率{dividend_yield:.1f}%，防御性强")
        elif dividend_yield > 3:
            dividend_score = 15
            signals['reasons'].append(f"股息率{dividend_yield:.1f}%，较为稳健")
        elif dividend_yield > 2:
            dividend_score = 10
            signals['reasons'].append(f"股息率{dividend_yield:.1f}%，可接受")
        
        # 4. 趋势评分（满分20分）
        trend_score = 0
        if current_price > ma20 > ma60:
            trend_score += 10
            signals['reasons'].append("均线多头排列，上升趋势良好")
        elif current_price > ma20:
            trend_score += 5
            signals['reasons'].append("价格站稳MA20")
        
        if current_price > ma60:
            trend_score += 10
        elif current_price > ma20:
            trend_score += 5
        
        # 计算总分
        total_score = valuation_score + dividend_score + trend_score
        signals['score'] = min(100, total_score)
        
        # 5. 生成信号
        if pe_percentile < self.buy_threshold and current_price > ma20:
            if pe_percentile < 20:
                signals['signal'] = 'STRONG_BUY'
                signals['confidence'] = 0.9
                signals['position'] = self.max_position
                signals['reasons'].append("强烈买入：低估值+趋势向上")
            else:
                signals['signal'] = 'BUY'
                signals['confidence'] = 0.7
                signals['position'] = 0.3
                signals['reasons'].append("建议买入：估值合理偏低")
        
        elif pe_percentile > self.sell_threshold:
            signals['signal'] = 'SELL'
            signals['confidence'] = 0.8
            signals['position'] = 0
            signals['reasons'].append("建议卖出：估值偏高")
        
        elif total_score > 60:
            signals['signal'] = 'HOLD'
            signals['confidence'] = 0.6
            signals['position'] = 0.2
        
        # 设置止损止盈
        signals['stop_loss'] = self.stop_loss
        signals['take_profit'] = self.take_profit
        
        return signals


def create_strategy():
    return ValueStrategy()
