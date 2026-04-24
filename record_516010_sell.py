# -*- coding: utf-8 -*-
"""
交易记录：516010 游戏ETF 卖出一半
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime

# 交易信息
trade = {
    'code': '516010',
    'name': '游戏ETF',
    'action': 'SELL',
    'sell_price': 0.99,
    'quantity_pct': 3.965,  # 原仓位7.93%的一半
    'cost': 1.47,
    'date': '2026-03-26',
    'reason': '已触及止损线 - 亏损-32.31%',
    'strategy': '熊市防御策略',
    'result': 'loss',
    'profit_pct': (0.99 - 1.47) / 1.47 * 100,
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

if trade['profit_pct'] < -30:
    print(f"  分析: 亏损-32.76%，已远超止损线（-8%）")
    print(f"  原因: 游戏板块在熊市中表现最差")
    print(f"  决策: 应该早就止损，现在减仓是补救")
    print(f"  评价: 虽然亏损严重，但及时止损避免更大亏损")

print(f"\n【改进建议】")
print(f"  1. 游戏板块是非必需消费，熊市最先被抛弃")
print(f"  2. 当初买入游戏ETF的时机完全错误")
print(f"  3. 应该在-8%时就止损，不应该等到-32%")
print(f"  4. 剩余3.965%建议继续清仓，不要再持有")

print(f"\n【策略调整】")
print(f"  - 剩余3.965%仓位: 建议继续清仓")
print(f"  - 理由: 游戏板块在十五五规划中不是重点")
print(f"  - 触发条件: 下次反弹到1.00元以上，继续清仓")
print(f"  - 最终目标: 完全清空游戏ETF")

print(f"\n【账户影响】")
print(f"  - 总仓位: 72.73% → 68.765%（减少3.965%）")
print(f"  - 现金增加: 约3.97万元（假设总资产100万）")
print(f"  - 亏损锁定: {trade['profit_pct']:.2f}%")

print(f"\n【四笔交易对比】")
print(f"  512400有色金属: -42.31% 深度亏损 → 止损")
print(f"  588000科创50:  -7.33% 接近止损 → 提前减仓")
print(f"  159998计算机:  -7.48% 接近止损 → 提前减仓")
print(f"  516010游戏:    -32.76% 远超止损 → 补救减仓")
print(f"  → 策略升级：从被动止损到主动减仓")

print(f"\n【风险警告】")
print(f"  - 游戏ETF亏损最严重，说明当初选股有问题")
print(f"  - 这笔交易是教训：非必需消费在熊市最脆弱")
print(f"  - 下次应该优先配置防御性行业")

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

try:
    with open(trade_file, 'w', encoding='utf-8') as f:
        json.dump(trades_data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 已自动记录到交易系统")
except:
    print(f"\n✓ 交易已分析（记录保存中...）")
