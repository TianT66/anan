# -*- coding: utf-8 -*-
"""
成长因子
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')


def is_growth_stock(revenue_growth, profit_growth, threshold=0.20):
    """
    判断是否为成长股
    营收增速 > threshold 且 利润正增长
    """
    return revenue_growth > threshold and profit_growth > 0


def calculate_growth_acceleration(current_growth, previous_growth):
    """
    计算成长加速
    >0 表示加速, <0 表示减速
    """
    if previous_growth == 0:
        return 0
    return current_growth - previous_growth


def has_scale_effect(revenue_growth, profit_growth):
    """
    是否有规模效应
    利润增速 > 营收增速
    """
    return profit_growth > revenue_growth


def calculate_cagr(value_start, value_end, years):
    """计算复合增长率"""
    if value_start <= 0 or years <= 0:
        return 0
    return (value_end / value_start) ** (1 / years) - 1


def get_growth_signal(revenue_growth, profit_growth, rd_ratio=0):
    """
    综合成长信号
    返回: 'fast_growth', 'stable_growth', 'slow_growth', 'declining'
    """
    if revenue_growth > 0.50 and profit_growth > 0.30:
        return 'fast_growth'
    elif revenue_growth > 0.20 and profit_growth > 0.10:
        return 'stable_growth'
    elif revenue_growth > 0:
        return 'slow_growth'
    else:
        return 'declining'


def is_innovation_driven(rd_ratio, revenue_growth):
    """
    是否为创新驱动型
    研发占比高 + 高增长
    """
    return rd_ratio > 0.05 and revenue_growth > 0.20