# -*- coding: utf-8 -*-
"""
全市场股票获取 - 方案2
1. 从东方财富获取股票列表（含代码）
2. 从新浪批量获取实时价格
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import re

def get_stock_list_from_netease():
    """从网易获取股票列表"""
    stocks = []
    # 网易股票接口 - 沪深A股
    for market in ['sh', 'sz', 'bj']:
        print(f"  正在获取{market.upper()}股票列表...")
        try:
            # 网易财经股票列表接口
            if market == 'sh':
                url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=STATUS:1;EXCHANGE:1&fields=SYMBOL,NAME,PRICE,PERCENT,UPDOWN,FIVE_MINUTE_OPEN,OPEN,YESTERDAY_CLOSE_PRICE,HIGH,LOW,VOLUME,TURNOVER,PE,MARKET_CAPITAL,LIMIT_UP,LIMIT_DOWN,INDUSTRY,INDUSTRY_CLASS,HAS_DETAILS,ALLOW_DATABASE_STAMP,NEW_PE_PS&sort=PERCENT&order=desc&count=5000&type=query'
            elif market == 'sz':
                url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=STATUS:1;EXCHANGE:0&fields=SYMBOL,NAME,PRICE,PERCENT,UPDOWN,FIVE_MINUTE_OPEN,OPEN,YESTERDAY_CLOSE_PRICE,HIGH,LOW,VOLUME,TURNOVER,PE,MARKET_CAPITAL,LIMIT_UP,LIMIT_DOWN,INDUSTRY,INDUSTRY_CLASS,HAS_DETAILS,ALLOW_DATABASE_STAMP,NEW_PE_PS&sort=PERCENT&order=desc&count=5000&type=query'
            else:
                url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=STATUS:1;EXCHANGE:2&fields=SYMBOL,NAME,PRICE,PERCENT,UPDOWN,FIVE_MINUTE_OPEN,OPEN,YESTERDAY_CLOSE_PRICE,HIGH,LOW,VOLUME,TURNOVER,PE,MARKET_CAPITAL,LIMIT_UP,LIMIT_DOWN,INDUSTRY,INDUSTRY_CLASS,HAS_DETAILS,ALLOW_DATABASE_STAMP,NEW_PE_PS&sort=PERCENT&order=desc&count=5000&type=query'
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quotes.money.163.com/'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('list'):
                    for item in data['list']:
                        code = str(item.get('SYMBOL', ''))
                        if code.startswith('6'):
                            prefix = 'sh'
                        elif code.startswith(('0','3')):
                            prefix = 'sz'
                        elif code.startswith('4','8'):
                            prefix = 'bj'
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
                    print(f"    获取到{len(data['list'])}只")
                time.sleep(1)
        except Exception as e:
            print(f"    失败: {e}")
            continue
    return stocks

def get_prices_from_sina_batch(prefixed_codes):
    """从新浪批量获取价格（每批100个）"""
    results = {}
    batch_size = 80
    
    for i in range(0, len(prefixed_codes), batch_size):
        batch = prefixed_codes[i:i+batch_size]
        code_str = ','.join(batch)
        url = f'http://hq.sinajs.cn/list={code_str}'
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://finance.sina.com.cn/',
                'Accept': '*/*',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('gbk', errors='replace')
                # 解析
                for line in content.split('\n'):
                    match = re.search(r'hq_(\w+)="([^"]+)"', line)
                    if match:
                        code = match.group(1)
                        data = match.group(2).split(',')
                        if len(data) >= 10 and data[0]:
                            try:
                                results[code] = {
                                    'name': data[0],
                                    'price': float(data[3]) if data[3] else 0,
                                    'last_close': float(data[2]) if data[2] else 0,
                                    'open': float(data[1]) if data[1] else 0,
                                    'high': float(data[4]) if data[4] else 0,
                                    'low': float(data[5]) if data[5] else 0,
                                    'volume': float(data[8]) if data[8] else 0,
                                    'amount': float(data[9]) if data[9] else 0,
                                }
                            except:
                                pass
            time.sleep(0.3)
        except Exception as e:
            print(f"    批次{i//batch_size+1}失败: {e}")
            time.sleep(1)
            continue
    
    return results

def get_pe_from_tencent(prefixed_codes):
    """从腾讯获取PE等财务数据（每批50个）"""
    results = {}
    batch_size = 50
    
    for i in range(0, len(prefixed_codes), batch_size):
        batch = prefixed_codes[i:i+batch_size]
        code_str = ','.join(batch)
        url = f'http://qt.gtimg.cn/q={code_str}'
        
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://gu.qq.com/',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('gbk', errors='replace')
                for line in content.split('\n'):
                    match = re.search(r'v_(\w+)="([^"]+)"', line)
                    if match:
                        code = match.group(1).replace('sh', '').replace('sz', '')
                        data = match.group(2).split('~')
                        if len(data) >= 50:
                            try:
                                results[code] = {
                                    'pe': float(data[39]) if data[39] and data[39] != '-' else -1,
                                    'pb': float(data[46]) if data[46] and data[46] != '-' else -1,
                                    'dividend': float(data[23]) if data[23] and data[23] != '-' else 0,
                                    'mkt_cap': float(data[44]) * 100000000 if data[44] and data[44] != '-' else 0,
                                    'roe': float(data[37]) if data[37] and data[37] != '-' else -1,
                                }
                            except:
                                pass
            time.sleep(0.3)
        except Exception as e:
            time.sleep(1)
            continue
    
    return results

print("=" * 80)
print("  全市场股票数据获取 - 方案2")
print("  2026-03-27 07:20")
print("=" * 80)

print("\n[步骤1] 从网易获取股票列表...")
stock_list = get_stock_list_from_netease()
print(f"\n  网易获取: {len(stock_list)}只")

if len(stock_list) < 1000:
    print("\n  网易接口失败，尝试腾讯...")
    # 备用：从腾讯获取列表
    try:
        url = 'http://stockapp.finance.qq.com/mstats/#mod=list&id=hs_boards&module=MC&type=10'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"  腾讯获取: {len(data.get('data', {}).get('symbols', []))}只")
    except Exception as e:
        print(f"  腾讯也失败: {e}")

print("\n[步骤2] 新浪批量获取实时价格...")
if stock_list:
    prefixed = [f"{s['prefix']}{s['code']}" for s in stock_list[:5000]]
    print(f"  正在获取{len(prefixed)}只股票价格...")
    prices = get_prices_from_sina_batch(prefixed)
    print(f"  成功获取: {len(prices)}只")

print("\n[步骤3] 腾讯获取财务数据...")
if stock_list:
    prefixed = [f"{s['prefix']}{s['code']}" for s in stock_list[:3000]]
    print(f"  正在获取{len(prefixed)}只财务数据...")
    financials = get_pe_from_tencent(prefixed)
    print(f"  成功获取: {len(financials)}只")

print("\n" + "=" * 80)
print("  数据获取完成")
print(f"  股票列表: {len(stock_list)}只")
print("=" * 80)
