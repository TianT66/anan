# -*- coding: utf-8 -*-
"""
全市场股票获取 - 新浪全量获取
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import re

def get_sina_stocks(page=1, num=1000):
    """从新浪获取股票列表"""
    url = f'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num={num}&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn/',
            'Accept': '*/*',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            content = resp.read().decode('gbk', errors='replace')
            data = json.loads(content)
            return data
    except Exception as e:
        return []

def get_sina_stocks_kcb(page=1, num=1000):
    """从新浪获取科创板股票"""
    url = f'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num={num}&sort=symbol&asc=1&node=kcb&symbol=&_s_r_a=page'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://finance.sina.com.cn/',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('gbk', errors='replace'))
    except:
        return []

def get_sina_stocks_bj(page=1, num=1000):
    """从新浪获取北交所"""
    url = f'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page={page}&num={num}&sort=symbol&asc=1&node=bj_a&symbol=&_s_r_a=page'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://finance.sina.com.cn/',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('gbk', errors='replace'))
    except:
        return []

print("=" * 80)
print("  全市场股票获取 - 新浪全量")
print("  2026-03-27 07:35")
print("=" * 80)

all_stocks = []

# 获取沪深A股
print("\n[1/3] 获取沪深A股...")
for page in range(1, 6):
    data = get_sina_stocks(page=page, num=1000)
    if not data:
        print(f"    第{page}页为空，停止")
        break
    
    for item in data:
        code = str(item.get('symbol', ''))
        name = item.get('name', '')
        
        try:
            price = float(item.get('trade', 0)) if item.get('trade') and item.get('trade') != '0.00' else 0
        except:
            price = 0
        try:
            change_pct = float(item.get('pricechange', 0)) if item.get('pricechange') else 0
        except:
            change_pct = 0
        try:
            pe = float(item.get('peratio', 0)) if item.get('peratio') and item.get('peratio') != '0' and item.get('peratio') != 'N/A' else -1
        except:
            pe = -1
        
        prefix = 'sh' if code.startswith('6') else 'sz'
        
        all_stocks.append({
            'code': code,
            'name': name,
            'price': price,
            'change_pct': change_pct,
            'pe': pe,
            'prefix': prefix,
            'market': '沪深主板',
        })
    
    print(f"    第{page}页: +{len(data)}只, 累计{len(all_stocks)}只")
    time.sleep(0.5)

# 获取科创板
print("\n[2/3] 获取科创板...")
kcb_count = len(all_stocks)
for page in range(1, 4):
    data = get_sina_stocks_kcb(page=page, num=1000)
    if not data:
        break
    
    for item in data:
        code = str(item.get('symbol', ''))
        name = item.get('name', '')
        try:
            price = float(item.get('trade', 0)) if item.get('trade') and item.get('trade') != '0.00' else 0
        except:
            price = 0
        try:
            change_pct = float(item.get('pricechange', 0)) if item.get('pricechange') else 0
        except:
            change_pct = 0
        try:
            pe = float(item.get('peratio', 0)) if item.get('peratio') and item.get('peratio') != '0' and item.get('peratio') != 'N/A' else -1
        except:
            pe = -1
        
        all_stocks.append({
            'code': code,
            'name': name,
            'price': price,
            'change_pct': change_pct,
            'pe': pe,
            'prefix': 'sh',
            'market': '科创板',
        })
    
    print(f"    第{page}页: +{len(data)}只")
    time.sleep(0.5)

print(f"  科创板: +{len(all_stocks)-kcb_count}只")

# 获取北交所
print("\n[3/3] 获取北交所...")
bj_start = len(all_stocks)
for page in range(1, 4):
    data = get_sina_stocks_bj(page=page, num=1000)
    if not data:
        break
    
    for item in data:
        code = str(item.get('symbol', ''))
        name = item.get('name', '')
        try:
            price = float(item.get('trade', 0)) if item.get('trade') and item.get('trade') != '0.00' else 0
        except:
            price = 0
        try:
            change_pct = float(item.get('pricechange', 0)) if item.get('pricechange') else 0
        except:
            change_pct = 0
        
        all_stocks.append({
            'code': code,
            'name': name,
            'price': price,
            'change_pct': change_pct,
            'pe': -1,
            'prefix': 'bj',
            'market': '北交所',
        })
    
    print(f"    第{page}页: +{len(data)}只")
    time.sleep(0.5)

print(f"  北交所: +{len(all_stocks)-bj_start}只")

print(f"\n\n{'='*80}")
print(f"  数据获取完成")
print(f"{'='*80}")
print(f"  沪深A股: {len([s for s in all_stocks if s['market'] == '沪深主板'])}只")
print(f"  科创板: {len([s for s in all_stocks if s['market'] == '科创板'])}只")
print(f"  北交所: {len([s for s in all_stocks if s['market'] == '北交所'])}只")
print(f"  总计: {len(all_stocks)}只")

# 去重
codes = set()
dedup = []
for s in all_stocks:
    key = f"{s['prefix']}{s['code']}"
    if key not in codes:
        codes.add(key)
        dedup.append(s)

print(f"  去重后: {len(dedup)}只")

# 统计
valid_price = len([s for s in dedup if s['price'] > 0])
valid_pe = len([s for s in dedup if s['pe'] and s['pe'] > 0])
valid_change = len([s for s in dedup if s['change_pct'] != 0])

print(f"  有价格数据: {valid_price}只")
print(f"  有PE数据: {valid_pe}只")
print(f"  有涨跌数据: {valid_change}只")

# 市值规模分布（通过价格*股本估算）
print(f"\n  前30只预览:")
for s in dedup[:30]:
    pe = f"{s['pe']:.1f}" if s['pe'] and s['pe'] > 0 else '-'
    pct = f"{s['change_pct']:.2f}%" if s['change_pct'] else '-'
    print(f"    {s['prefix']}{s['code']} {s['name']:<8} 现价:{s['price']:<8} 涨跌:{pct:<8} PE:{pe:<6} [{s['market']}]")

# 保存
save_path = r'C:\Users\12408\.qclaw\workspace\all_stocks_raw.json'
try:
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(dedup, f, ensure_ascii=False, indent=2)
    print(f"\n  已保存: {save_path}")
except Exception as e:
    print(f"  保存失败: {e}")
    # 尝试其他路径
    for alt in [r'C:\Users\12408\all_stocks.json', r'C:\all_stocks.json', r'D:\all_stocks.json']:
        try:
            with open(alt, 'w', encoding='utf-8') as f:
                json.dump(dedup, f, ensure_ascii=False)
            print(f"  已保存: {alt}")
            break
        except:
            continue

print(f"\n{'='*80}")
