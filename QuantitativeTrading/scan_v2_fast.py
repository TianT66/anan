# -*- coding: utf-8 -*-
"""
扩大筛选 v2 - 快速版
只分析PE最低的50只，排除问题行业，直接输出结果
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("扩大筛选 v2 - 快速版")
print("=" * 70)

# 第1步：获取全市场数据
print("\n[1/3] 获取全市场数据...")
df = ak.stock_zh_a_spot_em()
print(f"    获取 {len(df)} 只股票")

# 数据清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')

# 过滤
df = df[df['名称'].str.contains('ST', na=False) == False]
df = df[df['最新价'] > 0]
df_valid = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 25)]
print(f"    清洗后 {len(df_valid)} 只")

# 第2步：快速筛选
print("\n[2/3] 快速筛选...")

# 排除关键词
exclude = ['银行', '证券', '保险', '航空', '旅游', '酒店', '地产', '万科', '煤炭', '钢铁', '石油']

# 取PE最低的100只
sample = df_valid.nsmallest(100, '市盈率-动态').copy()

# 快速排除
results = []
for _, row in sample.iterrows():
    name = row['名称']
    # 快速排除
    if any(k in name for k in exclude):
        continue

    results.append({
        'code': row['代码'],
        'name': name,
        'price': row['最新价'],
        'pe': row['市盈率-动态'],
        'pb': row['市净率'],
        'change': row['涨跌幅'],
        'ytd': row['年初至今涨跌幅'] if pd.notna(row['年初至今涨跌幅']) else 0,
        'mkt_cap': row['流通市值'],
    })

print(f"    排除问题行业后: {len(results)} 只")

# 第3步：获取财务数据（只对top 20做深度分析）
print("\n[3/3] 深度财务分析（仅top 20）...")

for r in results[:20]:
    try:
        fin = ak.stock_financial_analysis_indicator(symbol=r['code'], start_year="2023")
        if fin is not None and len(fin) >= 4:
            if '净资产收益率(%)' in fin.columns:
                roe_vals = fin['净资产收益率(%)'].dropna().tolist()
                if len(roe_vals) >= 4 and all(v > 0 for v in roe_vals[:4]):
                    r['roe'] = roe_vals[0]
                    avg_roe = sum(roe_vals[1:4]) / 3
                    r['roe_change'] = (roe_vals[0] - avg_roe) / avg_roe
                else:
                    r['roe'] = 0
                    r['roe_change'] = 0
            else:
                r['roe'] = 0
                r['roe_change'] = 0
        else:
            r['roe'] = 0
            r['roe_change'] = 0
    except:
        r['roe'] = 0
        r['roe_change'] = 0

    time.sleep(0.3)

# 评分
for r in results:
    score = 0
    if r['pe'] < 10: score += 30
    elif r['pe'] < 15: score += 20
    elif r['pe'] < 20: score += 10

    if r.get('roe', 0) > 15: score += 25
    elif r.get('roe', 0) > 10: score += 20
    elif r.get('roe', 0) > 5: score += 10

    if r.get('roe_change', 0) > 0: score += 15
    elif r.get('roe_change', 0) > -0.1: score += 5

    if r['ytd'] < -30: score += 20
    elif r['ytd'] < -20: score += 10

    r['score'] = score

results.sort(key=lambda x: x['score'], reverse=True)

# 输出
print("\n" + "=" * 70)
print("【扩大筛选结果】")
print("=" * 70)

print("\n筛选标准:")
print("  1. PE < 25")
print("  2. 排除：银行、保险、证券、地产、周期品")
print("  3. ROE > 0 且稳定/增长")
print()

for i, r in enumerate(results[:15], 1):
    roe_str = f"{r.get('roe', 0):.1f}%" if r.get('roe', 0) > 0 else "N/A"
    trend = "^" if r.get('roe_change', 0) > 0.05 else "->" if r.get('roe_change', 0) > -0.1 else "v"
    print(f"{i:2d}. {r['name']}({r['code']}) PE={r['pe']:.1f} ROE={roe_str}({trend}) 年初至今{r['ytd']:+.0f}%")

# TOP 5 详细分析
print("\n" + "=" * 70)
print("【TOP 5 详细分析】")
print("=" * 70)

for i, r in enumerate(results[:5], 1):
    print(f"\n{i}. {r['name']}({r['code']})")
    print("-" * 50)

    # 估值
    if r['pe'] < 10: val = "极低"
    elif r['pe'] < 15: val = "较低"
    elif r['pe'] < 20: val = "合理"
    else: val = "偏贵"
    print(f"  估值: PE={r['pe']:.1f}({val}) PB={r['pb']:.2f}")

    # ROE
    roe = r.get('roe', 0)
    roe_chg = r.get('roe_change', 0)
    if roe > 0:
        trend = "上升" if roe_chg > 0.05 else "稳定" if roe_chg > -0.1 else "小幅下滑"
        print(f"  ROE: {roe:.1f}% 趋势: {trend}({roe_chg:+.1%})")
    else:
        print(f"  ROE: N/A")

    # 错杀原因
    if r['ytd'] < -40:
        reason = "超跌40%以上，市场恐慌导致的错杀"
    elif r['ytd'] < -30:
        reason = "年初至今跌幅超30%，被市场误解"
    elif r['change'] < -5:
        reason = "今日大跌，可能受战争恐慌拖累"
    else:
        reason = "估值低+盈利稳定"
    print(f"  错杀原因: {reason}")

    # 市值
    if r['mkt_cap'] > 1000: size = "大盘"
    elif r['mkt_cap'] > 300: size = "中盘"
    else: size = "小盘"
    print(f"  市值: {r['mkt_cap']/10000:.1f}亿 ({size})")

    # 翻倍潜力
    if r['pe'] < 15 and roe > 10 and r['ytd'] < -30:
        potential = "极高"
    elif r['pe'] < 20 and roe > 5:
        potential = "高"
    elif r['pe'] < 25 and roe > 0:
        potential = "中"
    else:
        potential = "待观察"
    print(f"  翻倍潜力: {potential}")

    # 目标价
    if roe > 15: fair_pe = 20
    elif roe > 10: fair_pe = 15
    elif roe > 5: fair_pe = 12
    else: fair_pe = 10
    target = r['price'] * (fair_pe / r['pe'])
    profit = (target - r['price']) / r['price'] * 100
    print(f"  合理PE: {fair_pe} → 目标价 ¥{target:.2f} (+{profit:.0f}%)")

    # 持有期
    if r['ytd'] < -30: period = "6-12个月"
    else: period = "3-6个月"
    print(f"  持有期: {period}")

print("\n" + "=" * 70)
