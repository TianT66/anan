# -*- coding: utf-8 -*-
"""
质量因子
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')


def is_high_quality(roe, gross_margin, debt_ratio):
    """
    判断是否为高质量公司
    ROE > 15%, 毛利率 > 30%, 负债率 < 60%
    """
    return roe > 15 and gross_margin > 30 and debt_ratio < 60


def calculate_roe(net_profit, equity):
    """计算ROE"""
    if equity <= 0:
        return 0
    return net_profit / equity


def calculate_gross_margin(revenue, cost):
    """计算毛利率"""
    if revenue <= 0:
        return 0
    return (revenue - cost) / revenue


def calculate_net_margin(revenue, net_profit):
    """计算净利率"""
    if revenue <= 0:
        return 0
    return net_profit / revenue


def calculate_debt_ratio(total_debt, total_assets):
    """计算负债率"""
    if total_assets <= 0:
        return 0
    return total_debt / total_assets


def get_quality_score(roe, gross_margin, net_margin, debt_ratio):
    """
    综合质量评分
    返回: 0-100
    """
    score = 0
    
    # ROE评分 (0-30)
    if roe > 25:
        score += 30
    elif roe > 20:
        score += 25
    elif roe > 15:
        score += 20
    elif roe > 10:
        score += 10
    elif roe > 5:
        score += 5
    
    # 毛利率评分 (0-25)
    if gross_margin > 50:
        score += 25
    elif gross_margin > 40:
        score += 20
    elif gross_margin > 30:
        score += 15
    elif gross_margin > 20:
        score += 10
    elif gross_margin > 10:
        score += 5
    
    # 净利率评分 (0-20)
    if net_margin > 20:
        score += 20
    elif net_margin > 15:
        score += 15
    elif net_margin > 10:
        score += 10
    elif net_margin > 5:
        score += 5
    
    # 负债率评分 (0-25) - 越低越好
    if debt_ratio < 30:
        score += 25
    elif debt_ratio < 40:
        score += 20
    elif debt_ratio < 50:
        score += 15
    elif debt_ratio < 60:
        score += 10
    elif debt_ratio < 70:
        score += 5
    
    return score