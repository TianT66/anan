# -*- coding: utf-8 -*-
"""
全市场股票获取 - 新浪批量查价
构建全量股票代码 → 批量查价
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import re

# 全量A股代码列表 (人工整理的关键代码池，覆盖各行业龙头)
# 实际上我们无法自动获取全量5000+代码，但可以覆盖主要股票

def get_tencent_price(codes):
    """腾讯批量查价"""
    results = {}
    batch_size = 100
    
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        # 腾讯格式
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
                                volume = float(data[6]) if data[6] and data[6] != '-' else 0
                                pe = float(data[39]) if data[39] and data[39] != '-' and data[39] != 'N/A' and data[39] != '0' else -1
                                pb = float(data[46]) if data[46] and data[46] != '-' and data[46] != 'N/A' else -1
                                mkt_cap = float(data[44]) * 100000000 if data[44] and data[44] != '-' else 0
                                dividend = float(data[23]) if data[23] and data[23] != '-' else 0
                                roe = float(data[37]) if data[37] and data[37] != '-' else -1
                                name = data[1] if len(data) > 1 else ''
                                
                                change_pct = 0
                                if last_close > 0 and price > 0:
                                    change_pct = (price - last_close) / last_close * 100
                                
                                results[code] = {
                                    'name': name,
                                    'price': price,
                                    'last_close': last_close,
                                    'change_pct': change_pct,
                                    'high': high,
                                    'low': low,
                                    'volume': volume,
                                    'pe': pe,
                                    'pb': pb,
                                    'mkt_cap': mkt_cap,
                                    'dividend': dividend,
                                    'roe': roe,
                                }
                            except (ValueError, IndexError):
                                pass
            time.sleep(0.2)
        except Exception as e:
            print(f"    批次{i//batch_size+1}失败: {e}")
            time.sleep(1)
    
    return results

def get_sina_price(codes):
    """新浪批量查价"""
    results = {}
    batch_size = 80
    
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        code_str = ','.join([f'{"sh" if c.startswith(("6","5","9")) else "sz"}{c}' for c in batch])
        url = f'http://hq.sinajs.cn/list={code_str}'
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://finance.sina.com.cn/',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('gbk', errors='replace')
                
                for line in content.split('\n'):
                    match = re.search(r'hq_(\w+)="([^"]+)"', line)
                    if match:
                        raw = match.group(1)
                        code = raw.replace('sh', '').replace('sz', '')
                        parts = match.group(2).split(',')
                        
                        if len(parts) >= 10 and parts[0]:
                            try:
                                name = parts[0]
                                price = float(parts[3]) if parts[3] else 0
                                last_close = float(parts[2]) if parts[2] else 0
                                open_p = float(parts[1]) if parts[1] else 0
                                high = float(parts[4]) if parts[4] else 0
                                low = float(parts[5]) if parts[5] else 0
                                volume = float(parts[8]) if parts[8] else 0
                                
                                change_pct = 0
                                if last_close > 0:
                                    change_pct = (price - last_close) / last_close * 100
                                
                                results[code] = {
                                    'name': name,
                                    'price': price,
                                    'last_close': last_close,
                                    'change_pct': change_pct,
                                    'high': high,
                                    'low': low,
                                    'volume': volume,
                                }
                            except (ValueError, IndexError):
                                pass
            time.sleep(0.3)
        except Exception as e:
            print(f"    新浪批次{i//batch_size+1}失败: {e}")
            time.sleep(1)
    
    return results

# 构建全量代码池（主要A股，约4000+）
# 这里用已知的股票代码模式，覆盖各行业

def build_stock_pool():
    """构建全量股票代码池"""
    codes = []
    
    # 上交所主板 (600000-603999, 605000-605999)
    for i in range(600000, 604000):
        codes.append(f'{i}')
    for i in range(605000, 606000):
        codes.append(f'{i}')
    
    # 上交所科创板 (688000-688999)
    for i in range(688000, 689000):
        codes.append(f'{i}')
    
    # 深交所主板 (000000-001999, 002000-002999)
    for i in range(0, 2000):
        codes.append(f'{i:06d}')
    for i in range(2000, 3000):
        codes.append(f'{i:06d}')
    
    # 深交所创业板 (300000-300999)
    for i in range(300000, 301000):
        codes.append(f'{i}')
    
    # 北交所 (830000-839999, 870000-879999)
    for i in range(830000, 840000):
        codes.append(f'{i}')
    for i in range(870000, 880000):
        codes.append(f'{i}')
    
    return codes

print("=" * 80)
print("  全市场股票获取 - 腾讯批量查价")
print("  2026-03-27 07:45")
print("=" * 80)

print("\n[步骤1] 构建股票代码池...")
all_codes = build_stock_pool()
print(f"  代码池: {len(all_codes)}个代码")

print("\n[步骤2] 腾讯批量查价（分批，每批100只）...")
# 先测一小批看看能不能用
test_codes = all_codes[:500]
print(f"  测试前500只...")
test_prices = get_tencent_price(test_codes)
print(f"  测试结果: {len(test_prices)}只成功")

if len(test_prices) > 100:
    print(f"\n  测试预览（前20只）:")
    for code, info in list(test_prices.items())[:20]:
        pe = f"{info['pe']:.1f}" if info['pe'] and info['pe'] > 0 else '-'
        chg = f"{info['change_pct']:+.2f}%" if info['change_pct'] else '-'
        mkt = f"{info['mkt_cap']/100000000:.0f}亿" if info['mkt_cap'] > 0 else '-'
        print(f"    {code} {info['name']:<8} 现价:{info['price']:<8} 涨跌:{chg:<8} PE:{pe:<6} 市值:{mkt}")
    
    print(f"\n  继续获取全部{len(all_codes)}只...")
    all_prices = get_tencent_price(all_codes)
    print(f"  最终结果: {len(all_prices)}只成功")
    
    # 过滤有价格数据的
    valid = [s for s in all_prices.values() if s['price'] > 0]
    print(f"  有效数据: {len(valid)}只")
    
    # 统计
    valid_pe = len([s for s in valid if s.get('pe', -1) > 0])
    valid_pb = len([s for s in valid if s.get('pb', -1) > 0])
    valid_div = len([s for s in valid if s.get('dividend', 0) > 0])
    
    print(f"\n  数据覆盖:")
    print(f"    PE数据: {valid_pe}只")
    print(f"    PB数据: {valid_pb}只")
    print(f"    股息数据: {valid_div}只")
    
    # 市值分布
    large = len([s for s in valid if s.get('mkt_cap', 0) > 10000000000])
    mid = len([s for s in valid if 1000000000 < s.get('mkt_cap', 0) <= 10000000000])
    small = len([s for s in valid if 0 < s.get('mkt_cap', 0) <= 1000000000])
    print(f"\n  市值分布:")
    print(f"    大盘(>100亿): {large}只")
    print(f"    中盘(10-100亿): {mid}只")
    print(f"    小盘(<10亿): {small}只")
    
    # 保存
    save_path = r'C:\Users\12408\.qclaw\workspace\all_stocks_full.json'
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(valid, f, ensure_ascii=False)
        print(f"\n  已保存: {save_path}")
    except:
        print(f"  保存失败")
else:
    print(f"\n  腾讯接口被限流，无法获取足够数据")
    print(f"  尝试新浪备用...")
    sina_prices = get_sina_price(all_codes[:2000])
    print(f"  新浪结果: {len(sina_prices)}只")

print(f"\n{'='*80}")
