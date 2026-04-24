# -*- coding: utf-8 -*-
"""
自适应策略 - 根据股票类型自动选择最优策略
"""

import sys
sys.path.insert(0, 'C:/Users/12408/.qclaw/workspace/QuantitativeTrading')

from classifier.stock_classifier import StockClassifier
from strategies.value_strategy import ValueStrategy
from strategies.cycle_strategy import CycleStrategy
from strategies.short_term import ShortTermStrategy
from strategies.multi_factor import MultiFactorStrategy
from strategies.defensive_strategy import DefensiveStrategy


class AdaptiveStrategy:
    """自适应量化策略"""
    
    def __init__(self):
        self.classifier = StockClassifier()
        self.strategies = {
            'VALUE': ValueStrategy(),
            'CONSUMER': ValueStrategy(),  # 消费股用价值逻辑
            'GROWTH': ShortTermStrategy(),
            'CYCLICAL': CycleStrategy(),
            'DEFENSIVE': DefensiveStrategy(),
            'NEW_ENERGY': ShortTermStrategy(),
        }
    
    def analyze(self, stock_data, fundamentals):
        """先分类股票，再选择对应策略"""
        # 1. 分类股票
        classification = self.classifier.classify_stock('unknown', fundamentals)
        stock_type = classification['type']
        confidence = classification['confidence']
        reasons = classification['reasons']
        
        # 2. 选择策略
        strategy = self.strategies.get(stock_type, MultiFactorStrategy())
        
        # 处理不同策略的接口差异
        if hasattr(strategy, 'analyze'):
            strategy_result = strategy.analyze(stock_data, fundamentals)
        elif hasattr(strategy, 'generate_signals'):
            # 短线策略接口不同，用简化处理
            strategy_result = {
                'strategy': strategy.name,
                'score': 50,
                'signal': 'HOLD',
                'confidence': 0.5,
                'position': 0,
                'stop_loss': -0.05,
                'take_profit': 0.15,
                'reasons': ['短线策略需结合实时数据分析']
            }
        else:
            strategy_result = {
                'strategy': 'MultiFactor',
                'score': 50,
                'signal': 'HOLD',
                'confidence': 0.5,
                'position': 0,
                'reasons': []
            }
        
        # 3. 合并结果
        result = {
            'stock_type': stock_type,
            'type_confidence': confidence,
            'type_reasons': reasons,
            'strategy': strategy_result.get('strategy', strategy_result.get('name', 'MultiFactor')),
            'score': strategy_result.get('score', strategy_result.get('total_score', 50)),
            'signal': strategy_result.get('signal', 'HOLD'),
            'confidence': strategy_result.get('confidence', 0.5),
            'position': strategy_result.get('position', 0),
            'stop_loss': strategy_result.get('stop_loss', -0.05),
            'take_profit': strategy_result.get('take_profit', 0.15),
            'hold_period': strategy_result.get('hold_period', 30),
            'reasons': strategy_result.get('reasons', [])
        }
        
        return result


def analyze_stock(code, stock_data, fundamentals):
    """分析单只股票的便捷函数"""
    adaptive = AdaptiveStrategy()
    result = adaptive.analyze(stock_data, fundamentals)
    result['code'] = code
    return result
