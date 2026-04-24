# -*- coding: utf-8 -*-
"""
扩大筛选范围：寻找盈利稳定增长的真正价值股
排除：银行（价值陷阱）、次新股（筹码不稳定）、出口导向（贸易战风险）
重点：国内需求、盈利稳定、估值合理
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("扩大筛选：寻找盈利稳定的国内需求型价值股")
print("=" * 70)

# ========================
# 第1步：获取全市场数据
# ========================
print("\n[1/4] 获取全市场数据...")
df = ak.stock_zh_a_spot_em()
print(f"    获取 {len(df)} 只股票")

# 数据清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['60日涨跌幅'] = pd.to_numeric(df['60日涨跌幅'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')

# 过滤
df = df[df['名称'].str.contains('ST', na=False) == False]
df = df[df['最新价'] > 0]
df_valid = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 50)]
print(f"    清洗后 {len(df_valid)} 只")

# ========================
# 第2步：多维度筛选
# ========================
print("\n[2/4] 多维度筛选...")

# 排除列表
exclude_keywords = [
    '银行', '证券', '保险',  # 金融（价值陷阱或投资端不稳）
    '航空', '旅游', '酒店', '机场',  # 战争受损
    '地产', '万科', '保利', '绿地',  # 地产链
    '煤炭', '钢铁', '石油', '化工',  # 周期品
    '芯片', '半导体', '电子',  # 科技波动大
]

results = []

# 取PE<25的所有股票
sample = df_valid[df_valid['市盈率-动态'] < 25].copy()
print(f"    PE<25的股票: {len(sample)} 只")

for idx, row in sample.iterrows():
    code = row['代码']
    name = row['名称']
    pe = row['市盈率-动态']
    pb = row['市净率']
    price = row['最新价']
    change = row['涨跌幅']
    ytd = row['年初至今涨跌幅'] if pd.notna(row['年初至今涨跌幅']) else 0
    mkt_cap = row['流通市值']

    # 排除关键词
    is_excluded = False
    for kw in exclude_keywords:
        if kw in name:
            is_excluded = True
            break
    if is_excluded:
        continue

    # 排除次新股（2024年后上市）
    try:
        info = ak.stock_individual_info_em(symbol=code)
        if info is not None and not info.empty:
            for _, r in info.iterrows():
                if r['item'] == '上市时间':
                    date_str = str(r['value'])
                    if len(date_str) >= 4:
                        year = int(date_str[:4])
                        if year >= 2024:
                            is_excluded = True
                            break
        time.sleep(0.2)
    except:
        pass

    if is_excluded:
        continue

    # 获取财务数据
    try:
        fin = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")
        if fin is not None and len(fin) >= 4:
            roe_col = '净资产收益率(%)'
            if roe_col in fin.columns:
                roe_vals = fin[roe_col].dropna().tolist()
                if len(roe_vals) >= 4 and all(v > 0 for v in roe_vals[:4]):
                    latest_roe = roe_vals[0]
                    avg_roe = sum(roe_vals[1:4]) / 3

                    # 核心条件：盈利稳定或增长（ROE下滑<20%）
                    roe_change = (latest_roe - avg_roe) / avg_roe

                    if roe_change > -0.20:  # 盈利稳定或增长
                        results.append({
                            'code': code, 'name': name, 'price': price,
                            'pe': pe, 'pb': pb, 'change': change,
                            'ytd': ytd, 'mkt_cap': mkt_cap,
                            'roe': latest_roe, 'roe_change': roe_change
                        })
    except:
        pass

    time.sleep(0.3)

print(f"    盈利稳定的标的: {len(results)} 只")

# ========================
# 第3步：行业分类评分
# ========================
print("\n[3/4] 行业分类与评分...")

# 行业分类
def classify_industry(name):
    keywords = {
        '医药': ['医药', '医疗', '制药', '中药', '生物'],
        '消费': ['食品', '饮料', '白酒', '啤酒', '乳业', '调味', '家电', '家居'],
        '基建': ['电力', '电网', '能源', '水务', '燃气', '公路', '铁路'],
        '公用': ['环保', '环卫', '固废', '水处理'],
        '制造': ['机械', '设备', '汽车', '零部件', '电机', '电气'],
        '通信': ['通信', '电信', '网络'],
        '软件': ['软件', '信息', 'IT', '数据'],
        '零售': ['零售', '商贸', '超市', '连锁', '电商'],
    }

    for ind, kws in keywords.items():
        for kw in kws:
            if kw in name:
                return ind
    return '其他'

# 行业加分
def industry_bonus(industry):
    bonuses = {
        '医药': 15,  # 刚需，防御性强
        '消费': 12,  # 内需，稳定
        '基建': 10,  # 政策支持
        '公用': 8,   # 稳定
        '制造': 5,   # 一般
        '通信': 5,
        '软件': 5,
        '零售': 5,
        '其他': 0,
    }
    return bonuses.get(industry, 0)

for r in results:
    # 行业分类
    r['industry'] = classify_industry(r['name'])

    # 综合评分
    score = 0

    # PE评分
    if r['pe'] < 10:
        score += 30
    elif r['pe'] < 15:
        score += 25
    elif r['pe'] < 20:
        score += 15
    else:
        score += 5

    # ROE评分
    if r['roe'] > 15:
        score += 25
    elif r['roe'] > 10:
        score += 20
    elif r['roe'] > 5:
        score += 10

    # ROE变化评分
    if r['roe_change'] > 0.1:
        score += 15
    elif r['roe_change'] > 0:
        score += 10
    elif r['roe_change'] > -0.1:
        score += 5

    # 跌幅评分
    if r['ytd'] < -40:
        score += 20
    elif r['ytd'] < -30:
        score += 15
    elif r['ytd'] < -20:
        score += 10
    elif r['ytd'] < -10:
        score += 5

    # 行业加分
    score += industry_bonus(r['industry'])

    # 今日下跌加分
    if r['change'] < -5:
        score += 10
    elif r['change'] < -3:
        score += 5

    r['score'] = score

# 排序
results.sort(key=lambda x: x['score'], reverse=True)

# ========================
# 第4步：输出结果
# ========================
print("\n" + "=" * 70)
print("【扩大筛选结果：盈利稳定的国内需求型价值股】")
print("=" * 70)

print("\n筛选标准:")
print("  1. PE < 25")
print("  2. ROE > 0 且稳定/增长（下滑<20%）")
print("  3. 排除：银行、保险、证券、地产、周期品、科技、次新股")
print("  4. 重点：医药、消费、基建等国内刚需行业")
print()

print("-" * 70)

# 按行业分组输出
from collections import defaultdict
by_industry = defaultdict(list)
for r in results:
    by_industry[r['industry']].append(r)

for industry in ['医药', '消费', '基建', '公用', '制造', '通信', '软件', '零售', '其他']:
    if industry in by_industry and by_industry[industry]:
        stocks = by_industry[industry][:5]  # 每行业最多5只
        print(f"\n【{industry}】")
        for r in stocks:
            status = "^" if r['roe_change'] > 0.05 else "->" if r['roe_change'] > -0.1 else "v"
            print(f"  {r['name']}({r['code']}) PE={r['pe']:.1f} ROE={r['roe']:.1f}%({status}) 年初至今{r['ytd']:+.0f}% 得分={r['score']}")

# TOP 10 详细分析
print("\n" + "=" * 70)
print("【TOP 10 详细分析】")
print("=" * 70)

for i, r in enumerate(results[:10], 1):
    print(f"\n{i}. {r['name']}({r['code']}) [{r['industry']}]")
    print("-" * 50)

    # 估值
    if r['pe'] < 10:
        val = "极低"
    elif r['pe'] < 15:
        val = "较低"
    elif r['pe'] < 20:
        val = "合理"
    else:
        val = "偏贵"

    print(f"  估值: PE={r['pe']:.1f}({val}) PB={r['pb']:.2f}")

    # ROE
    trend = "上升" if r['roe_change'] > 0.05 else "稳定" if r['roe_change'] > -0.1 else "小幅下滑"
    print(f"  ROE: {r['roe']:.1f}% 趋势: {trend}({r['roe_change']:+.1%})")

    # 错杀原因
    if r['ytd'] < -40:
        reason = "超跌40%以上，可能是市场恐慌导致的错杀"
    elif r['ytd'] < -30:
        reason = "年初至今跌幅超30%，被市场误解"
    elif r['change'] < -5:
        reason = "今日大跌，可能受战争恐慌拖累"
    else:
        reason = "估值低+盈利稳定+行业刚需"

    print(f"  错杀原因: {reason}")

    # 市值
    if r['mkt_cap'] > 1000:
        size = "大盘"
    elif r['mkt_cap'] > 300:
        size = "中盘"
    else:
        size = "小盘"
    print(f"  市值: {r['mkt_cap']/10000:.1f}亿 ({size})")

    # 翻倍潜力
    if r['pe'] < 15 and r['roe'] > 10 and r['ytd'] < -30:
        potential = "极高"
    elif r['pe'] < 20 and r['roe'] > 8:
        potential = "高"
    elif r['pe'] < 25 and r['roe'] > 5:
        potential = "中"
    else:
        potential = "待观察"

    print(f"  翻倍潜力: {potential}")

    # 目标价估算
    if r['roe'] > 15:
        fair_pe = 20
    elif r['roe'] > 10:
        fair_pe = 15
    elif r['roe'] > 5:
        fair_pe = 12
    else:
        fair_pe = 10

    target = r['price'] * (fair_pe / r['pe'])
    profit = (target - r['price']) / r['price'] * 100

    print(f"  合理PE: {fair_pe} → 目标价 ¥{target:.2f} (+{profit:.0f}%)")

    # 持有期
    if r['ytd'] < -30:
        period = "6-12个月"
    else:
        period = "3-6个月"

    print(f"  建议持有: {period} | 得分: {r['score']}")

print("\n" + "=" * 70)
print("免责声明：以上仅为数据分析结果，不构成投资建议")
print("=" * 70)
