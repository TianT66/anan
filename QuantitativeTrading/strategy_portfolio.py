# -*- coding: utf-8 -*-
"""
P2改进：策略组合优化
多策略组合，自适应切换，降低波动提升收益
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')


class StrategyPortfolio:
    """策略组合管理器"""
    
    def __init__(self):
        self.strategies = {}
        self.current_strategy = None
        self.performance_history = []
    
    def add_strategy(self, name, strategy_func, params=None):
        """添加策略"""
        self.strategies[name] = {
            'func': strategy_func,
            'params': params or {},
            'stats': {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'total_return': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0
            }
        }
    
    def update_stats(self, name, trade_result):
        """更新策略表现"""
        if name not in self.strategies:
            return
        
        stats = self.strategies[name]['stats']
        stats['total_trades'] += 1
        
        if trade_result['profit'] > 0:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        stats['total_return'] += trade_result['profit']
        stats['win_rate'] = stats['wins'] / stats['total_trades'] * 100
        
        if stats['wins'] > 0:
            stats['avg_profit'] = sum([t['profit'] for t in self.performance_history 
                                       if t['strategy'] == name and t['profit'] > 0]) / stats['wins']
        
        if stats['losses'] > 0:
            stats['avg_loss'] = sum([t['profit'] for t in self.performance_history 
                                    if t['strategy'] == name and t['profit'] < 0]) / stats['losses']
    
    def get_best_strategy(self):
        """获取当前最优策略"""
        if not self.strategies:
            return None
        
        # 综合评分：胜率40% + 盈亏比40% + 收益率20%
        best = None
        best_score = -999
        
        for name, data in self.strategies.items():
            stats = data['stats']
            if stats['total_trades'] < 5:
                continue
            
            win_rate = stats['win_rate']
            avg_profit = stats['avg_profit'] or 0
            avg_loss = abs(stats['avg_loss']) or 1
            profit_factor = avg_profit / avg_loss if avg_loss > 0 else 0
            
            # 综合评分
            score = win_rate * 0.4 + profit_factor * 40
            
            if score > best_score:
                best_score = score
                best = name
        
        return best
    
    def select_strategy(self, market_status):
        """根据市场状态选择策略"""
        status = market_status.get('status', 'OSCILLATION')
        
        if status == 'BULL':
            return 'momentum'  # 牛市趋势策略
        elif status == 'BEAR':
            return 'defensive'  # 熊市防御策略
        else:
            return 'oscillation'  # 震荡市


# 预定义策略
class StrategyLibrary:
    """策略库"""
    
    @staticmethod
    def momentum_strategy(stock_data, market_status):
        """
        趋势动量策略 - 牛市使用
        特点：高仓位，高弹性，跟随趋势
        """
        return {
            'name': '趋势动量策略',
            'position': min(0.9, market_status.get('position', 0.8)),
            'stop_loss': 0.08,
            'take_profit': 0.25,
            'holding_period': 30,  # 天
            'selection': {
                'min_volume': 10,  # 日均成交额亿
                'min_trend': 'MA20之上',
                'preferred': ['科技', '新能源', '券商']
            },
            'filters': ['剔除ST', '剔除亏损', '剔除高估值PE>50']
        }
    
    @staticmethod
    def defensive_strategy(stock_data, market_status):
        """
        防御策略 - 熊市使用
        特点：低仓位，高股息，稳定收益
        """
        return {
            'name': '防御策略',
            'position': max(0.2, market_status.get('position', 0.3)),
            'stop_loss': 0.05,
            'take_profit': 0.15,
            'holding_period': 90,
            'selection': {
                'min_pe': 0,
                'max_pe': 20,
                'min_dividend': 3,  # 股息率>3%
                'preferred': ['银行', '电力', '公用事业', '消费']
            },
            'filters': ['高股息优先', 'ROE>10%', '稳定盈利']
        }
    
    @staticmethod
    def oscillation_strategy(stock_data, market_status):
        """
        震荡策略 - 震荡市使用
        特点：中等仓位，高抛低吸，波段操作
        """
        return {
            'name': '震荡策略',
            'position': max(0.4, market_status.get('position', 0.5)),
            'stop_loss': 0.06,
            'take_profit': 0.12,
            'holding_period': 15,
            'selection': {
                'rsi_range': (30, 70),
                'preferred': ['医药', '消费', '科技']
            },
            'filters': ['RSI<40买入', 'RSI>60卖出', '回落止盈']
        }
    
    @staticmethod
    def value_strategy(stock_data, market_status):
        """
        价值策略 - 长期投资
        特点：低估值，高ROE，长期持有
        """
        return {
            'name': '价值策略',
            'position': 0.6,
            'stop_loss': 0.15,
            'take_profit': 0.30,
            'holding_period': 180,
            'selection': {
                'max_pe': 25,
                'min_roe': 15,
                'min_dividend': 2,
                'preferred': ['各行业龙头']
            },
            'filters': ['PE<25', 'ROE>15%', '行业龙头']
        }
    
    @staticmethod
    def growth_strategy(stock_data, market_status):
        """
        成长策略 - 高增长公司
        特点：高增速，高弹性，高风险
        """
        return {
            'name': '成长策略',
            'position': 0.4,
            'stop_loss': 0.10,
            'take_profit': 0.20,
            'holding_period': 60,
            'selection': {
                'min_revenue_growth': 30,
                'min_profit_growth': 20,
                'preferred': ['AI', '半导体', '新能源', '生物医药']
            },
            'filters': ['营收增速>30%', '研发投入>5%', '止损必须执行']
        }


class AdaptivePortfolio:
    """自适应组合"""
    
    def __init__(self):
        self.library = StrategyLibrary()
        self.current_regime = 'OSCILLATION'  # 当前市场状态
        self.regime_history = []
    
    def detect_regime(self, market_data):
        """
        识别市场状态
        
        Returns:
            str: BULL / BEAR / OSCILLATION
        """
        # 简化判断
        # 实际应接入真实数据
        
        if market_data.get('trend_score', 0) > 3:
            return 'BULL'
        elif market_data.get('trend_score', 0) < -3:
            return 'BEAR'
        else:
            return 'OSCILLATION'
    
    def get_strategy_config(self, market_status):
        """获取当前市场状态下的策略配置"""
        regime = self.detect_regime(market_status)
        self.current_regime = regime
        self.regime_history.append({
            'regime': regime,
            'timestamp': market_data.get('timestamp', 'now')
        })
        
        # 根据市场状态选择策略
        if regime == 'BULL':
            return self.library.momentum_strategy(market_data, {'position': 0.8})
        elif regime == 'BEAR':
            return self.library.defensive_strategy(market_data, {'position': 0.3})
        else:
            return self.library.oscillation_strategy(market_data, {'position': 0.5})
    
    def optimize_weights(self, strategies_performance):
        """
        优化策略权重
        
        根据历史表现动态调整权重
        """
        total_return = sum(s['return'] for s in strategies_performance.values())
        
        weights = {}
        for name, data in strategies_performance.items():
            # 基于风险调整后的收益分配权重
            sharpe = data['return'] / max(data['max_drawdown'], 1)
            weights[name] = max(0.1, sharpe / total_return if total_return > 0 else 0.2)
        
        # 归一化
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}


def print_portfolio_guide():
    """打印组合指南"""
    
    print("=" * 70)
    print("  策略组合优化系统 v5.2")
    print("  P2改进: 多策略组合 + 自适应切换")
    print("=" * 70)
    
    print("""
【策略组合说明】

┌─────────────────────────────────────────────────────────────────┐
│  市场状态     │  推荐策略      │  仓位   │  持有期 │  特点         │
├─────────────────────────────────────────────────────────────────┤
│  牛市        │  趋势动量策略  │  80-90% │  30天  │ 高弹性       │
│  熊市        │  防御策略      │  20-30% │  90天  │ 高股息       │
│  震荡市      │  震荡策略      │  40-60% │  15天  │ 高抛低吸     │
└─────────────────────────────────────────────────────────────────┘

【策略选择逻辑】

1. 识别当前市场状态（牛市/熊市/震荡）
2. 选择对应策略
3. 按策略规则选股
4. 严格执行止损止盈
5. 定期评估策略有效性

【权重优化】

- 最近1个月表现好的策略权重增加
- 连续3个月跑输基准的策略暂停
- 每季度重新平衡权重

【策略失效检测】

- 连续3个月胜率<40% → 预警
- 连续6个月跑输基准 → 暂停
- 策略有效条件：胜率>50% 且 盈亏比>1.5

【当前建议】

基于当前市场状态（熊市 + 恐慌情绪）:
- 推荐策略: 防御策略
- 建议仓位: 30%
- 持仓周期: 90天
- 选股标准: 高股息(>3%) + 低PE(<15) + 行业龙头

具体配置:
- 银行: 10% (高股息，稳定)
- 电力: 10% (稳定现金流)
- 消费: 10% (防御性好)
- 现金: 70% (等待机会)

    """)
    
    print("=" * 70)


if __name__ == "__main__":
    print_portfolio_guide()
