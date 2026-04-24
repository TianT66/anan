# -*- coding: utf-8 -*-
"""
全市场股票获取 - 方案5
新浪/腾讯/网易 备用接口
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import re

def try_sina_stocklist():
    """从新浪获取股票列表"""
    stocks = []
    
    # 新浪财经股票列表页
    urls = [
        'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=1000&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page',
        'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=1000&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page',
    ]
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn/',
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode('gbk')
                # 解析JSON
                data = json.loads(content)
                for item in data:
                    code = str(item.get('symbol', ''))
                    name = item.get('name', '')
                    price = item.get('trade', 0) or 0
                    change_pct = item.get('pricechange', 0) or 0
                    pe = item.get('peratio', 0) or -1
                    
                    if code:
                        prefix = 'sh' if code.startswith('6') else 'sz'
                        stocks.append({
                            'code': code,
                            'name': name,
                            'price': float(price),
                            'change_pct': float(change_pct),
                            'pe': float(pe) if pe and pe != '0' else -1,
                            'prefix': prefix,
                        })
                print(f"  新浪获取: {len(data)}只")
                if len(stocks) > 1000:
                    break
                time.sleep(1)
        except Exception as e:
            print(f"  新浪失败: {e}")
    
    return stocks

def try_tencent_stocklist():
    """从腾讯获取股票列表"""
    stocks = []
    
    # 腾讯财经A股列表
    try:
        url = 'https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?apptype=&isrc=&count=1&_var=kline_dayqfq&param=sh000001,day,,,,,100,qfq&_=0'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://finance.qq.com/',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  腾讯测试: OK")
    except Exception as e:
        print(f"  腾讯测试: {e}")
    
    return stocks

def try_netease_list():
    """从网易获取列表"""
    stocks = []
    
    # 网易财经股票列表
    try:
        url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=STATUS:1&fields=SYMBOL,NAME,PRICE,PERCENT,PE,MARKET_CAPITAL,INDUSTRY&sort=PERCENT&order=desc&count=5000&type=query'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quotes.money.163.com/',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('list'):
                for item in data['list']:
                    code = str(item.get('SYMBOL', ''))
                    if code.startswith('6'):
                        prefix = 'sh'
                    elif code.startswith(('0', '3')):
                        prefix = 'sz'
                    else:
                        continue
                    stocks.append({
                        'code': code,
                        'name': item.get('NAME', ''),
                        'price': float(item.get('PRICE', 0)) or 0,
                        'change_pct': float(item.get('PERCENT', 0)) or 0,
                        'pe': float(item.get('PE', 0)) or -1,
                        'mkt_cap': float(item.get('MARKET_CAPITAL', 0)) or 0,
                        'industry': item.get('INDUSTRY', ''),
                        'prefix': prefix,
                    })
                print(f"  网易获取: {len(data['list'])}只")
    except Exception as e:
        print(f"  网易失败: {e}")
    
    return stocks

def try_bloomberg_style():
    """尝试彭博风格的接口"""
    stocks = []
    
    # 雪球接口
    try:
        url = 'https://stock.xueqiu.com/v5/stock/screener/quote/list.json?page=1&size=1000&order=desc&orderby=percent&order_by=percent&market=CN&type=sh_sz'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://xueqiu.com/',
            'Cookie': 'xq_a_token=placeholder',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list']:
                    code = str(item.get('symbol', '')).replace('SH', 'sh').replace('SZ', 'sz')
                    stocks.append({
                        'code': code.replace('sh', '').replace('sz', ''),
                        'name': item.get('name', ''),
                        'price': item.get('current', 0),
                        'change_pct': item.get('percent', 0),
                        'pe': item.get('pe_ttm', 0) or -1,
                        'pb': item.get('pb', 0) or -1,
                        'mkt_cap': item.get('market_capital', 0),
                        'dividend': item.get('dividend_yield', 0) or 0,
                        'prefix': 'sh' if code.startswith('sh') else 'sz',
                    })
                print(f"  雪球获取: {len(stocks)}只")
    except Exception as e:
        print(f"  雪球失败: {e}")
    
    return stocks

def try_jqdata():
    """聚宽数据"""
    stocks = []
    try:
        url = 'https://dataapi.joinquant.com/apis'
        # 这个需要API Key，先测试连通性
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"  聚宽测试: {resp.read().decode()[:100]}")
    except Exception as e:
        print(f"  聚宽失败: {e}")
    return stocks

print("=" * 80)
print("  全市场股票获取 - 多接口测试")
print("  2026-03-27 07:30")
print("=" * 80)

all_stocks = []

# 测试各接口
print("\n[1] 测试新浪...")
sina = try_sina_stocklist()
all_stocks.extend(sina)
print(f"  累计: {len(all_stocks)}只")

print("\n[2] 测试网易...")
netease = try_netease_list()
# 去重合并
existing = set(s['code'] for s in all_stocks)
for s in netease:
    if s['code'] not in existing:
        all_stocks.append(s)
        existing.add(s['code'])
print(f"  累计: {len(all_stocks)}只")

print("\n[3] 测试腾讯...")
tencent = try_tencent_stocklist()
all_stocks.extend(tencent)
print(f"  累计: {len(all_stocks)}只")

print("\n[4] 测试雪球...")
xueqiu = try_bloomberg_style()
existing = set(s['code'] for s in all_stocks)
for s in xueqiu:
    if s['code'] not in existing:
        all_stocks.append(s)
        existing.add(s['code'])
print(f"  累计: {len(all_stocks)}只")

print("\n[5] 测试聚宽...")
jqdata = try_jqdata()
all_stocks.extend(jqdata)

print(f"\n\n{'='*80}")
print(f"  最终结果")
print(f"{'='*80}")
print(f"  总共获取: {len(all_stocks)}只")

# 去重
codes = set()
dedup = []
for s in all_stocks:
    if s['code'] not in codes:
        codes.add(s['code'])
        dedup.append(s)

print(f"  去重后: {len(dedup)}只")

# 预览
valid_pe = len([s for s in dedup if s.get('pe', -1) > 0])
print(f"  有PE数据: {valid_pe}只")

if dedup:
    print(f"\n  前10只预览:")
    for s in dedup[:10]:
        pe = f"{s['pe']:.1f}" if s.get('pe', -1) > 0 else '-'
        print(f"    {s.get('prefix','')}{s['code']} {s['name']} 现价:{s['price']} PE:{pe}")

print(f"\n{'='*80}")
