# -*- coding: utf-8 -*-
"""
回测引擎 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital=100000, commission_rate=0.0003, 
                 stamp_duty=0.001, slippage=0.001):
        """
        初始化回测引擎
        :param initial_capital: 初始资金
        :param commission_rate: 手续费率
        :param stamp_duty: 印花税率
        :param slippage: 滑点
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.stamp_duty = stamp_duty
        self.slippage = slippage
        
        # 回测状态
        self.reset()
    
    def reset(self):
        """重置回测状态"""
        self.current_cash = self.initial_capital
        self.current_position = 0
        self.current_price = 0
        self.hold_days = 0
        self.buy_date = None
        
        self.trades = []
        self.equity_curve = []
        self.daily_positions = []
        
        self.total_commission = 0
        self.total_stamp_duty = 0
        
    def run_backtest(self, df, stock_code, strategy_func=None, stop_loss=-0.05, 
                     take_profit=0.08, max_hold_days=5):
        """
        运行回测
        :param df: 历史数据
        :param stock_code: 股票代码
        :param strategy_func: 策略函数，接收(df, idx)返回评分
        :param stop_loss: 止损比例
        :param take_profit: 止盈比例
        :param max_hold_days: 最大持仓天数
        :return: 回测结果
        """
        self.reset()
        
        if df is None or len(df) < 30:
            return self._empty_result(stock_code, "数据不足")
        
        # 确保数据有必要的列
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume', 'pct_change']
        for col in required_cols:
            if col not in df.columns:
                if col == 'pct_change':
                    df['pct_change'] = df['close'].pct_change() * 100
        
        results = {
            'stock_code': stock_code,
            'trades': [],
            'equity_curve': [],
            'metrics': {}
        }
        
        # 遍历每一天
        for idx in range(20, len(df)):
            current_date = df['date'].iloc[idx]
            current_price = df['close'].iloc[idx]
            
            # 获取当前持仓成本
            if self.current_position > 0 and self.current_price > 0:
                profit_rate = (current_price - self.current_price) / self.current_price
                
                # 止损检查
                if profit_rate <= stop_loss:
                    self._sell(current_price, df.iloc[idx], 'STOP_LOSS')
                    continue
                
                # 止盈检查
                if profit_rate >= take_profit:
                    self._sell(current_price, df.iloc[idx], 'TAKE_PROFIT')
                    continue
                
                # 最大持仓天数检查
                if self.hold_days >= max_hold_days:
                    self._sell(current_price, df.iloc[idx], 'MAX_HOLD')
                    continue
            
            # 策略评分
            if strategy_func:
                score = strategy_func(df.iloc[:idx+1])
            else:
                score = self._default_strategy(df.iloc[:idx+1])
            
            # 交易决策
            if self.current_position == 0 and score >= 65:
                # 买入
                self._buy(df.iloc[idx], score)
            elif self.current_position > 0:
                self.hold_days += 1
            
            # 记录每日权益
            total_value = self.current_cash + self.current_position * current_price
            self.equity_curve.append({
                'date': current_date,
                'cash': self.current_cash,
                'position_value': self.current_position * current_price,
                'total_value': total_value,
                'profit_rate': (total_value - self.initial_capital) / self.initial_capital
            })
        
        # 最后一天如果还有持仓，卖出
        if self.current_position > 0:
            last_price = df['close'].iloc[-1]
            self._sell(last_price, df.iloc[-1], 'END_SELL')
        
        # 计算指标
        results['trades'] = self.trades
        results['equity_curve'] = self.equity_curve
        results['metrics'] = self._calculate_metrics(df, stock_code)
        
        return results
    
    def _buy(self, row, score):
        """买入"""
        price = row['close'] * (1 + self.slippage)  # 滑点
        max_shares = int(self.current_cash / (price * (1 + self.commission_rate)))
        
        if max_shares <= 0:
            return
        
        # 根据评分确定仓位
        if score >= 75:
            position_ratio = 0.40
        elif score >= 65:
            position_ratio = 0.25
        else:
            position_ratio = 0.15
        
        quantity = int(max_shares * position_ratio / 100) * 100  # 整手
        if quantity <= 0:
            return
        
        cost = price * quantity
        commission = cost * self.commission_rate
        self.total_commission += commission
        
        self.current_cash -= (cost + commission)
        self.current_position = quantity
        self.current_price = price
        self.hold_days = 0
        self.buy_date = row['date']
        
        self.trades.append({
            'date': row['date'],
            'action': 'BUY',
            'price': price,
            'quantity': quantity,
            'cost': cost,
            'commission': commission,
            'score': score,
            'profit': 0
        })
    
    def _sell(self, price, row, reason):
        """卖出"""
        if self.current_position <= 0:
            return
        
        sell_price = price * (1 - self.slippage)
        revenue = sell_price * self.current_position
        commission = revenue * self.commission_rate
        stamp_duty = revenue * self.stamp_duty
        self.total_commission += commission
        self.total_stamp_duty += stamp_duty
        
        net_revenue = revenue - commission - stamp_duty
        cost_basis = self.current_position * self.current_price
        profit = net_revenue - cost_basis
        profit_rate = profit / cost_basis if cost_basis > 0 else 0
        
        self.current_cash += net_revenue
        
        self.trades.append({
            'date': row['date'],
            'action': reason,
            'price': sell_price,
            'quantity': self.current_position,
            'revenue': revenue,
            'commission': commission,
            'stamp_duty': stamp_duty,
            'profit': profit,
            'profit_rate': profit_rate,
            'hold_days': self.hold_days
        })
        
        self.current_position = 0
        self.current_price = 0
        self.hold_days = 0
        self.buy_date = None
    
    def _default_strategy(self, df):
        """默认策略（简化版）"""
        if len(df) < 20:
            return 50
        
        # 简单策略：均线多头 + RSI适中
        score = 50
        
        # MA多头
        ma5 = df['ma5'].iloc[-1] if 'ma5' in df.columns else df['close'].iloc[-5:].mean()
        ma10 = df['ma10'].iloc[-1] if 'ma10' in df.columns else df['close'].iloc[-10:].mean()
        
        if df['close'].iloc[-1] > ma5:
            score += 20
        if ma5 > ma10:
            score += 15
        
        # RSI
        rsi = df['rsi_6'].iloc[-1] if 'rsi_6' in df.columns else 50
        if 30 < rsi < 70:
            score += 10
        
        # 涨幅
        pct_5d = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] * 100 if len(df) >= 6 else 0
        if 2 < pct_5d < 15:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_metrics(self, df, stock_code):
        """计算回测指标"""
        # 买入持有收益率
        bh_profit_rate = (df['close'].iloc[-1] - df['close'].iloc[20]) / df['close'].iloc[20]
        
        # 策略收益率
        final_value = self.current_cash
        strategy_profit_rate = (final_value - self.initial_capital) / self.initial_capital
        
        # 相对收益
        relative_profit = strategy_profit_rate - bh_profit_rate
        
        # 年化收益率
        days = len(df)
        years = days / 244  # A股每年约244个交易日
        annual_return = (1 + strategy_profit_rate) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        equity_values = [e['total_value'] for e in self.equity_curve]
        if equity_values:
            peak = equity_values[0]
            max_drawdown = 0
            for value in equity_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        else:
            max_drawdown = 0
        
        # 胜率
        sell_trades = [t for t in self.trades if t['action'] not in ['BUY']]
        winning_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        win_rate = len(winning_trades) / len(sell_trades) if sell_trades else 0
        
        # 盈亏比
        total_profit = sum(t['profit'] for t in winning_trades)
        total_loss = abs(sum(t['profit'] for t in sell_trades if t.get('profit', 0) < 0))
        profit_loss_ratio = total_profit / total_loss if total_loss > 0 else 0
        
        # 夏普比率（简化）
        if len(self.equity_curve) > 1:
            returns = [e['profit_rate'] for e in self.equity_curve]
            avg_return = np.mean(returns) * 244  # 年化
            std_return = np.std(returns) * np.sqrt(244)
            sharpe_ratio = avg_return / std_return if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 月度盈利统计
        monthly_profits = self._calculate_monthly_profits()
        profitable_months = sum(1 for p in monthly_profits if p > 0)
        total_months = len(monthly_profits)
        monthly_win_rate = profitable_months / total_months if total_months > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'strategy_profit_rate': strategy_profit_rate,
            'bh_profit_rate': bh_profit_rate,
            'relative_profit': relative_profit,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'total_trades': len(sell_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(sell_trades) - len(winning_trades),
            'total_commission': self.total_commission,
            'total_stamp_duty': self.total_stamp_duty,
            'monthly_win_rate': monthly_win_rate,
            'profitable_months': profitable_months,
            'total_months': total_months
        }
    
    def _calculate_monthly_profits(self):
        """计算月度盈亏"""
        monthly_profits = {}
        
        for trade in self.trades:
            if trade['action'] not in ['BUY']:
                date = trade['date']
                month_key = f"{date.year}-{date.month:02d}"
                if month_key not in monthly_profits:
                    monthly_profits[month_key] = 0
                monthly_profits[month_key] += trade.get('profit', 0)
        
        return list(monthly_profits.values())
    
    def _empty_result(self, stock_code, reason):
        """返回空结果"""
        return {
            'stock_code': stock_code,
            'reason': reason,
            'trades': [],
            'equity_curve': [],
            'metrics': {}
        }


# 全局实例
backtest_engine = BacktestEngine()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    
    print("[TEST] Running backtest on 000528...")
    
    df = fetcher.get_daily_data('000528', '20200101', '20241231')
    print(f"Data fetched: {len(df)} rows")
    
    bt = BacktestEngine(100000)
    result = bt.run_backtest(df, '000528')
    
    print(f"\n[OK] Backtest completed")
    print(f"Total trades: {result['metrics'].get('total_trades', 0)}")
    print(f"Win rate: {result['metrics'].get('win_rate', 0)*100:.1f}%")
    print(f"Strategy profit: {result['metrics'].get('strategy_profit_rate', 0)*100:.1f}%")
    print(f"BH profit: {result['metrics'].get('bh_profit_rate', 0)*100:.1f}%")
