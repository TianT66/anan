# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json

with open(r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\all_stocks.json', encoding='utf-8') as f:
    stocks = json.load(f)

prices = [s for s in stocks if s.get('price', 0) > 0 and s.get('change_pct') is not None]
total = len(prices)

up         = [s for s in prices if s['change_pct'] > 0]
down       = [s for s in prices if s['change_pct'] < 0]
flat       = [s for s in prices if s['change_pct'] == 0]
limit_up   = [s for s in prices if s['change_pct'] >= 9.9]
limit_down = [s for s in prices if s['change_pct'] <= -9.9]
up5        = [s for s in prices if s['change_pct'] >= 5]
up3        = [s for s in prices if s['change_pct'] >= 3]
down3      = [s for s in prices if s['change_pct'] <= -3]
down5      = [s for s in prices if s['change_pct'] <= -5]
down7      = [s for s in prices if s['change_pct'] <= -7]

ud_ratio   = len(up) / len(down) if len(down) > 0 else 999
avg_chg    = sum(s['change_pct'] for s in prices) / total

total_amount_yi = sum(s.get('amount', 0) for s in prices) / 1e8

# 振幅
amps = [s.get('amplitude', 0) or ((s['high']-s['low'])/s['prev_close']*100 if s.get('prev_close',0)>0 else 0) for s in prices]
amps = [a for a in amps if a > 0]
avg_amp = sum(amps)/len(amps) if amps else 0

# 换手率
turnovers = [s.get('turnover', 0) for s in prices if s.get('turnover', 0) > 0]
avg_turnover = sum(turnovers)/len(turnovers) if turnovers else 0

# PE分布
pe_valid = [s for s in prices if s.get('pe', 0) and 0 < s['pe'] < 200]
avg_pe = sum(s['pe'] for s in pe_valid)/len(pe_valid) if pe_valid else 0

# 市值分布
mc_valid = [s for s in prices if s.get('market_cap', 0) > 0]
small_cap  = [s for s in mc_valid if s['market_cap'] < 5e8]   # <5亿
mid_cap    = [s for s in mc_valid if 5e8 <= s['market_cap'] < 50e8]
large_cap  = [s for s in mc_valid if s['market_cap'] >= 50e8]

# 跌幅分布
chg_dist = {
    '涨停(≥+10%)':  len([s for s in prices if s['change_pct'] >= 10]),
    '+5%~+10%':     len([s for s in prices if 5 <= s['change_pct'] < 10]),
    '+3%~+5%':      len([s for s in prices if 3 <= s['change_pct'] < 5]),
    '0%~+3%':       len([s for s in prices if 0 < s['change_pct'] < 3]),
    '平盘(0%)':     len(flat),
    '-3%~0%':       len([s for s in prices if -3 < s['change_pct'] < 0]),
    '-5%~-3%':      len([s for s in prices if -5 <= s['change_pct'] <= -3]),
    '-10%~-5%':     len([s for s in prices if -10 < s['change_pct'] < -5]),
    '跌停(≤-10%)':  len([s for s in prices if s['change_pct'] <= -10]),
}

# ── 恐慌指数计算 ──────────────────────────────────────
# 1. 涨跌比（0.15 -> 极度恐慌）
# 正常1.0=0分，0.5=30分，0.15=80分，0.05=100分
ud_score = max(0, min(100, (1 - ud_ratio) / 0.95 * 80)) if ud_ratio < 1 else 0

# 2. 平均跌幅（-2%=20分，-3%=50分，-5%=90分）
avg_score = max(0, min(100, (-avg_chg) * 18))

# 3. 跌幅>5%占比（10%=30分，20%=60分，30%=90分）
d5_ratio = len(down5) / total * 100
d5_score = min(100, d5_ratio * 3)

# 4. 涨停/跌停比（正常>2，越低越恐慌）
lu_ld = len(limit_up) / len(limit_down) if len(limit_down) > 0 else 10
lul_score = max(0, min(100, (2 - lu_ld) / 2 * 60)) if lu_ld < 2 else 0

# 5. 下跌股票占比（80%=50分，90%=80分，95%=100分）
down_ratio = len(down) / total * 100
dr_score = max(0, min(100, (down_ratio - 50) * 2))

panic_index = round(
    ud_score  * 0.30 +
    avg_score * 0.25 +
    d5_score  * 0.20 +
    lul_score * 0.15 +
    dr_score  * 0.10,
    1
)

if panic_index >= 80:
    level = "极度恐慌 💀"
    color = "历史性底部区域"
elif panic_index >= 65:
    level = "高度恐慌 😱"
    color = "市场情绪崩溃"
elif panic_index >= 50:
    level = "明显恐慌 😰"
    color = "恐慌蔓延"
elif panic_index >= 35:
    level = "轻度恐慌 😟"
    color = "情绪偏弱"
elif panic_index >= 20:
    level = "情绪中性 😐"
    color = "正常波动"
else:
    level = "情绪乐观 😊"
    color = "注意过热"

bar_len = int(panic_index / 2)
bar = "█" * bar_len + "░" * (50 - bar_len)

print("=" * 65)
print("  A股恐慌指数分析报告  2026-04-03 收盘")
print("=" * 65)

print(f"""
【一、今日市场全景】
  全市场有效股票：{total} 只
  上涨：{len(up)} 只（{len(up)/total*100:.1f}%）
  下跌：{len(down)} 只（{len(down)/total*100:.1f}%）
  平盘：{len(flat)} 只（{len(flat)/total*100:.1f}%）
  涨跌比：{ud_ratio:.3f}  （正常值约1.0）
  平均涨跌幅：{avg_chg:+.2f}%
  涨停：{len(limit_up)} 只  跌停：{len(limit_down)} 只
  涨幅>5%：{len(up5)} 只  跌幅>5%：{len(down5)} 只
  跌幅>7%：{len(down7)} 只
  全市场成交额：{total_amount_yi:.0f} 亿元
  平均换手率：{avg_turnover:.2f}%
  平均PE（有效）：{avg_pe:.1f}x""")

print(f"""
【二、涨跌幅分布】""")
for k, v in chg_dist.items():
    bar2 = "▓" * int(v/total*100)
    print(f"  {k:<14} {v:>5} 只  {v/total*100:>5.1f}%  {bar2}")

print(f"""
【三、恐慌指数】

  恐慌指数：{panic_index} / 100
  [{bar}]
  等级：{level}

  分项得分：
    涨跌比得分：      {ud_score:.1f}  （涨跌比={ud_ratio:.3f}，正常≈1.0）
    平均跌幅得分：    {avg_score:.1f}  （全市场均跌{avg_chg:.2f}%）
    大跌占比得分：    {d5_score:.1f}  （跌>5%占{d5_ratio:.1f}%）
    涨跌停比得分：    {lul_score:.1f}  （涨停{len(limit_up)}只 vs 跌停{len(limit_down)}只）
    下跌占比得分：    {dr_score:.1f}  （{down_ratio:.1f}%股票下跌）""")

print(f"""
【四、市场信号与历史对比】
  当前信号：{color}，恐慌指数 {panic_index}

  历史参考区间：
  ┌─────────────────────────────────────────────┐
  │ 指数  0-20  ：情绪乐观，注意高位风险        │
  │ 指数 20-35  ：情绪中性，正常操作            │
  │ 指数 35-50  ：轻度恐慌，谨慎观望            │
  │ 指数 50-65  ：明显恐慌，可小仓位试探        │
  │ 指数 65-80  ：高度恐慌，历史上接近底部      │
  │ 指数 80-100 ：极度恐慌，逆向布局良机 ★     │
  └─────────────────────────────────────────────┘
  当前 {panic_index} 分 → {"▶ 处于高恐慌区间，历史上往往是中期底部附近" if panic_index >= 65 else "▶ 恐慌情绪明显，但尚未到极端恐慌" if panic_index >= 50 else "▶ 轻度恐慌，市场情绪偏弱"}""")

print(f"""
【五、市值结构】
  小盘股（<5亿）：  {len(small_cap)} 只（{len(small_cap)/len(mc_valid)*100:.1f}%）
  中盘股（5-50亿）：{len(mid_cap)} 只（{len(mid_cap)/len(mc_valid)*100:.1f}%）
  大盘股（>50亿）： {len(large_cap)} 只（{len(large_cap)/len(mc_valid)*100:.1f}%）""")

# 大盘股跌幅
large_avg = sum(s['change_pct'] for s in large_cap)/len(large_cap) if large_cap else 0
small_avg = sum(s['change_pct'] for s in small_cap)/len(small_cap) if small_cap else 0
print(f"  大盘股平均涨跌：{large_avg:+.2f}%")
print(f"  小盘股平均涨跌：{small_avg:+.2f}%")
if large_avg > small_avg:
    print(f"  → 大盘股相对抗跌，资金向蓝筹避险")
else:
    print(f"  → 小盘股相对抗跌，题材股有局部活跃")

print(f"""
【六、操作建议】""")
if panic_index >= 65:
    print("""  ⚡ 高度恐慌区间，历史上往往是布局良机：
  1. 不要追杀，恐慌性抛售接近尾声
  2. 分批建仓，不要一次性满仓（每次10-20%仓位）
  3. 优先选择大盘蓝筹、高股息防御性品种
  4. 等待成交量萎缩到极致后的放量反弹信号
  5. 止损线：若继续跌破近期低点则减仓""")
elif panic_index >= 50:
    print("""  ⚠️ 恐慌情绪明显，谨慎操作：
  1. 控制仓位在30-50%，不要重仓
  2. 关注抗跌板块的防御性机会
  3. 等待市场企稳信号（连续两日缩量+收阳）再加仓
  4. 避免追涨停板，情绪市容易高开低走""")
elif panic_index >= 35:
    print("""  📊 轻度恐慌，保持谨慎：
  1. 维持现有仓位，不要盲目加仓
  2. 关注基本面扎实的个股逢低机会
  3. 等待市场方向明朗""")

print("\n" + "=" * 65)
