# -*- coding: utf-8 -*-
"""
估值因子
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')


def calculate_pe_percentile(pe_history, current_pe):
    """
    计算PE历史分位数
    """
    if pe_history is None or len(pe_history) < 10:
        return 0.5
    
    # 过滤无效PE值
    valid_pe = [p for p in pe_history if p > 0 and p < 200]
    if len(valid_pe) < 10:
        return 0.5
    
    # 计算分位数
    count_below = sum(1 for p in valid_pe if p < current_pe)
    percentile = count_below / len(valid_pe)
    
    return percentile


def calculate_pb_percentile(pb_history, current_pb):
    """
    计算PB历史分位数
    """
    if pb_history is None or len(pb_history) < 10:
        return 0.5
    
    valid_pb = [p for p in pb_history if p > 0 and p < 50]
    if len(valid_pb) < 10:
        return 0.5
    
    count_below = sum(1 for p in valid_pb if p < current_pb)
    percentile = count_below / len(valid_pb)
    
    return percentile


def get_valuation_signal(pe_percentile, pb_percentile):
    """
    综合估值信号
    返回: 'undervalued', 'normal', 'overvalued'
    """
    avg_percentile = (pe_percentile + pb_percentile) / 2
    
    if avg_percentile < 0.3:
        return 'undervalued'
    elif avg_percentile > 0.7:
        return 'overvalued'
    else:
        return 'normal'


def calculate_dividend_yield(dividend_per_share, price):
    """计算股息率"""
    if price <= 0:
        return 0
    return dividend_per_share / price


def calculate_earnings_yield(pe):
    """计算盈利收益率 (PE的倒数)"""
    if pe <= 0:
        return 0
    return 1 / pe


# 生成模拟历史PE/PB数据
def generate_mock_pe_history(code, current_pe):
    """生成模拟PE历史数据"""
    import random
    base = current_pe if current_pe > 0 else 15
    history = []
    for i in range(60):  # 5年数据
        pe = base * random.uniform(0.7, 1.3)
        history.append(pe)
    return history


def generate_mock_pb_history(code, current_pb):
    """生成模拟PB历史数据"""
    import random
    base = current_pb if current_pb > 0 else 1.5
    history = []
    for i in range(60):
        pb = base * random.uniform(0.7, 1.3)
        history.append(pb)
    return history