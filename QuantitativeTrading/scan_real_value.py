# -*- coding: utf-8 -*-
"""
真正价值股筛选 - 排除盈利下滑的假低估
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("真正价值股筛选 - 鉴别真假低估")
print("=" * 70)

# 获取全市场数据
print("[1/3] 获取全市场数据...")
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

# 分析
print("\n[2/3] 深度财务分析...")
results = []
sample = df_valid.nsmallest(150, '市盈率-动态')

for idx, row in sample.iterrows():
    code = row['代码']
    name = row['名称']
    pe = row['市盈率-动态']
    pb = row['市净率']
    price = row['最新价']
    change = row['涨跌幅']
    ytd = row['年初至今涨跌幅'] if pd.notna(row['年初至今涨跌幅']) else 0

    # 排除银行和受损行业
    if any(k in name for k in ['银行']):
        continue
    if any(k in name for k in ['航空', '旅游', '酒店']):
        continue

    try:
        fin = ak.stock_financial_analysis_indicator(symbol=code, start_year="2023")
        if fin is not None and len(fin) >= 4:
            roe_col = '净资产收益率(%)'
            if roe_col in fin.columns:
                roe_vals = fin[roe_col].dropna().tolist()
                if len(roe_vals) >= 4 and roe_vals[0] > 0:
                    latest_roe = roe_vals[0]
                    avg_roe = sum(roe_vals[1:4]) / 3
                    if avg_roe > 0:
                        roe_change = (latest_roe - avg_roe) / avg_roe
                        # ROE稳定或小幅下滑
                        if roe_change > -0.25:
                            results.append({
                                'code': code, 'name': name, 'price': price,
                                'pe': pe, 'pb': pb, 'change': change,
                                'ytd': ytd, 'roe': latest_roe, 'roe_change': roe_change
                            })
    except:
        pass
    time.sleep(0.3)

print(f"    找到 {len(results)} 只盈利稳定的标的")

# 评分
print("\n[3/3] 综合评分...")
for r in results:
    score = 0
    if r['pe'] < 15:
        score += 30
    elif r['pe'] < 20:
        score += 20
    if r['roe_change'] > 0:
        score += 25
    elif r['roe_change'] > -0.1:
        score += 15
    if r['ytd'] < -30:
        score += 20
    elif r['ytd'] < -20:
        score += 15
    if r['change'] < -5:
        score += 15
    elif r['change'] < -3:
        score += 10
    if any(k in r['name'] for k in ['医药', '医疗', '消费']):
        score += 10
    r['score'] = score

results.sort(key=lambda x: x['score'], reverse=True)

# 输出
print("\n" + "=" * 70)
print("【真正有价值的低估标的】")
print("=" * 70)

for i, r in enumerate(results[:20], 1):
    status = "^" if r['roe_change'] > 0 else "->" if r['roe_change'] > -0.1 else "v"
    print(f"\n{i:2d}. {r['name']}({r['code']})")
    print(f"    价格: {r['price']:.2f} | PE: {r['pe']:.1f} | PB: {r['pb']:.2f}")
    print(f"    今日: {r['change']:+.2f}% | 年初至今: {r['ytd']:+.1f}%")
    print(f"    ROE: {r['roe']:.1f}% ({status}) | 得分: {r['score']}")

# TOP5深度分析
print("\n" + "=" * 70)
print("【TOP 5 深度分析】")
print("=" * 70)

for i, r in enumerate(results[:5], 1):
    print(f"\n{i}. {r['name']}({r['code']})")
    print("-" * 50)
    
    # 估值
    val = "极低" if r['pe'] < 15 else "较低" if r['pe'] < 20 else "合理"
    print(f"  估值: PE={r['pe']:.1f}({val}) PB={r['pb']:.2f}")
    
    # ROE
    print(f"  ROE: {r['roe']:.1f}% (变化: {r['roe_change']:+.1%})")
    
    # 错杀原因
    if r['ytd'] < -30:
        reason = "年初至今跌幅超30%，可能被误解"
    elif r['change'] < -5:
        reason = "今日大跌，战争恐慌被错杀"
    else:
        reason = "估值低+盈利稳定"
    print(f"  错杀原因: {reason}")
    
    # 行业
    sector = "其他"
    if any(k in r['name'] for k in ['医药', '医疗']):
        sector = "医药"
    elif any(k in r['name'] for k in ['食品', '饮料']):
        sector = "消费"
    elif any(k in r['name'] for k in ['科技', '电子']):
        sector = "科技"
    print(f"  行业: {sector}")
    
    # 翻倍潜力
    if r['pe'] < 15 and r['roe'] > 10 and r['ytd'] < -20:
        potential = "极高"
        reason2 = "估值极低+ROE高+超跌"
    elif r['pe'] < 20 and r['roe'] > 5:
        potential = "高"
        reason2 = "估值低+盈利稳定"
    else:
        potential = "中等"
        reason2 = "需要催化剂"
    print(f"  翻倍潜力: {potential} ({reason2})")
    
    # 目标价
    fair_pe = 15 if r['roe'] > 10 else 12 if r['roe'] > 5 else 10
    target = r['price'] * (fair_pe / r['pe'])
    profit = (target - r['price']) / r['price'] * 100
    print(f"  目标价: {target:.2f} (+{profit:.0f}%)")
    
    # 持有期
    period = "6-12个月" if r['ytd'] < -30 else "3-6个月"
    print(f"  持有期: {period}")

print("\n" + "=" * 70)
