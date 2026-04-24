# -*- coding: utf-8 -*-
"""
快速筛选版 - 只用实时行情数据，不查财务
"""
import akshare as ak
import pandas as pd
import sys
import warnings
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("快速筛选 - 内需型被错杀价值股")
print("=" * 70)

# 获取数据
print("\n[1/2] 获取全市场数据...")
df = ak.stock_zh_a_spot_em()
print(f"    获取 {len(df)} 只股票")

# 清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')

# 排除ST
df = df[df['名称'].str.contains('ST', na=False) == False]

# 排除问题行业
exclude = ['银行', '证券', '保险', '信托', '期货', '地产', '万科', '恒大',
           '煤炭', '钢铁', '石油', '化工', '水泥', '航空', '航运', '港口',
           '旅游', '酒店', '餐饮', '电子', '芯片', '半导体', '光伏', '锂电',
           '新能源', '猪', '牧原', '温氏', '军工', '国防']

def is_ok(name):
    for kw in exclude:
        if kw in name:
            return False
    return True

df = df[df['名称'].apply(is_ok)]
print(f"    排除问题行业后: {len(df)} 只")

# 筛选
print("\n[2/2] 筛选...")

# PE 0-20
df = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 20)]
print(f"    PE<20: {len(df)} 只")

# PB 0-2
df = df[df['市净率'] < 2]
print(f"    PB<2: {len(df)} 只")

# 年初至今下跌
df = df[df['年初至今涨跌幅'] < 0]
print(f"    年初至今下跌: {len(df)} 只")

# 按跌幅排序
df = df.sort_values('年初至今涨跌幅')

# 快速评分
results = []
for _, row in df.iterrows():
    score = 0
    pe = row['市盈率-动态']
    pb = row['市净率']
    ytd = row['年初至今涨跌幅']
    mkt = row['流通市值'] / 10000  # 亿

    if pe < 8: score += 25
    elif pe < 12: score += 18
    elif pe < 15: score += 12
    else: score += 6

    if pb < 0.8: score += 20
    elif pb < 1: score += 15
    elif pb < 1.5: score += 10
    else: score += 5

    if ytd < -40: score += 25
    elif ytd < -30: score += 20
    elif ytd < -20: score += 15
    elif ytd < -10: score += 10
    else: score += 5

    if 50 < mkt < 500: score += 10  # 中小市值

    results.append({
        'code': row['代码'],
        'name': row['名称'],
        'price': row['最新价'],
        'pe': pe,
        'pb': pb,
        'ytd': ytd,
        'mkt': mkt,
        'score': score,
    })

results.sort(key=lambda x: x['score'], reverse=True)

# 输出
print("\n" + "=" * 70)
print("【TOP 25 被错杀价值股】")
print("=" * 70)

print("\n筛选标准: PE<20, PB<2, 年初至今下跌, 排除金融/地产/周期/科技")
print()

for i, r in enumerate(results[:25], 1):
    pb_tag = "破净" if r['pb'] < 1 else ""
    print(f"{i:2d}. {r['name']:8s}({r['code']}) PE={r['pe']:5.1f} PB={r['pb']:.2f}{pb_tag:4s} 年初{r['ytd']:+5.1f}% 市值{r['mkt']:.0f}亿 得分{r['score']}")

# 按行业分组
print("\n" + "=" * 70)
print("【按行业分组】")
print("=" * 70)

# 医药
medicals = [r for r in results if any(k in r['name'] for k in ['药', '医', '生物', '康', '济', '仁', '片'])]
if medicals:
    print(f"\n【医药生物】({len(medicals)}只)")
    for r in medicals[:5]:
        print(f"  {r['name']}({r['code']}) PE={r['pe']:.1f} PB={r['pb']:.2f} 年初{r['ytd']:+.1f}%")

# 消费
consumes = [r for r in results if any(k in r['name'] for k in ['酒', '食', '饮', '乳', '肉', '菜', '厨', '家电', '电', '服装', '纺', '鞋'])]
if consumes:
    print(f"\n【消费】({len(consumes)}只)")
    for r in consumes[:5]:
        print(f"  {r['name']}({r['code']}) PE={r['pe']:.1f} PB={r['pb']:.2f} 年初{r['ytd']:+.1f}%")

# 公用事业
utilities = [r for r in results if any(k in r['name'] for k in ['电', '水', '气', '能', '环保', '水务'])]
if utilities:
    print(f"\n【公用事业】({len(utilities)}只)")
    for r in utilities[:5]:
        print(f"  {r['name']}({r['code']}) PE={r['pe']:.1f} PB={r['pb']:.2f} 年初{r['ytd']:+.1f}%")

# 制造业
manufactures = [r for r in results if any(k in r['name'] for k in ['机', '械', '设', '备', '造', '工', '材', '纸', '塑', '玻'])]
if manufactures:
    print(f"\n【制造业】({len(manufactures)}只)")
    for r in manufactures[:5]:
        print(f"  {r['name']}({r['code']}) PE={r['pe']:.1f} PB={r['pb']:.2f} 年初{r['ytd']:+.1f}%")

# 其他
print(f"\n【其他】({len(results) - len(medicals) - len(consumes) - len(utilities) - len(manufactures)}只)")

print("\n" + "=" * 70)
print(f"共筛选出 {len(results)} 只符合条件的股票")
print("=" * 70)
