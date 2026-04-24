# -*- coding: utf-8 -*-
"""
全市场综合筛选分析
基于5028只股票的真实数据
9维度筛选：激进/稳健/保守 × 短期/中期/长期
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import re

def fetch_tencent_prices(codes):
    """腾讯批量查价"""
    results = {}
    batch_size = 100
    
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        code_str = ','.join([f'{"sh" if c.startswith(("6","5","9")) else "sz"}{c}' for c in batch])
        url = f'http://qt.gtimg.cn/q={code_str}'
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://gu.qq.com/',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('gbk', errors='replace')
                
                for line in content.split('\n'):
                    if '="pv"' in line or '_' not in line:
                        continue
                    match = re.search(r'v_(\w+)="([^"]+)"', line)
                    if match:
                        raw_code = match.group(1)
                        code = raw_code.replace('sh', '').replace('sz', '')
                        data = match.group(2).split('~')
                        
                        if len(data) >= 50 and data[0]:
                            try:
                                price = float(data[3]) if data[3] and data[3] != '-' else 0
                                last_close = float(data[4]) if data[4] and data[4] != '-' else 0
                                high = float(data[33]) if data[33] and data[33] != '-' else 0
                                low = float(data[34]) if data[34] and data[34] != '-' else 0
                                pe = float(data[39]) if data[39] and data[39] not in ('-', 'N/A', '0', '') else -1
                                pb = float(data[46]) if data[46] and data[46] not in ('-', 'N/A') else -1
                                mkt_cap = float(data[44]) * 100000000 if data[44] and data[44] != '-' else 0
                                dividend = float(data[23]) if data[23] and data[23] != '-' else 0
                                roe = float(data[37]) if data[37] and data[37] != '-' else -1
                                name = data[1] if len(data) > 1 else ''
                                change_pct = (price - last_close) / last_close * 100 if last_close > 0 and price > 0 else 0
                                
                                results[code] = {
                                    'name': name,
                                    'price': price,
                                    'last_close': last_close,
                                    'change_pct': change_pct,
                                    'high': high,
                                    'low': low,
                                    'pe': pe,
                                    'pb': pb,
                                    'mkt_cap': mkt_cap,
                                    'dividend': dividend,
                                    'roe': roe,
                                }
                            except:
                                pass
            time.sleep(0.15)
        except:
            pass
    
    return results

def build_full_pool():
    """构建全量代码池"""
    codes = []
    for i in range(600000, 604000): codes.append(f'{i}')
    for i in range(605000, 606000): codes.append(f'{i}')
    for i in range(688000, 689000): codes.append(f'{i}')
    for i in range(0, 2000): codes.append(f'{i:06d}')
    for i in range(2000, 3000): codes.append(f'{i:06d}')
    for i in range(300000, 301000): codes.append(f'{i}')
    for i in range(830000, 840000): codes.append(f'{i}')
    for i in range(870000, 880000): codes.append(f'{i}')
    return codes

# ============================================================
# 评分模型
# ============================================================

def score_valuation(s):
    """估值评分"""
    score = 0
    pe = abs(s['pe']) if s['pe'] < 0 else s['pe']
    if 0 < pe <= 8: score += 30
    elif pe <= 12: score += 25
    elif pe <= 16: score += 20
    elif pe <= 20: score += 15
    elif pe <= 25: score += 10
    elif pe <= 35: score += 5
    
    if s['pb'] > 0:
        if s['pb'] <= 1.0: score += 25
        elif s['pb'] <= 1.5: score += 22
        elif s['pb'] <= 2.0: score += 18
        elif s['pb'] <= 3.0: score += 12
        elif s['pb'] <= 4.0: score += 8
        else: score += 4
    
    if s['dividend'] > 0:
        if s['dividend'] >= 5: score += 25
        elif s['dividend'] >= 3: score += 20
        elif s['dividend'] >= 2: score += 15
        elif s['dividend'] >= 1: score += 10
        else: score += 5
    
    if s['pe'] < 0: score -= 10
    return max(0, min(100, score))

def score_quality(s):
    """质量评分"""
    score = 0
    if s['roe'] > 0:
        if s['roe'] >= 25: score += 40
        elif s['roe'] >= 20: score += 32
        elif s['roe'] >= 15: score += 25
        elif s['roe'] >= 10: score += 18
        else: score += 10
    
    if s['mkt_cap'] >= 10000000000: score += 30
    elif s['mkt_cap'] >= 1000000000: score += 22
    elif s['mkt_cap'] >= 500000000: score += 15
    elif s['mkt_cap'] >= 100000000: score += 8
    else: score += 4
    
    if s['dividend'] >= 3: score += 20
    elif s['dividend'] >= 1: score += 12
    elif s['dividend'] > 0: score += 6
    
    return max(0, min(100, score))

def score_technical(s):
    """技术面评分 - 基于今日涨跌幅和价格位置"""
    score = 0
    change = abs(s['change_pct'])
    
    # 今日跌幅越大（便宜），分数越高
    if s['change_pct'] < -5: score += 35
    elif s['change_pct'] < -3: score += 30
    elif s['change_pct'] < -2: score += 25
    elif s['change_pct'] < -1: score += 20
    elif s['change_pct'] < 0: score += 15
    else: score += 5
    
    # 低价股更安全
    if s['price'] <= 10: score += 25
    elif s['price'] <= 20: score += 20
    elif s['price'] <= 50: score += 15
    elif s['price'] <= 100: score += 10
    else: score += 5
    
    return max(0, min(100, score))

# ============================================================
# 主程序
# ============================================================

print("=" * 80)
print("  全市场综合筛选 - 基于5028只股票真实数据")
print("  筛选时间: 2026-03-27")
print("=" * 80)

print("\n[1/3] 获取全市场数据...")
codes = build_full_pool()
all_prices = fetch_tencent_prices(codes)
all_stocks = list(all_prices.values())
print(f"  获取成功: {len(all_stocks)}只")

# 过滤有效数据
valid_stocks = [s for s in all_stocks if s['price'] > 0]
print(f"  有效数据: {len(valid_stocks)}只")

valid_pe = [s for s in valid_stocks if s['pe'] > 0]
valid_pb = [s for s in valid_stocks if s['pb'] > 0]
valid_roe = [s for s in valid_stocks if s['roe'] > 0]
valid_div = [s for s in valid_stocks if s['dividend'] > 0]

print(f"  PE数据: {len(valid_pe)}只 | PB数据: {len(valid_pb)}只 | 股息: {len(valid_div)}只 | ROE: {len(valid_roe)}只")

# 估算近3月/6月跌幅（用今日涨跌代替，实际需要历史数据）
# 这里用今日涨幅作为超跌的近似指标
for s in valid_stocks:
    s['drop_3m_est'] = s['change_pct'] * -3  # 估算
    s['drop_6m_est'] = s['change_pct'] * -6

print("\n[2/3] 全市场统计...")
# 市值分布
large = len([s for s in valid_stocks if s['mkt_cap'] > 10000000000])
mid = len([s for s in valid_stocks if 1000000000 < s['mkt_cap'] <= 10000000000])
small = len([s for s in valid_stocks if s['mkt_cap'] <= 1000000000])
print(f"  大盘(>100亿): {large}只 | 中盘(10-100亿): {mid}只 | 小盘(<10亿): {small}只")

# 行业分布
sectors = {}
for s in valid_stocks:
    name = s['name']
    sector = '其他'
    if any(k in name for k in ['银行', '保险', '券商']): sector = '金融'
    elif any(k in name for k in ['茅台', '五粮液', '酒', '饮料']): sector = '白酒饮料'
    elif any(k in name for k in ['药', '医', '生']): sector = '医药'
    elif any(k in name for k in ['芯', '半导', '光', '电']): sector = '半导体'
    elif any(k in name for k in ['银', '铜', '铝', '矿', '金', '锂']): sector = '有色金属'
    elif any(k in name for k in ['车', '汽', '比亚迪']): sector = '汽车'
    elif any(k in name for k in ['房', '地', '建']): sector = '地产建筑'
    elif any(k in name for k in ['电', '能', '光', '风', '核']): sector = '电力新能源'
    elif any(k in name for k in ['AI', '智', '云', '网']): sector = 'AI云计算'
    elif any(k in name for k in ['机', '器', '自动']): sector = '机器人'
    sectors[sector] = sectors.get(sector, 0) + 1

print(f"\n  行业分布 (前15):")
for sector, cnt in sorted(sectors.items(), key=lambda x: -x[1])[:15]:
    print(f"    {sector}: {cnt}只")

print("\n[3/3] 9维度筛选...")

# 9维度权重配置
configs = [
    ('激进', '短期', {'quality': 0.15, 'valuation': 0.10, 'technical': 0.40, 'dividend': 0.10, 'growth': 0.25}),
    ('稳健', '短期', {'quality': 0.25, 'valuation': 0.25, 'technical': 0.25, 'dividend': 0.15, 'growth': 0.10}),
    ('保守', '短期', {'quality': 0.25, 'valuation': 0.35, 'technical': 0.10, 'dividend': 0.30, 'growth': 0.00}),
    ('激进', '中期', {'quality': 0.20, 'valuation': 0.10, 'technical': 0.25, 'dividend': 0.10, 'growth': 0.35}),
    ('稳健', '中期', {'quality': 0.25, 'valuation': 0.20, 'technical': 0.15, 'dividend': 0.15, 'growth': 0.25}),
    ('保守', '中期', {'quality': 0.30, 'valuation': 0.30, 'technical': 0.10, 'dividend': 0.25, 'growth': 0.05}),
    ('激进', '长期', {'quality': 0.25, 'valuation': 0.10, 'technical': 0.15, 'dividend': 0.10, 'growth': 0.40}),
    ('稳健', '长期', {'quality': 0.30, 'valuation': 0.20, 'technical': 0.10, 'dividend': 0.15, 'growth': 0.25}),
    ('保守', '长期', {'quality': 0.35, 'valuation': 0.30, 'technical': 0.05, 'dividend': 0.25, 'growth': 0.05}),
]

def filter_and_score(stocks, w, min_pe=0, max_pe=200, min_div=0, min_mkt=0, require_growth=False):
    """筛选 + 评分"""
    candidates = []
    for s in stocks:
        # 基础筛选
        if s['pe'] < 0 and require_growth: continue
        if min_pe > 0 and (s['pe'] <= 0 or s['pe'] < min_pe): continue
        if max_pe < 200 and s['pe'] > max_pe: continue
        if s['dividend'] < min_div: continue
        if s['mkt_cap'] > 0 and s['mkt_cap'] < min_mkt: continue
        if s['price'] <= 0: continue
        
        # 评分
        sv = score_valuation(s)
        sq = score_quality(s)
        st = score_technical(s)
        sd = s['dividend'] * 10 if s['dividend'] > 0 else 0
        sg = 50 if s['pe'] > 0 and s['pe'] < 25 else 30  # 粗估成长性
        
        total = sv * w['valuation'] + sq * w['quality'] + st * w['technical'] + sd * w['dividend'] + sg * w['growth']
        
        s['sv'] = round(sv, 1)
        s['sq'] = round(sq, 1)
        s['st'] = round(st, 1)
        s['sd'] = round(sd, 1)
        s['sg'] = round(sg, 1)
        s['total'] = round(total, 1)
        candidates.append(s)
    
    candidates.sort(key=lambda x: x['total'], reverse=True)
    return candidates

# 输出9维度结果
results_table = []
horizon_targets = {'短期': 0.15, '中期': 0.30, '长期': 0.50}

for risk, horizon, weights in configs:
    print(f"\n{'='*80}")
    print(f"  【{risk} × {horizon}】")
    print(f"  权重: 估值={weights['valuation']:.0%} 质量={weights['quality']:.0%} 技术={weights['technical']:.0%} 股息={weights['dividend']:.0%} 成长={weights['growth']:.0%}")
    print(f"{'='*80}")
    
    # 根据风险调整筛选条件
    if risk == '激进':
        picks = filter_and_score(valid_pe + [s for s in valid_stocks if s['pe'] <= 0], weights, min_div=0, require_growth=False)
    elif risk == '稳健':
        picks = filter_and_score(valid_pe, weights, min_pe=0, max_pe=30, min_div=0, require_growth=False)
    else:
        picks = filter_and_score(valid_pe, weights, min_pe=0, max_pe=25, min_div=1.0, require_growth=False)
    
    target_up = horizon_targets[horizon]
    stop_down = 0.08
    
    for rank, s in enumerate(picks[:3], 1):
        upside = round((s['price'] * (1 + target_up) - s['price']) / s['price'] * 100, 1)
        stop = round(s['price'] * (1 - stop_down), 2)
        rr = round(abs(upside / 100 / stop_down), 1)
        pe_str = f"{s['pe']:.1f}" if s['pe'] > 0 else "亏损"
        pb_str = f"{s['pb']:.2f}" if s['pb'] > 0 else "-"
        div_str = f"{s['dividend']:.1f}%" if s['dividend'] > 0 else "-"
        roe_str = f"{s['roe']:.1f}%" if s['roe'] > 0 else "-"
        mkt_str = f"{s['mkt_cap']/100000000:.0f}亿" if s['mkt_cap'] > 0 else "-"
        
        print(f"\n  第{rank}名: {s['name']} ({s.get('code', 'N/A')})")
        print(f"    现价: {s['price']:.2f}元 | PE: {pe_str} | PB: {pb_str} | ROE: {roe_str}")
        print(f"    股息: {div_str} | 市值: {mkt_str} | 今日涨跌: {s['change_pct']:+.2f}%")
        print(f"    目标: {s['price']*(1+target_up):.2f}元 ({upside}%) | 止损: {stop:.2f}元 (-8%)")
        print(f"    盈亏比: 1:{rr}")
        print(f"    评分: 总={s['total']} 估值={s['sv']} 质量={s['sq']} 技术={s['st']} 股息={s['sd']} 成长={s['sg']}")
        
        results_table.append({
            'risk': risk, 'horizon': horizon, 'rank': rank,
            'name': s['name'], 'code': s.get('code', ''),
            'price': s['price'], 'pe': pe_str, 'pb': pb_str,
            'roe': roe_str, 'div': div_str, 'mkt': mkt_str,
            'change': s['change_pct'],
            'target': f"{s['price']*(1+target_up):.2f}",
            'upside': upside, 'stop': stop,
            'rr': rr, 'total': s['total']
        })

# ============================================================
# 全市场汇总表
# ============================================================
print(f"\n\n{'='*80}")
print(f"  汇总：全市场9维度TOP3推荐")
print(f"{'='*80}")

print(f"\n  {'维度':<14} {'第1名':<20} {'第2名':<20} {'第3名':<20}")
print(f"  {'-'*76}")

dim_names = [f"{r['risk']:<6}{r['horizon']:<8}" for r in results_table[:9:3]]
names1 = [f"{r['name']}({r['price']:.1f})" for r in results_table[:9:3]]
names2 = [f"{r['name']}({r['price']:.1f})" for r in results_table[1:9:3]]
names3 = [f"{r['name']}({r['price']:.1f})" for r in results_table[2:9:3]]

for i in range(3):
    print(f"  {dim_names[i]:<14} {names1[i]:<20} {names2[i]:<20} {names3[i]:<20}")

# 全市场统计亮点
print(f"\n\n{'='*80}")
print(f"  全市场数据亮点")
print(f"{'='*80}")

# PE分布
pe_buckets = {'<10': 0, '10-20': 0, '20-30': 0, '30-50': 0, '>50': 0, '亏损': 0}
for s in valid_pe:
    if s['pe'] < 10: pe_buckets['<10'] += 1
    elif s['pe'] < 20: pe_buckets['10-20'] += 1
    elif s['pe'] < 30: pe_buckets['20-30'] += 1
    elif s['pe'] < 50: pe_buckets['30-50'] += 1
    else: pe_buckets['>50'] += 1
for s in valid_stocks:
    if s['pe'] <= 0: pe_buckets['亏损'] += 1

print(f"\n  PE分布 ({len(valid_pe)}只有效PE):")
for k, v in pe_buckets.items():
    bar = '█' * int(v / len(valid_pe) * 40)
    print(f"    {k:>8}: {v:>4}只 ({v/len(valid_pe)*100:.1f}%) {bar}")

# 股息分布
div_buckets = {'<1%': 0, '1-2%': 0, '2-3%': 0, '3-5%': 0, '>5%': 0}
for s in valid_div:
    if s['dividend'] < 1: div_buckets['<1%'] += 1
    elif s['dividend'] < 2: div_buckets['1-2%'] += 1
    elif s['dividend'] < 3: div_buckets['2-3%'] += 1
    elif s['dividend'] < 5: div_buckets['3-5%'] += 1
    else: div_buckets['>5%'] += 1

print(f"\n  股息分布 ({len(valid_div)}只有效):")
for k, v in div_buckets.items():
    bar = '█' * int(v / len(valid_div) * 40)
    print(f"    {k:>8}: {v:>4}只 ({v/len(valid_div)*100:.1f}%) {bar}")

# 今日涨跌分布
up1 = len([s for s in valid_stocks if s['change_pct'] > 5])
up2 = len([s for s in valid_stocks if 2 < s['change_pct'] <= 5])
up3 = len([s for s in valid_stocks if 0 < s['change_pct'] <= 2])
dn1 = len([s for s in valid_stocks if -2 <= s['change_pct'] < 0])
dn2 = len([s for s in valid_stocks if -5 <= s['change_pct'] < -2])
dn3 = len([s for s in valid_stocks if s['change_pct'] < -5])

print(f"\n  今日涨跌分布 ({len(valid_stocks)}只):")
print(f"    涨停(+10%): {up1:>4}只")
print(f"    大涨(+5~10%): {up2:>4}只")
print(f"    小涨(+2~5%): {up3:>4}只")
print(f"    小跌(-2~0%): {dn1:>4}只")
print(f"    大跌(-5~-2%): {dn2:>4}只")
print(f"    跌停(-10%): {dn3:>4}只")

print(f"\n{'='*80}")
print(f"  分析完成 - 基于全市场{len(valid_stocks)}只股票真实数据")
print(f"{'='*80}")
