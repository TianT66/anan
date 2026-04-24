# -*- coding: utf-8 -*-
"""
工具函数模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def format_percentage(value, show_sign=True):
    """格式化百分比"""
    if show_sign:
        return f"{value:+.2f}%" if isinstance(value, (int, float)) else value
    return f"{value:.2f}%" if isinstance(value, (int, float)) else value


def format_money(value):
    """格式化金额"""
    if isinstance(value, (int, float)):
        if abs(value) >= 100000000:
            return f"{value/100000000:.2f}亿"
        elif abs(value) >= 10000:
            return f"{value/10000:.2f}万"
        else:
            return f"{value:.2f}元"
    return value


def calculate_annual_return(total_return, days):
    """计算年化收益率"""
    if days <= 0:
        return 0
    years = days / 244  # A股每年约244个交易日
    if years <= 0:
        return 0
    return (1 + total_return) ** (1 / years) - 1


def calculate_sharpe_ratio(returns, risk_free_rate=0.03):
    """计算夏普比率"""
    if not returns or len(returns) < 2:
        return 0
    
    returns = np.array(returns)
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    sharpe = (avg_return - risk_free_rate / 244) / std_return * np.sqrt(244)
    return sharpe


def calculate_max_drawdown(equity_curve):
    """计算最大回撤"""
    if not equity_curve:
        return 0
    
    values = np.array(equity_curve)
    peak = values[0]
    max_dd = 0
    
    for value in values:
        if value > peak:
            peak = value
        dd = (peak - value) / peak if peak > 0 else 0
        if dd > max_dd:
            max_dd = dd
    
    return max_dd


def is_trading_day(date, exchange='A'):
    """判断是否为交易日"""
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y%m%d')
    
    # 简单判断：排除周末
    if date.weekday() >= 5:
        return False
    
    return True


def get_trading_days(start_date, end_date):
    """获取交易日列表"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y%m%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y%m%d')
    
    days = []
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 排除周末
            days.append(current)
        current += timedelta(days=1)
    
    return days


def calculate_win_rate(trades):
    """计算胜率"""
    if not trades:
        return 0
    
    winning = sum(1 for t in trades if t.get('profit', 0) > 0)
    return winning / len(trades) if trades else 0


def calculate_profit_loss_ratio(trades):
    """计算盈亏比"""
    if not trades:
        return 0
    
    profits = [t['profit'] for t in trades if t.get('profit', 0) > 0]
    losses = [abs(t['profit']) for t in trades if t.get('profit', 0) < 0]
    
    avg_profit = sum(profits) / len(profits) if profits else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    
    return avg_profit / avg_loss if avg_loss > 0 else 0


def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='='):
    """打印进度条"""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if iteration == total:
        print()


def export_to_csv(data, filename):
    """导出数据到CSV"""
    if isinstance(data, pd.DataFrame):
        data.to_csv(filename, index=False, encoding='utf-8-sig')
        return True
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        return True
    return False


def log_trade(trade, log_file='trades.log'):
    """记录交易日志"""
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            log_line = f"{trade.get('date', '')},{trade.get('action', '')},"
            log_line += f"{trade.get('price', 0):.2f},{trade.get('quantity', 0)},"
            log_line += f"{trade.get('profit', 0):.2f}\n"
            f.write(log_line)
    except Exception as e:
        print(f"[ERROR] Failed to log trade: {e}")


class Logger:
    """简单日志记录器"""
    
    def __init__(self, name='QuantSystem'):
        self.name = name
    
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def warning(self, msg):
        print(f"[WARN] {msg}")
    
    def error(self, msg):
        print(f"[ERROR] {msg}")
    
    def success(self, msg):
        print(f"[OK] {msg}")


# 全局日志实例
logger = Logger()
