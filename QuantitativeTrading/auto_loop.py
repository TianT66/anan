# -*- coding: utf-8 -*-
"""
自动化交易闭环系统
记录 -> 分析 -> 改进 -> 进化
全流程自动化
"""

import sys
import json
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data'
TRADE_FILE = os.path.join(DATA_DIR, 'trades.json')
ANALYSIS_FILE = os.path.join(DATA_DIR, 'analysis.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'strategy_settings.json')

os.makedirs(DATA_DIR, exist_ok=True)


class AutoTradingLoop:
    """自动化交易闭环"""
    
    def __init__(self):
        self.trades = self.load_data(TRADE_FILE, {'trades': [], 'stats': {}})
        self.analysis = self.load_data(ANALYSIS_FILE, {'learnings': [], 'improvements': []})
        self.settings = self.load_data(SETTINGS_FILE, self.default_settings())
    
    def load_data(self, filepath, default):
        """加载数据"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def save_data(self, filepath, data):
        """保存数据"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def default_settings(self):
        """默认策略设置"""
        return {
            'weights': {
                'technical': 0.25,
                'fund_flow': 0.15,
                'sentiment': 0.10,
                'fundamental': 0.20,
                'market_timing': 0.20,
                'policy': 0.10
            },
            'strategy_params': {
                'BEAR': {
                    'max_position': 0.30,
                    'stop_loss': 0.08,
                    'take_profit': 0.15,
                    'max_pe': 20,
                    'min_dividend': 3
                },
                'BULL': {
                    'max_position': 0.80,
                    'stop_loss': 0.10,
                    'take_profit': 0.25
                },
                'OSCILLATION': {
                    'max_position': 0.50,
                    'stop_loss': 0.06,
                    'take_profit': 0.12
                }
            },
            'thresholds': {
                'strong_buy': 70,
                'buy': 60,
                'sell': 40,
                'strong_sell': 30
            }
        }
    
    def add_trade(self, code, name, action, price, quantity, reason, strategy):
        """添加交易记录"""
        trade = {
            'id': len(self.trades['trades']) + 1,
            'code': code,
            'name': name,
            'action': action,
            'price': price,
            'quantity': quantity,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'reason': reason,
            'strategy': strategy,
            'result': 'pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.trades['trades'].append(trade)
        self.save_data(TRADE_FILE, self.trades)
        return trade['id']
    
    def close_trade(self, trade_id, sell_price, sell_date, notes=''):
        """平仓并自动分析"""
        for trade in self.trades['trades']:
            if trade['id'] == trade_id and trade.get('result') == 'pending':
                trade['sell_price'] = sell_price
                trade['sell_date'] = sell_date
                
                profit_pct = (sell_price - trade['price']) / trade['price'] * 100
                trade['profit_pct'] = profit_pct
                trade['result'] = 'profit' if profit_pct > 0 else 'loss'
                trade['holding_days'] = (datetime.strptime(sell_date, '%Y-%m-%d') - 
                                        datetime.strptime(trade['date'], '%Y-%m-%d')).days
                trade['notes'] = notes
                trade['closed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.save_data(TRADE_FILE, self.trades)
                
                # 自动分析
                self.analyze_trade(trade)
                
                return trade
        return None
    
    def analyze_trade(self, trade):
        """自动分析单笔交易"""
        profit = trade['profit_pct']
        reason = trade.get('reason', '')
        strategy = trade.get('strategy', '')
        
        analysis = {
            'trade_id': trade['id'],
            'code': trade['code'],
            'result': trade['result'],
            'profit': profit,
            'analysis': '',
            'improvement': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 分析盈利原因
        if profit > 0:
            if '低估' in reason or '低PE' in reason:
                analysis['analysis'] = '低估策略有效，PE<15选股正确'
            elif '主力净流入' in reason or '资金' in reason:
                analysis['analysis'] = '资金面分析有效，跟随主力资金正确'
            elif '趋势' in reason or '突破' in reason:
                analysis['analysis'] = '趋势策略有效，突破买入正确'
            elif '高股息' in reason or '股息' in reason:
                analysis['analysis'] = '高股息策略有效'
            else:
                analysis['analysis'] = f'策略{strategy}产生盈利'
            
            analysis['improvement'] = '继续沿用当前策略和选股标准'
        
        # 分析亏损原因
        else:
            if trade['holding_days'] < 7:
                analysis['analysis'] = '持有期太短（<7天），频繁交易导致亏损'
                analysis['improvement'] = '建议持有至少15天，避免频繁交易'
            elif abs(profit) > 15:
                analysis['analysis'] = '亏损超过15%，止损不严格'
                analysis['improvement'] = '必须严格执行8%止损线'
            elif '追高' in reason:
                analysis['analysis'] = '追高买入是亏损主因'
                analysis['improvement'] = '只做低吸，不追高'
            elif '周期' in reason:
                analysis['analysis'] = '周期股波动大，不适合短线'
                analysis['improvement'] = '周期股延长持有期或减少配置'
            else:
                analysis['analysis'] = f'策略{strategy}产生亏损，需复盘'
                analysis['improvement'] = '检查选股标准和买入时机'
            
            # 自动调整策略参数
            self.auto_adjust_strategy(analysis)
        
        self.analysis['learnings'].append(analysis)
        self.save_data(ANALYSIS_FILE, self.analysis)
        
        return analysis
    
    def auto_adjust_strategy(self, analysis):
        """根据亏损自动调整策略"""
        improvements = []
        
        # 记录改进
        if '持有期太短' in analysis['analysis']:
            self.settings['strategy_params']['BEAR']['min_holding_days'] = 15
            improvements.append('已调整：熊市最小持有期改为15天')
        
        if '止损' in analysis['analysis']:
            self.settings['strategy_params']['BEAR']['stop_loss'] = 0.05
            improvements.append('已调整：止损线加严到5%')
        
        if '追高' in analysis['analysis']:
            self.settings['filters'] = self.settings.get('filters', [])
            self.settings['filters'].append('禁止追高买入')
            improvements.append('已调整：增加禁止追高过滤器')
        
        if improvements:
            self.analysis['improvements'].extend(improvements)
            self.save_data(SETTINGS_FILE, self.settings)
    
    def get_stats(self):
        """获取统计"""
        trades = self.trades['trades']
        closed = [t for t in trades if t.get('result') in ['profit', 'loss']]
        
        if not closed:
            return {'total': 0, 'wins': 0, 'losses': 0, 'win_rate': 0}
        
        wins = [t for t in closed if t.get('profit_pct', 0) > 0]
        losses = [t for t in closed if t.get('profit_pct', 0) <= 0]
        
        return {
            'total': len(trades),
            'closed': len(closed),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(closed) * 100 if closed else 0,
            'avg_profit': sum(t['profit_pct'] for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t['profit_pct'] for t in losses) / len(losses) if losses else 0,
            'total_return': sum(t.get('profit_pct', 0) for t in closed)
        }
    
    def get_recommendations(self):
        """获取当前策略推荐"""
        return self.settings


# 便捷函数
def record_trade(code, name, action, price, quantity, reason, strategy):
    """记录交易"""
    loop = AutoTradingLoop()
    return loop.add_trade(code, name, action, price, quantity, reason, strategy)


def close_trade_with_analysis(trade_id, sell_price, notes=''):
    """平仓并自动分析"""
    loop = AutoTradingLoop()
    trade = loop.close_trade(trade_id, sell_price, datetime.now().strftime('%Y-%m-%d'), notes)
    if trade:
        print(f"\n自动分析结果:")
        print(f"  盈亏: {trade['profit_pct']:.2f}%")
        loop2 = AutoTradingLoop()
        for learning in reversed(loop2.analysis['learnings']):
            if learning['trade_id'] == trade_id:
                print(f"  分析: {learning['analysis']}")
                print(f"  改进: {learning['improvement']}")
                break
    return trade


def show_stats():
    """显示统计"""
    loop = AutoTradingLoop()
    stats = loop.get_stats()
    
    print("=" * 50)
    print("  交易统计")
    print("=" * 50)
    print(f"  总交易: {stats['total']}")
    print(f"  已平仓: {stats['closed']}")
    print(f"  盈利: {stats['wins']}")
    print(f"  亏损: {stats['losses']}")
    print(f"  胜率: {stats['win_rate']:.1f}%")
    print(f"  平均盈利: {stats['avg_profit']:.2f}%")
    print(f"  平均亏损: {stats['avg_loss']:.2f}%")
    print(f"  总收益: {stats['total_return']:.2f}%")
    print("=" * 50)


# 使用示例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'stats':
            show_stats()
        
        elif cmd == 'add' and len(sys.argv) >= 8:
            # 添加交易: python auto_loop.py add 代码 名称 买入/卖出 价格 数量 理由 策略
            record_trade(sys.argv[2], sys.argv[3], sys.argv[4], 
                       float(sys.argv[5]), int(sys.argv[6]), 
                       sys.argv[7], sys.argv[8])
        
        elif cmd == 'close' and len(sys.argv) >= 4:
            # 平仓: python auto_loop.py close 交易ID 卖出价
            close_trade_with_analysis(int(sys.argv[2]), float(sys.argv[3]))
        
        else:
            print("用法:")
            print("  python auto_loop.py stats              # 查看统计")
            print("  python auto_loop.py add 代码 名称 买入 100 10.5 理由 策略")
            print("  python auto_loop.py close 交易ID 卖出价")
    else:
        show_stats()
