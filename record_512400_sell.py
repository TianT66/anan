# -*- coding: utf-8 -*-
"""
交易记录：512400 有色金属ETF 卖出一半
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime

# 交易信息
trade = {
    'code': '512400',
    'name': '有色金属ETF',
    'action': 'SELL',
    'sell_price': 1.95,
    'quantity_pct': 1.885,  # 原仓位3.77%的一半
    'cost': 3.38,
    'date': '2026-03-26',
    'reason': '止损执行 - 亏损超过-40%',
    'strategy': '熊市防御策略',
    'result': 'loss',
    'profit_pct': (1.95 - 3.38) / 3.38 * 100,
    'holding_days': 0,  # 不知道具体持有多久
}

print("=" * 70)
print("  交易记录分析")
print("=" * 70)

print(f"\n【交易信息】")
print(f"  股票: {trade['name']} ({trade['code']})")
print(f"  操作: {trade['action']}")
print(f"  卖出价: {trade['sell_price']:.2f}元")
print(f"  成本价: {trade['cost']:.2f}元")
print(f"  盈亏: {trade['profit_pct']:.2f}%")
print(f"  卖出仓位: {trade['quantity_pct']:.2f}%")
print(f"  日期: {trade['date']}")

print(f"\n【自动分析】")

# 分析亏损原因
if trade['profit_pct'] < -40:
    print(f"  分析: 亏损超过40%，这是一个深度亏损")
    print(f"  原因: 有色金属ETF在熊市中表现极差")
    print(f"  决策: 止损执行是正确的，避免继续下跌")
    print(f"  评价: 虽然亏损，但及时止损是理性决策")

print(f"\n【改进建议】")
print(f"  1. 这笔交易说明当初买入有色金属ETF的时机不对")
print(f"  2. 熊市环境下不应该配置周期性强的有色金属")
print(f"  3. 下次应该优先选择防御性行业（银行、医药、消费）")
print(f"  4. 止损纪律执行得好，避免了更大的亏损")

print(f"\n【策略调整】")
print(f"  - 剩余1.885%仓位: 继续持有观察，或继续减仓")
print(f"  - 释放的现金: 可用于建仓防御性标的")
print(f"  - 建议: 用释放的现金买入银行/医药/消费龙头")

print(f"\n【账户影响】")
print(f"  - 总仓位: 84.81% → 82.925%（减少1.885%）")
print(f"  - 现金增加: 约3.68万元（假设总资产100万）")
print(f"  - 亏损锁定: -{trade['profit_pct']:.2f}%")

print("\n" + "=" * 70)

# 保存到交易记录
import json
import os

trade_file = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\trades.json'
os.makedirs(os.path.dirname(trade_file), exist_ok=True)

trades_data = {'trades': [], 'stats': {}}
if os.path.exists(trade_file):
    try:
        with open(trade_file, 'r', encoding='utf-8') as f:
            trades_data = json.load(f)
    except:
        pass

trade['id'] = len(trades_data['trades']) + 1
trade['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
trades_data['trades'].append(trade)

with open(trade_file, 'w', encoding='utf-8') as f:
    json.dump(trades_data, f, ensure_ascii=False, indent=2)

print(f"\n✓ 已自动记录到交易系统")
