# -*- coding: utf-8 -*-
"""
交易记录系统 - 持续进化量化系统
记录每笔交易，分析盈亏原因，持续优化策略
"""

import sys
import json
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

TRADE_FILE = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\trades.json'
ANALYSIS_FILE = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\trade_analysis.json'


class TradeRecorder:
    """交易记录器"""
    
    def __init__(self):
        self.trade_file = TRADE_FILE
        self.analysis_file = ANALYSIS_FILE
        os.makedirs(os.path.dirname(self.trade_file), exist_ok=True)
        self.trades = self.load_trades()
    
    def load_trades(self):
        """加载交易记录"""
        if os.path.exists(self.trade_file):
            try:
                with open(self.trade_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'trades': [], 'stats': {}}
        return {'trades': [], 'stats': {}}
    
    def save_trades(self):
        """保存交易记录"""
        with open(self.trade_file, 'w', encoding='utf-8') as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)
    
    def add_trade(self, trade):
        """
        添加交易记录
        
        trade格式:
        {
            'code': '600519',
            'name': '贵州茅台',
            'action': 'BUY' / 'SELL',
            'price': 1500.00,
            'quantity': 100,
            'date': '2026-03-25',
            'reason': '技术面金叉+低估',
            'strategy': '价值策略',
            'result': 'pending' / 'profit' / 'loss',
            'profit_pct': 0,  # 盈利百分比
            'holding_days': 0,
            'notes': '备注'
        }
        """
        trade['id'] = len(self.trades['trades']) + 1
        trade['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.trades['trades'].append(trade)
        self.save_trades()
        print(f"已记录交易: {trade['name']} {trade['action']} {trade['quantity']}股 @ {trade['price']}")
        return trade['id']
    
    def close_trade(self, trade_id, sell_price, sell_date, result, notes=''):
        """平仓记录"""
        for trade in self.trades['trades']:
            if trade['id'] == trade_id and trade.get('result') == 'pending':
                trade['sell_price'] = sell_price
                trade['sell_date'] = sell_date
                trade['result'] = result
                trade['profit_pct'] = (sell_price - trade['price']) / trade['price'] * 100
                trade['holding_days'] = (datetime.strptime(sell_date, '%Y-%m-%d') - 
                                        datetime.strptime(trade['date'], '%Y-%m-%d')).days
                trade['close_notes'] = notes
                trade['closed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_trades()
                print(f"已平仓: {trade['name']} 卖出价 {sell_price}, 盈亏 {trade['profit_pct']:.2f}%")
                return trade
        return None
    
    def get_stats(self):
        """获取统计数据"""
        trades = self.trades['trades']
        closed = [t for t in trades if t.get('result') in ['profit', 'loss']]
        pending = [t for t in trades if t.get('result') == 'pending']
        
        if not closed:
            return {
                'total_trades': len(trades),
                'closed_trades': 0,
                'pending_trades': len(pending),
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        wins = [t for t in closed if t['profit_pct'] > 0]
        losses = [t for t in closed if t['profit_pct'] <= 0]
        
        total_profit = sum(t['profit_pct'] for t in wins)
        total_loss = abs(sum(t['profit_pct'] for t in losses))
        
        stats = {
            'total_trades': len(trades),
            'closed_trades': len(closed),
            'pending_trades': len(pending),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(closed) * 100 if closed else 0,
            'avg_profit': sum(t['profit_pct'] for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t['profit_pct'] for t in losses) / len(losses) if losses else 0,
            'profit_factor': total_profit / total_loss if total_loss > 0 else 0,
            'total_return': sum(t['profit_pct'] for t in closed),
            'best_trade': max((t['profit_pct'] for t in closed), default=0),
            'worst_trade': min((t['profit_pct'] for t in closed), default=0),
        }
        
        self.trades['stats'] = stats
        self.save_trades()
        return stats
    
    def analyze_by_strategy(self):
        """按策略分析"""
        trades = [t for t in self.trades['trades'] if t.get('result') in ['profit', 'loss']]
        strategy_stats = {}
        
        for t in trades:
            strategy = t.get('strategy', '未知')
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'wins': 0, 'losses': 0, 'total': 0, 'profits': [], 'losses_list': []}
            
            strategy_stats[strategy]['total'] += 1
            if t['profit_pct'] > 0:
                strategy_stats[strategy]['wins'] += 1
                strategy_stats[strategy]['profits'].append(t['profit_pct'])
            else:
                strategy_stats[strategy]['losses'] += 1
                strategy_stats[strategy]['losses_list'].append(t['profit_pct'])
        
        # 计算每个策略的胜率和平均盈亏
        for s, data in strategy_stats.items():
            data['win_rate'] = data['wins'] / data['total'] * 100 if data['total'] > 0 else 0
            data['avg_profit'] = sum(data['profits']) / len(data['profits']) if data['profits'] else 0
            data['avg_loss'] = sum(data['losses_list']) / len(data['losses_list']) if data['losses_list'] else 0
        
        return strategy_stats
    
    def analyze_by_reason(self):
        """按买入理由分析"""
        trades = [t for t in self.trades['trades'] if t.get('result') in ['profit', 'loss']]
        reason_stats = {}
        
        for t in trades:
            reason = t.get('reason', '未知')[:20]  # 取前20字符作为分类
            if reason not in reason_stats:
                reason_stats[reason] = {'wins': 0, 'losses': 0, 'total': 0}
            
            reason_stats[reason]['total'] += 1
            if t['profit_pct'] > 0:
                reason_stats[reason]['wins'] += 1
            else:
                reason_stats[reason]['losses'] += 1
        
        return reason_stats
    
    def print_report(self):
        """打印交易报告"""
        stats = self.get_stats()
        
        print("=" * 70)
        print("  交易记录统计报告")
        print("=" * 70)
        
        print(f"\n【总体统计】")
        print(f"  总交易次数: {stats['total_trades']}")
        print(f"  已平仓: {stats['closed_trades']}")
        print(f"  持仓中: {stats['pending_trades']}")
        
        if stats['closed_trades'] > 0:
            print(f"\n【盈亏统计】")
            print(f"  胜率: {stats['win_rate']:.1f}%")
            print(f"  盈利次数: {stats['wins']}")
            print(f"  亏损次数: {stats['losses']}")
            print(f"  平均盈利: {stats['avg_profit']:.2f}%")
            print(f"  平均亏损: {stats['avg_loss']:.2f}%")
            print(f"  盈亏比: {stats['profit_factor']:.2f}")
            print(f"  总收益: {stats['total_return']:.2f}%")
            print(f"  最佳交易: +{stats['best_trade']:.2f}%")
            print(f"  最差交易: {stats['worst_trade']:.2f}%")
        
        # 按策略分析
        strategy_stats = self.analyze_by_strategy()
        if strategy_stats:
            print(f"\n【按策略分析】")
            print(f"  {'策略':<15} {'次数':<6} {'胜率':<8} {'平均盈利':<10} {'平均亏损':<10}")
            print(f"  {'-'*55}")
            for s, data in sorted(strategy_stats.items(), key=lambda x: -x[1]['win_rate']):
                print(f"  {s:<15} {data['total']:<6} {data['win_rate']:>5.1f}% {data['avg_profit']:>8.2f}% {data['avg_loss']:>9.2f}%")
        
        # 按理由分析
        reason_stats = self.analyze_by_reason()
        if reason_stats:
            print(f"\n【按买入理由分析】")
            print(f"  {'理由':<20} {'次数':<6} {'胜率':<8}")
            print(f"  {'-'*40}")
            for r, data in sorted(reason_stats.items(), key=lambda x: -x[1]['total'])[:10]:
                win_rate = data['wins'] / data['total'] * 100 if data['total'] > 0 else 0
                print(f"  {r:<20} {data['total']:<6} {win_rate:>5.1f}%")
        
        print("\n" + "=" * 70)
        
        # 进化建议
        print("\n【进化建议】")
        
        if stats['win_rate'] < 50:
            print("  ⚠️ 胜率低于50%，需要优化选股逻辑")
            best_strategy = max(strategy_stats.items(), key=lambda x: x[1]['win_rate'])[0] if strategy_stats else None
            if best_strategy:
                print(f"  → 多使用'{best_strategy}'策略")
        
        if stats['profit_factor'] < 1.5:
            print("  ⚠️ 盈亏比较低，需要优化止损纪律")
            print("  → 建议：亏损超过-8%必须止损")
        
        if stats['avg_loss'] < -15:
            print("  ⚠️ 平均亏损过大，止损不够严格")
            print("  → 建议：单笔亏损超过-10%立即止损")
        
        best_reason = max(reason_stats.items(), key=lambda x: x[1]['wins']/x[1]['total'] if x[1]['total'] > 0 else 0)[0] if reason_stats else None
        if best_reason:
            print(f"  → 胜率最高的买入理由: {best_reason}")
        
        print("\n" + "=" * 70)


def quick_add_trade(code, name, action, price, quantity, reason, strategy):
    """快速添加交易"""
    recorder = TradeRecorder()
    trade = {
        'code': code,
        'name': name,
        'action': action,
        'price': price,
        'quantity': quantity,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'reason': reason,
        'strategy': strategy,
        'result': 'pending'
    }
    recorder.add_trade(trade)


def quick_close_trade(trade_id, sell_price, result, notes=''):
    """快速平仓"""
    recorder = TradeRecorder()
    recorder.close_trade(trade_id, sell_price, datetime.now().strftime('%Y-%m-%d'), result, notes)


# 使用示例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'report':
        # 打印报告
        recorder = TradeRecorder()
        recorder.print_report()
    elif len(sys.argv) > 1 and sys.argv[1] == 'add':
        # 添加交易
        # python trade_recorder.py add 代码 名称 买入/卖出 价格 数量 理由 策略
        quick_add_trade(sys.argv[2], sys.argv[3], sys.argv[4], 
                      float(sys.argv[5]), int(sys.argv[6]), sys.argv[7], sys.argv[8])
    else:
        # 默认显示帮助
        print("""
交易记录系统使用说明:

1. 添加交易记录:
   python trade_recorder.py add 代码 名称 买入/卖出 价格 数量 理由 策略
   
   示例:
   python trade_recorder.py add 600519 贵州茅台 买入 1500.00 100 低估+消费龙头 价值策略

2. 查看统计报告:
   python trade_recoder.py report
        """)
