# -*- coding: utf-8 -*-
"""
短线策略 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')


class ShortTermStrategy:
    """短线策略类"""
    
    def __init__(self):
        self.name = "A股短线多因子策略 v3.0"
        self.description = "基于技术指标、K线形态、市场情绪的短线量化策略"
        
    def generate_signals(self, df, stock_code=None):
        """
        生成交易信号
        :param df: 历史数据
        :param stock_code: 股票代码
        :return: 信号列表
        """
        from engine.scorer import ComprehensiveScorer
        from engine.signal import SignalGenerator
        
        scorer = ComprehensiveScorer()
        signal_gen = SignalGenerator()
        
        # 计算评分
        score_result = scorer.score(df, stock_code)
        
        # 生成信号
        signal = signal_gen.generate_signal(df, score_result)
        
        return signal
    
    def get_strategy_params(self):
        """获取策略参数"""
        return {
            'name': self.name,
            'stop_loss': -0.05,
            'take_profit': 0.08,
            'max_hold_days': 5,
            'position_rules': {
                'heavy': {'min_score': 75, 'position': 0.40},
                'standard': {'min_score': 65, 'position': 0.25},
                'light': {'min_score': 55, 'position': 0.15},
            }
        }


# 全局实例
short_term_strategy = ShortTermStrategy()
