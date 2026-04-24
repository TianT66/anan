# -*- coding: utf-8 -*-
"""
仓位管理模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime


class PositionManager:
    """仓位管理器"""
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.current_position = 0  # 当前持仓股数
        self.current_price = 0     # 持仓成本
        self.hold_days = 0        # 持仓天数
        self.buy_date = None      # 买入日期
        self.trades = []          # 交易记录
        self.equity_curve = []    # 权益曲线
        
        # 止损止盈配置
        self.stop_loss = -0.05     # 止损 -5%
        self.take_profit = 0.08   # 止盈 +8%
        self.max_hold_days = 5    # 最大持仓天数
    
    def update_position(self, action, price, quantity=0, date=None):
        """
        更新持仓状态
        :param action: 'BUY'/'SELL'/'ADD'/'REDUCE'
        :param price: 交易价格
        :param quantity: 交易数量
        :param date: 交易日期
        """
        if date is None:
            date = datetime.now()
        
        if action in ['BUY', 'ADD']:
            # 买入
            cost = price * quantity
            commission = cost * 0.0003  # 手续费
            
            if cost + commission <= self.current_cash:
                self.current_cash -= (cost + commission)
                avg_cost = (self.current_position * self.current_price + cost) / (self.current_position + quantity)
                self.current_position += quantity
                self.current_price = avg_cost
                self.hold_days = 0
                self.buy_date = date
                
                self.trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': price,
                    'quantity': quantity,
                    'cost': cost,
                    'commission': commission,
                    'position': self.current_position,
                    'cash': self.current_cash
                })
                return True
            else:
                return False
        
        elif action in ['SELL', 'REDUCE', 'STOP_LOSS', 'TAKE_PROFIT']:
            # 卖出
            if self.current_position <= 0:
                return False
            
            sell_qty = min(quantity, self.current_position)
            revenue = price * sell_qty
            commission = revenue * 0.0003
            stamp_duty = revenue * 0.001  # 印花税
            net_revenue = revenue - commission - stamp_duty
            
            self.current_cash += net_revenue
            self.current_position -= sell_qty
            
            # 计算盈亏
            cost_basis = sell_qty * self.current_price
            profit = net_revenue - cost_basis
            
            self.trades.append({
                'date': date,
                'action': action,
                'price': price,
                'quantity': sell_qty,
                'revenue': revenue,
                'commission': commission,
                'stamp_duty': stamp_duty,
                'profit': profit,
                'profit_rate': profit / cost_basis if cost_basis > 0 else 0,
                'position': self.current_position,
                'cash': self.current_cash
            })
            
            # 如果全部卖出，重置成本
            if self.current_position == 0:
                self.current_price = 0
                self.buy_date = None
                self.hold_days = 0
            
            return True
        
        return False
    
    def check_stop_loss_profit(self, current_price):
        """
        检查是否触发止损止盈
        """
        if self.current_position == 0:
            return None
        
        change = (current_price - self.current_price) / self.current_price
        
        if change <= self.stop_loss:
            return 'STOP_LOSS'
        elif change >= self.take_profit:
            return 'TAKE_PROFIT'
        
        return None
    
    def check_max_hold_days(self):
        """检查是否超过最大持仓天数"""
        return self.hold_days >= self.max_hold_days
    
    def increment_hold_days(self):
        """增加持仓天数"""
        self.hold_days += 1
    
    def get_current_value(self, current_price):
        """获取当前总市值"""
        return self.current_cash + self.current_position * current_price
    
    def get_profit_rate(self, current_price):
        """获取当前收益率"""
        if self.current_position == 0:
            return (self.current_cash - self.initial_capital) / self.initial_capital
        
        total_value = self.get_current_value(current_price)
        return (total_value - self.initial_capital) / self.initial_capital
    
    def get_position_summary(self):
        """获取持仓摘要"""
        return {
            'cash': self.current_cash,
            'position': self.current_position,
            'cost_price': self.current_price,
            'hold_days': self.hold_days,
            'buy_date': self.buy_date,
            'total_trades': len(self.trades)
        }
    
    def reset(self):
        """重置仓位管理器"""
        self.current_cash = self.initial_capital
        self.current_position = 0
        self.current_price = 0
        self.hold_days = 0
        self.buy_date = None
        self.trades = []
        self.equity_curve = []
    
    def get_performance_summary(self):
        """获取绩效摘要"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'total_loss': 0,
                'profit_loss_ratio': 0
            }
        
        # 计算盈亏统计
        sell_trades = [t for t in self.trades if t['action'] in ['SELL', 'REDUCE', 'STOP_LOSS', 'TAKE_PROFIT']]
        
        winning = [t for t in sell_trades if t.get('profit', 0) > 0]
        losing = [t for t in sell_trades if t.get('profit', 0) < 0]
        
        total_profit = sum(t.get('profit', 0) for t in winning)
        total_loss = abs(sum(t.get('profit', 0) for t in losing))
        
        return {
            'total_trades': len(sell_trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': len(winning) / len(sell_trades) if sell_trades else 0,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_loss_ratio': total_profit / total_loss if total_loss > 0 else float('inf')
        }


# 全局实例
position_manager = PositionManager()


if __name__ == '__main__':
    # 测试
    pm = PositionManager(100000)
    
    print("[TEST] Position Manager Test")
    print(f"Initial: Cash={pm.current_cash}, Position={pm.current_position}")
    
    # 买入测试
    pm.update_position('BUY', 10.0, 10000, datetime.now())
    print(f"After BUY: Cash={pm.current_cash}, Position={pm.current_position}, Cost={pm.current_price}")
    
    # 检查止损止盈
    result = pm.check_stop_loss_profit(10.8)
    print(f"Stop check at 10.8: {result}")
    
    result = pm.check_stop_loss_profit(9.4)
    print(f"Stop check at 9.4: {result}")
    
    # 卖出测试
    pm.update_position('SELL', 10.5, 10000, datetime.now())
    print(f"After SELL: Cash={pm.current_cash}, Position={pm.current_position}")
    
    summary = pm.get_performance_summary()
    print(f"Performance: {summary}")
