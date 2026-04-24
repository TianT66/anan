# -*- coding: utf-8 -*-
"""
持仓分析与操作建议
基于当前熊市环境
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

# 持仓数据
portfolio = [
    {'code': '512400', 'name': '有色金属ETF', 'weight': 0.0377, 'cost': 3.3849, 'type': 'ETF-周期'},
    {'code': '513060', 'name': '恒生医疗ETF', 'weight': 0.0001, 'cost': 55.4776, 'type': 'ETF-医药'},
    {'code': '515980', 'name': '人工智能ETF', 'weight': 0.1207, 'cost': 0.9248, 'type': 'ETF-科技'},
    {'code': '516010', 'name': '游戏ETF', 'weight': 0.0793, 'cost': 1.4688, 'type': 'ETF-传媒'},
    {'code': '562500', 'name': '机器人ETF', 'weight': 0.0812, 'cost': 0.9734, 'type': 'ETF-制造'},
    {'code': '588000', 'name': '科创50ETF', 'weight': 0.1184, 'cost': 1.5016, 'type': 'ETF-科创'},
    {'code': '600309', 'name': '万华化学', 'weight': 0.0818, 'cost': 78.9583, 'type': '化工-周期'},
    {'code': '601899', 'name': '紫金矿业', 'weight': 0.1126, 'cost': 35.4773, 'type': '有色-周期'},
    {'code': '159998', 'name': '计算机ETF', 'weight': 0.0853, 'cost': 1.0728, 'type': 'ETF-科技'},
    {'code': '300760', 'name': '迈瑞医疗', 'weight': 0.1310, 'cost': 178.4800, 'type': '医药-防御'},
]

print("=" * 80)
print("  持仓分析报告")
print("  分析时间: 2026-03-25")
print("  市场环境: 熊市（沪深300趋势评分-4，建议仓位30%）")
print("=" * 80)

# 计算各类别仓位
category_weights = {
    'ETF-周期': 0,
    'ETF-科技': 0,
    'ETF-医药': 0,
    'ETF-传媒': 0,
    'ETF-制造': 0,
    'ETF-科创': 0,
    '化工-周期': 0,
    '有色-周期': 0,
    '医药-防御': 0,
}

for p in portfolio:
    category_weights[p['type']] += p['weight']

total_weight = sum(p['weight'] for p in portfolio)

print(f"\n【当前仓位】")
print(f"  总仓位: {total_weight*100:.2f}%")
print(f"  建议仓位: 30%（熊市）")
print(f"  仓位状态: {'严重超标' if total_weight > 0.5 else '偏高' if total_weight > 0.3 else '正常'}")

print(f"\n【类别分布】")
print(f"  {'类别':<15} {'当前仓位':<12} {'建议仓位':<12} {'操作':<10}")
print(f"  {'-'*50}")

suggestions = {
    'ETF-周期': ('0%', '减仓', '周期股熊市回避'),
    'ETF-科技': ('5%', '大幅减仓', '科技股高波动'),
    'ETF-医药': ('5%', '持有', '医药防御属性'),
    'ETF-传媒': ('0%', '清仓', '传媒非主线'),
    'ETF-制造': ('5%', '减仓', '制造业承压'),
    'ETF-科创': ('5%', '大幅减仓', '科创板高风险'),
    '化工-周期': ('0%', '减仓', '化工周期下行'),
    '有色-周期': ('5%', '减仓', '铜价高位震荡'),
    '医药-防御': ('10%', '持有', '迈瑞医疗优质'),
}

for cat, weight in sorted(category_weights.items(), key=lambda x: -x[1]):
    if weight > 0:
        suggest = suggestions.get(cat, ('0%', '观望', ''))
        print(f"  {cat:<15} {weight*100:>8.2f}%    {suggest[0]:<12} {suggest[1]:<10}")

print(f"\n【个股分析】")
print(f"  {'代码':<10} {'名称':<12} {'仓位':<8} {'成本':<10} {'建议':<12}")
print(f"  {'-'*60}")

stock_suggestions = [
    ('512400', '有色金属ETF', '减仓或清仓', '周期ETF熊市回避'),
    ('513060', '恒生医疗ETF', '清仓', '仓位极低，无意义'),
    ('515980', '人工智能ETF', '减仓50%', 'AI概念波动大，熊市回避'),
    ('516010', '游戏ETF', '清仓', '传媒非主线，业绩不确定'),
    ('562500', '机器人ETF', '减仓50%', '制造业承压'),
    ('588000', '科创50ETF', '减仓50%', '科创板高估值，熊市杀估值'),
    ('600309', '万华化学', '减仓', '化工龙头但周期下行'),
    ('601899', '紫金矿业', '持有观望', '铜金双龙头，但注意止损'),
    ('159998', '计算机ETF', '减仓50%', '科技股高波动'),
    ('300760', '迈瑞医疗', '持有', '医疗器械龙头，防御性好'),
]

for code, name, action, reason in stock_suggestions:
    p = next((x for x in portfolio if x['code'] == code), None)
    if p:
        print(f"  {code:<10} {name:<12} {p['weight']*100:>6.2f}%   {p['cost']:<10.2f} {action:<12}")
        print(f"    -> {reason}")

print(f"\n【紧急操作建议】")
print(f"=" * 80)
print("""
⚠️  当前总仓位67%，严重超标！熊市建议仓位30%

【立即执行】（本周内）
1. 清仓（仓位<1%或亏损严重的）
   - 513060 恒生医疗ETF（仓位仅0.01%，无意义）
   - 516010 游戏ETF（传媒非主线）

2. 减仓50%（高波动品种）
   - 515980 人工智能ETF（12%->6%）
   - 562500 机器人ETF（8%->4%）
   - 588000 科创50ETF（12%->6%）
   - 159998 计算机ETF（9%->4%）

3. 减仓30%（周期股）
   - 512400 有色金属ETF（4%->3%）
   - 600309 万华化学（8%->6%）

【持有观望】
- 601899 紫金矿业：铜价支撑，但设止损-12%
- 300760 迈瑞医疗：医药防御，可继续持有

【目标仓位】
- 减仓后总仓位控制在35-40%
- 保留60-65%现金应对下跌
- 等牛市信号再逐步加仓
""")

print(f"\n【止损设置】")
print(f"  股票/ETF          当前成本      止损价格      止损幅度")
print(f"  {'-'*55}")
stop_loss_settings = [
    ('紫金矿业', 35.48, -0.12),
    ('迈瑞医疗', 178.48, -0.10),
    ('万华化学', 78.96, -0.10),
]
for name, cost, sl in stop_loss_settings:
    stop_price = cost * (1 + sl)
    print(f"  {name:<15} {cost:<12.2f} {stop_price:<12.2f} {sl*100:>6.0f}%")

print(f"\n【ETF止损】")
print(f"  所有ETF统一设置止损：成本价-8%")
for p in portfolio:
    if 'ETF' in p['type'] and p['weight'] > 0.01:
        stop_price = p['cost'] * 0.92
        print(f"  {p['name']:<15} 成本{p['cost']:.4f} -> 止损{stop_price:.4f}")

print(f"\n{'='*80}")
print("  总结")
print(f"{'='*80}")
print(f"  当前问题：仓位过重（67% vs 建议30%），科技/周期占比过高")
print(f"  核心风险：熊市继续下跌可能亏损20-30%")
print(f"  紧急行动：本周减仓至40%，保留现金")
print(f"  后续策略：等沪深300站上MA20再逐步加仓")
print(f"{'='*80}")
