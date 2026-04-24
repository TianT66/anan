# -*- coding: utf-8 -*-
"""
全市场股票数据获取
尝试多种数据源，确保获取完整数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import os

def try_eastmoney_all(page=1, pz=100):
    """东方财富全市场接口"""
    # 沪深京A股全市场
    url = (
        f'http://push2.eastmoney.com/api/qt/clist/get'
        f'?pn={page}&pz={pz}&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281'
        f'&fltt=2&invt=2&fid=f3&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23'
        f'&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f45,f38'
    )
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://quote.eastmoney.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

def try_sina_batch(codes):
    """新浪批量接口"""
    code_str = ','.join(codes)
    url = f'http://hq.sinajs.cn/list={code_str}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://finance.sina.com.cn/'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('gbk', errors='replace')
    except Exception as e:
        return f'error:{e}'

def try_tencent_batch(codes):
    """腾讯批量接口"""
    code_str = ','.join([f'{"sh" if c.startswith(("6","5")) else "sz"}{c}' for c in codes])
    url = f'http://qt.gtimg.cn/q={code_str}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://gu.qq.com/'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('gbk', errors='replace')
    except Exception as e:
        return f'error:{e}'

print("=" * 80)
print("  全市场股票数据获取")
print("  2026-03-27 07:15")
print("=" * 80)

# 方案1：东方财富全市场接口（每页500条）
print("\n[1/3] 尝试东方财富全市场接口（每页500条）...")
success_count = 0
all_stocks = []

for page in range(1, 15):  # 最多14页，约7000条
    result = try_eastmoney_all(page=page, pz=500)
    
    if 'error' in result:
        print(f"  第{page}页失败: {result['error']}")
        time.sleep(2)
        if page > 3:  # 如果前几页都失败了，可能接口被限制
            continue
        break
    
    if result.get('data') and result['data'].get('diff'):
        stocks = result['data']['diff']
        if not stocks:
            print(f"  第{page}页为空，停止")
            break
        
        for s in stocks:
            code = str(s.get('f12', ''))
            name = s.get('f14', '')
            if not code or not name:
                continue
            
            price = s.get('f2', 0)
            change_pct = s.get('f3', 0)
            high = s.get('f15', 0)
            low = s.get('f16', 0)
            volume = s.get('f5', 0)  # 手
            amount = s.get('f6', 0)  # 元
            pe = s.get('f9', 0)
            pb = s.get('f23', 0)
            mkt_cap = s.get('f20', 0)  # 总市值
            flow_cap = s.get('f21', 0)  # 流通市值
            dividend = s.get('f116', 0)  # 股息率
            roe = s.get('f37', 0)  # ROE
            
            all_stocks.append({
                'code': code,
                'name': name,
                'price': float(price) if price and price != '-' else 0,
                'change_pct': float(change_pct) if change_pct and change_pct != '-' else 0,
                'high': float(high) if high and high != '-' else 0,
                'low': float(low) if low and low != '-' else 0,
                'volume': float(volume) if volume and volume != '-' else 0,
                'amount': float(amount) if amount and amount != '-' else 0,
                'pe': float(pe) if pe and pe != '-' and pe != 0 else -1,
                'pb': float(pb) if pb and pb != '-' and pb != 0 else -1,
                'mkt_cap': float(mkt_cap) if mkt_cap else 0,
                'flow_cap': float(flow_cap) if flow_cap else 0,
                'dividend': float(dividend) if dividend and dividend != '-' else 0,
                'roe': float(roe) if roe and roe != '-' else -1,
            })
        
        total = result['data'].get('total', len(all_stocks))
        success_count += len(stocks)
        print(f"  第{page}页: +{len(stocks)}只, 累计: {success_count}只 (总计约{total})")
        time.sleep(0.5)
    else:
        print(f"  第{page}页无数据")
        break

print(f"\n  东方财富接口获取: {len(all_stocks)}只")

if len(all_stocks) < 3000:
    print("\n[2/3] 东方财富数据不足，尝试补充...")
    # 补充：按交易所分别获取
    exchanges = [
        ('sh', '上证主板'),
        ('sz', '深圳主板'),
        ('bj', '北交所'),
    ]
    
    extra_count = 0
    for prefix, name in exchanges:
        print(f"  尝试获取{name}...")
        for page in range(1, 20):
            url = (
                f'http://push2.eastmoney.com/api/qt/clist/get'
                f'?pn={page}&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281'
                f'&fltt=2&invt=2&fid=f3&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80'
                f'&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25'
            )
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'http://quote.eastmoney.com/'
                })
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if data.get('data') and data['data'].get('diff'):
                        stocks = data['data']['diff']
                        for s in stocks:
                            code = str(s.get('f12', ''))
                            if not any(st['code'] == code for st in all_stocks):
                                all_stocks.append({
                                    'code': code,
                                    'name': s.get('f14', ''),
                                    'price': float(s.get('f2', 0)) if s.get('f2') and s.get('f2') != '-' else 0,
                                    'change_pct': float(s.get('f3', 0)) if s.get('f3') and s.get('f3') != '-' else 0,
                                    'pe': float(s.get('f9', 0)) if s.get('f9') and s.get('f9') != '-' and s.get('f9') != 0 else -1,
                                    'pb': float(s.get('f23', 0)) if s.get('f23') and s.get('f23') != '-' and s.get('f23') != 0 else -1,
                                    'mkt_cap': float(s.get('f20', 0)) if s.get('f20') else 0,
                                    'roe': float(s.get('f37', 0)) if s.get('f37') and s.get('f37') != '-' else -1,
                                    'dividend': 0,
                                })
                                extra_count += 1
                        if len(stocks) < 500:
                            break
                    else:
                        break
                time.sleep(0.3)
            except:
                break
        print(f"    {name}补充: +{extra_count}只")

print(f"\n[3/3] 最终统计...")
print(f"  总共获取: {len(all_stocks)}只股票")

# 数据质量统计
valid_pe = len([s for s in all_stocks if s['pe'] > 0])
valid_pb = len([s for s in all_stocks if s['pb'] > 0])
valid_roe = len([s for s in all_stocks if s['roe'] > 0])
valid_div = len([s for s in all_stocks if s['dividend'] > 0])

print(f"  有效PE数据: {valid_pe}只")
print(f"  有效PB数据: {valid_pb}只")
print(f"  有效ROE数据: {valid_roe}只")
print(f"  有效股息数据: {valid_div}只")

# 市值分布
large = len([s for s in all_stocks if s['mkt_cap'] > 10000000])  # >100亿
mid = len([s for s in all_stocks if 1000000 < s['mkt_cap'] <= 10000000])  # 10-100亿
small = len([s for s in all_stocks if s['mkt_cap'] <= 1000000])  # <10亿

print(f"\n  市值分布:")
print(f"    大盘股(>100亿): {large}只")
print(f"    中盘股(10-100亿): {mid}只")
print(f"    小盘股(<10亿): {small}只")

# 保存数据
if len(all_stocks) > 1000:
    save_path = r'C:\Users\12408\.qclaw\workspace\all_stocks_full.json'
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(all_stocks, f, ensure_ascii=False)
        print(f"\n  ✓ 数据已保存: {save_path}")
    except Exception as e:
        print(f"  ✗ 保存失败: {e}")
        # 尝试保存到其他位置
        try:
            alt_path = r'C:\Users\12408\.qclaw\all_stocks.json'
            with open(alt_path, 'w', encoding='utf-8') as f:
                json.dump(all_stocks, f, ensure_ascii=False)
            print(f"  ✓ 已保存到: {alt_path}")
        except:
            print(f"  ✗ 备用路径也失败")

print("\n" + "=" * 80)
print(f"  数据获取{'成功' if len(all_stocks) > 3000 else '部分成功'}: {len(all_stocks)}只")
print("=" * 80)
