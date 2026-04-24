# -*- coding: utf-8 -*-
"""
恐慌指数分析 - 基于今日真实行情数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json, os, math

# 加载今日全市场数据
data_path = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\all_stocks.json'
with open(data_path, encoding='utf-8') as f:
    stocks = json.load(f)

total = len(stocks)
prices = [s for s in stocks if s.get('price', 0) > 0]

# ── 基础统计 ──────────────────────────────────────────
up       = [s for s in prices if s.get('change_pct', 0) > 0]
down     = [s for s in prices if s.get('change_pct', 0) < 0]
flat     = [s for s in prices if s.get('change_pct', 0) == 0]

limit_up   = [s for s in prices if s.get('change_pct', 0) >= 9.9]
limit_down = [s for s in prices if s.get('change_pct', 0) <= -9.9]
up5        = [s for s in prices if s.get('change_pct', 0) >= 5]
down5      = [s for s in prices if s.get('change_pct', 0) <= -5]
down3      = [s for s in prices if s.get('change_pct', 0) <= -3]

# ── 涨跌比 ────────────────────────────────────────────
ud_ratio = len(up) / len(down) if len(down) > 0 else 999

# ── 平均涨跌幅 ────────────────────────────────────────
avg_chg = sum(s.get('change_pct', 0) for s in prices) / len(prices)

# ── 成交额统计 ────────────────────────────────────────
total_amount = sum(s.get('amount', 0) for s in prices)  # 元
total_amount_yi = total_amount / 1e8  # 亿元

# ── 振幅统计 ──────────────────────────────────────────
amplitudes = [s.get('amplitude', 0) for s in prices if s.get('amplitude', 0) > 0]
avg_amplitude = sum(amplitudes) / len(amplitudes) if amplitudes else 0

# ── 恐慌指数计算（0-100，越高越恐慌）────────────────────
# 维度1：涨跌比（正常1.0，越低越恐慌）
# 涨跌比0.1 -> 90分恐慌；涨跌比1.0 -> 50分；涨跌比2.0 -> 20分
ud_score = max(0, min(100, 100 - ud_ratio * 40))

# 维度2：跌停数量占比
limit_down_ratio = len(limit_down) / total * 100
ld_score = min(100, limit_down_ratio * 5)  # 每1%跌停 -> 5分恐慌

# 维度3：平均涨跌幅（-3%以下开始恐慌）
avg_score = max(0, min(100, (-avg_chg - 1) * 20))

# 维度4：下跌5%以上占比
down5_ratio = len(down5) / total * 100
d5_score = min(100, down5_ratio * 3)

# 维度5：涨停/跌停比（正常>1，越低越恐慌）
lu_ld_ratio = len(limit_up) / len(limit_down) if len(limit_down) > 0 else 10
lul_score = max(0, min(100, 80 - lu_ld_ratio * 15))

# 综合恐慌指数（加权）
panic_index = (
    ud_score    * 0.30 +
    ld_score    * 0.20 +
    avg_score   * 0.25 +
    d5_score    * 0.15 +
    lul_score   * 0.10
)
panic_index = round(panic_index, 1)

# 恐慌等级
if panic_index >= 80:
    level = "极度恐慌 💀"
    signal = "历史性底部区域，逆向布局时机"
elif panic_index >= 65:
    level = "高度恐慌 😱"
    signal = "市场情绪崩溃，可能接近阶段底"
elif panic_index >= 50:
    level = "明显恐慌 😰"
    signal = "恐慌蔓延，谨慎观望为主"
elif panic_index >= 35:
    level = "轻度恐慌 😟"
    signal = "情绪偏弱，等待企稳信号"
elif panic_index >= 20:
    level = "情绪中性 😐"
    signal = "市场平稳，正常波动"
else:
    level = "情绪乐观 😊"
    signal = "注意过热风险"

# ── 行业分布（跌幅最惨的行业）────────────────────────
industry_stats = {}
for s in prices:
    ind = s.get('industry', '未知')
    if not ind:
        ind = '未知'
    if ind not in industry_stats:
        industry_stats[ind] = {'count': 0, 'total_chg': 0, 'down': 0}
    industry_stats[ind]['count'] += 1
    industry_stats[ind]['total_chg'] += s.get('change_pct', 0)
    if s.get('change_pct', 0) < 0:
        industry_stats[ind]['down'] += 1

# 计算行业平均涨跌幅
for ind in industry_stats:
    c = industry_stats[ind]['count']
    industry_stats[ind]['avg_chg'] = industry_stats[ind]['total_chg'] / c if c > 0 else 0

# 跌幅最大的10个行业
worst_industries = sorted(
    [(k, v) for k, v in industry_stats.items() if v['count'] >= 5 and k != '未知'],
    key=lambda x: x[1]['avg_chg']
)[:10]

# 跌幅最小（相对抗跌）的10个行业
best_industries = sorted(
    [(k, v) for k, v in industry_stats.items() if v['count'] >= 5 and k != '未知'],
    key=lambda x: x[1]['avg_chg'],
    reverse=True
)[:10]

# ── 输出报告 ──────────────────────────────────────────
print("=" * 65)
print("  A股恐慌指数分析报告  2026-04-03 收盘")
print("=" * 65)

print("\n【一、今日市场全景】")
print(f"  全市场股票数：{total} 只")
print(f"  上涨：{len(up)} 只  下跌：{len(down)} 只  平盘：{len(flat)} 只")
print(f"  涨跌比：{ud_ratio:.2f}  （正常值约1.0）")
print(f"  平均涨跌幅：{avg_chg:+.2f}%")
print(f"  涨停：{len(limit_up)} 只  跌停：{len(limit_down)} 只")
print(f"  涨幅>5%：{len(up5)} 只  跌幅>5%：{len(down5)} 只")
print(f"  跌幅>3%：{len(down3)} 只  占比：{len(down3)/total*100:.1f}%")
if total_amount_yi > 0:
    print(f"  全市场成交额：{total_amount_yi:.0f} 亿元")

print("\n【二、恐慌指数】")
bar_len = int(panic_index / 2)
bar = "█" * bar_len + "░" * (50 - bar_len)
print(f"\n  恐慌指数：{panic_index} / 100")
print(f"  [{bar}]")
print(f"  等级：{level}")
print(f"\n  分项得分：")
print(f"    涨跌比得分：    {ud_score:.1f}  （涨跌比={ud_ratio:.2f}）")
print(f"    跌停占比得分：  {ld_score:.1f}  （跌停{len(limit_down)}只={limit_down_ratio:.1f}%）")
print(f"    平均跌幅得分：  {avg_score:.1f}  （均跌{avg_chg:.2f}%）")
print(f"    大跌占比得分：  {d5_score:.1f}  （跌>5%占{down5_ratio:.1f}%）")
print(f"    涨跌停比得分：  {lul_score:.1f}  （涨停{len(limit_up)}:跌停{len(limit_down)}）")

print("\n【三、市场信号】")
print(f"  {signal}")

# 历史对比
print("\n  历史参考：")
print(f"  恐慌指数 >80：2024年2月（924行情前夕）、2022年4月（上海封控）")
print(f"  恐慌指数 65-80：2023年10月、2024年1月")
print(f"  当前 {panic_index} 分 → ", end="")
if panic_index >= 65:
    print("处于历史高恐慌区间，往往是中期底部附近")
elif panic_index >= 50:
    print("恐慌情绪明显，但尚未到极端")
else:
    print("恐慌程度一般")

print("\n【四、行业恐慌分布】")
print("\n  跌幅最惨的10个行业：")
print(f"  {'行业':<15} {'平均涨跌':<10} {'股票数':<8} {'下跌占比'}")
print(f"  {'-'*50}")
for ind, stat in worst_industries:
    down_ratio = stat['down'] / stat['count'] * 100
    print(f"  {ind:<15} {stat['avg_chg']:>+.2f}%     {stat['count']:<8} {down_ratio:.0f}%")

print(f"\n  相对抗跌的10个行业：")
print(f"  {'行业':<15} {'平均涨跌':<10} {'股票数':<8} {'下跌占比'}")
print(f"  {'-'*50}")
for ind, stat in best_industries:
    down_ratio = stat['down'] / stat['count'] * 100
    print(f"  {ind:<15} {stat['avg_chg']:>+.2f}%     {stat['count']:<8} {down_ratio:.0f}%")

print("\n【五、操作建议】")
if panic_index >= 65:
    print("""
  ⚡ 高度恐慌区间，历史上往往是布局良机：
  1. 不要追杀，恐慌性抛售接近尾声
  2. 分批建仓，不要一次性满仓
  3. 优先选择抗跌行业中的龙头股
  4. 等待成交量萎缩到极致后的放量反弹信号
  5. 止损线：若继续跌破近期低点则减仓""")
elif panic_index >= 50:
    print("""
  ⚠️ 恐慌情绪明显，谨慎操作：
  1. 控制仓位，不要重仓
  2. 关注抗跌板块的防御性机会
  3. 等待市场企稳信号再加仓""")
else:
    print("""
  📊 市场情绪尚可，正常操作即可""")

print("\n" + "=" * 65)
