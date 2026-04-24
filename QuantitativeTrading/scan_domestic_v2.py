# -*- coding: utf-8 -*-
"""
内需型行业深度筛选 v2 - 修复版
排除：金融、地产、周期品、出口导向
重点：医药、消费、公用事业、制造业
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("内需型行业深度筛选 v2")
print("=" * 70)

# 第1步：获取全市场数据
print("\n[1/5] 获取全市场数据...")
df = ak.stock_zh_a_spot_em()
print(f"    获取 {len(df)} 只股票")

# 数据清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')
df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')

# 过滤ST
df = df[df['名称'].str.contains('ST', na=False) == False]

# 第2步：排除问题行业
print("\n[2/5] 行业筛选...")

exclude_keywords = [
    '银行', '证券', '保险', '信托', '期货',
    '地产', '万科', '恒大', '碧桂园', '融创',
    '煤炭', '钢铁', '石油', '化工', '水泥',
    '航空', '航运', '港口', '物流',
    '旅游', '酒店', '餐饮', '影院',
    '电子', '芯片', '半导体', '光伏', '锂电', '新能源',
    '猪', '牧原', '温氏', '新希望',
    '军工', '国防',
]

def is_excluded(name):
    for kw in exclude_keywords:
        if kw in name:
            return True
    return False

df_clean = df[~df['名称'].apply(is_excluded)]
print(f"    排除问题行业后: {len(df_clean)} 只")

# 第3步：估值筛选
print("\n[3/5] 估值筛选...")

df_valid = df_clean[(df_clean['市盈率-动态'] > 0) & (df_clean['市盈率-动态'] < 25)]
df_valid = df_valid[df_valid['市净率'] < 3]
df_valid = df_valid[df_valid['最新价'] > 0]
print(f"    PE<25 且 PB<3: {len(df_valid)} 只")

# 第4步：超跌筛选
print("\n[4/5] 超跌筛选...")

# 按超跌排序
df_oversold = df_valid[df_valid['年初至今涨跌幅'] < 0]
df_oversold = df_oversold.sort_values('年初至今涨跌幅')
print(f"    年初至今下跌: {len(df_oversold)} 只")

# 取跌幅最大的50只
sample = df_oversold.head(50)
print(f"    取跌幅最大的50只进行深度分析")

# 第5步：深度财务分析
print("\n[5/5] 深度财务分析...")

results = []
total = len(sample)

for i, (_, row) in enumerate(sample.iterrows(), 1):
    code = row['代码']
    name = row['名称']

    print(f"    [{i}/{total}] {name}...", end=" ")

    roe = 0
    roe_change = 0
    profit_growth = 0

    try:
        fin = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")
        if fin is not None and len(fin) >= 4:
            if '净资产收益率(%)' in fin.columns:
                roe_vals = fin['净资产收益率(%)'].dropna().tolist()
                if len(roe_vals) >= 4 and all(v > 0 for v in roe_vals[:4]):
                    roe = roe_vals[0]
                    avg_roe = sum(roe_vals[1:4]) / 3
                    roe_change = (roe - avg_roe) / avg_roe

            if '净利润(元)' in fin.columns:
                profit_vals = fin['净利润(元)'].dropna().tolist()
                if len(profit_vals) >= 2 and profit_vals[1] > 0:
                    profit_growth = (profit_vals[0] - profit_vals[1]) / profit_vals[1]
    except:
        pass

    # 评分
    score = 0
    if row['市盈率-动态'] < 10: score += 20
    elif row['市盈率-动态'] < 15: score += 15
    else: score += 10

    if row['市净率'] < 1: score += 15
    elif row['市净率'] < 2: score += 10

    if roe > 15: score += 25
    elif roe > 10: score += 20
    elif roe > 5: score += 10

    if profit_growth > 0.2: score += 20
    elif profit_growth > 0: score += 10

    if roe_change > 0.1: score += 15
    elif roe_change > -0.1: score += 10

    ytd = row['年初至今涨跌幅']
    if ytd < -40: score += 20
    elif ytd < -30: score += 15
    elif ytd < -20: score += 10
    elif ytd < -10: score += 5

    results.append({
        'code': code,
        'name': name,
        'price': row['最新价'],
        'pe': row['市盈率-动态'],
        'pb': row['市净率'],
        'ytd': ytd,
        'mkt_cap': row['流通市值'],
        'roe': roe,
        'roe_change': roe_change,
        'profit_growth': profit_growth,
        'score': score,
    })

    print(f"ROE={roe:.1f}%, 利润={profit_growth:+.0%}, 得分={score}")

    time.sleep(0.3)

results.sort(key=lambda x: x['score'], reverse=True)

# 输出
print("\n" + "=" * 70)
print("【内需型行业筛选结果 - TOP 20 被错杀价值股】")
print("=" * 70)

for i, r in enumerate(results[:20], 1):
    roe_str = f"{r['roe']:.1f}%" if r['roe'] > 0 else "N/A"
    trend = "^" if r['roe_change'] > 0.1 else "->" if r['roe_change'] > -0.1 else "v"
    profit_str = f"{r['profit_growth']:+.0%}" if r['profit_growth'] != 0 else "N/A"

    print(f"\n{i:2d}. {r['name']}({r['code']})")
    print(f"    价格: ¥{r['price']:.2f} | PE: {r['pe']:.1f} | PB: {r['pb']:.2f}")
    print(f"    年初至今: {r['ytd']:+.1f}%")
    print(f"    ROE: {roe_str}({trend}) | 利润增长: {profit_str}")
    print(f"    得分: {r['score']}")

# TOP 5 详细分析
print("\n" + "=" * 70)
print("【TOP 5 深度博弈分析】")
print("=" * 70)

for i, r in enumerate(results[:5], 1):
    print(f"\n{'='*60}")
    print(f"{i}. {r['name']}({r['code']})")
    print(f"{'='*60}")

    # 估值
    print(f"\n【估值分析】")
    if r['pe'] < 8: val = "极低"
    elif r['pe'] < 12: val = "较低"
    elif r['pe'] < 18: val = "合理"
    else: val = "偏贵"
    print(f"  PE={r['pe']:.1f} ({val})")

    if r['pb'] < 1: pb_val = "破净"
    elif r['pb'] < 2: pb_val = "正常"
    else: pb_val = "较高"
    print(f"  PB={r['pb']:.2f} ({pb_val})")

    # 业绩
    print(f"\n【业绩分析】")
    if r['roe'] > 0:
        print(f"  ROE={r['roe']:.1f}%，趋势:{'上升' if r['roe_change']>0.1 else '稳定' if r['roe_change']>-0.1 else '下滑'}")
    else:
        print(f"  ROE=N/A")
    if r['profit_growth'] != 0:
        print(f"  净利润增长: {r['profit_growth']:+.1%}")

    # 错杀原因
    print(f"\n【错杀原因】")
    if r['ytd'] < -40: reason = "超跌40%以上，市场恐慌错杀"
    elif r['ytd'] < -30: reason = "年初至今跌幅超30%"
    elif r['ytd'] < -20: reason = "年初至今跌幅20%以上"
    else: reason = "估值低但未被市场认可"
    print(f"  {reason}")

    # 翻倍潜力
    print(f"\n【翻倍潜力】")
    potential = "极高" if r['score'] >= 70 else "高" if r['score'] >= 50 else "中" if r['score'] >= 30 else "待观察"
    print(f"  {potential} (得分: {r['score']})")

    # 目标价
    if r['roe'] > 15: fair_pe = 20
    elif r['roe'] > 10: fair_pe = 15
    elif r['roe'] > 5: fair_pe = 12
    else: fair_pe = 10

    target = r['price'] * (fair_pe / r['pe'])
    profit = (target - r['price']) / r['price'] * 100

    print(f"\n【操作建议】")
    print(f"  合理PE: {fair_pe}")
    print(f"  目标价: ¥{target:.2f} (+{profit:.0f}%)")
    print(f"  持有期: {'6-12个月' if r['ytd'] < -30 else '3-6个月'}")

print("\n" + "=" * 70)
