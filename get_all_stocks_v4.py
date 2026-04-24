# -*- coding: utf-8 -*-
"""
全市场股票获取 - 方案4：Python直请求
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time

print("=" * 80)
print("  全市场股票数据获取 - Python直请求")
print("  2026-03-27")
print("=" * 80)

# 东方财富行情接口
base_url = "http://push2.eastmoney.com/api/qt/clist/get"

all_stocks = []

# 不同市场
markets = [
    # 沪深A股
    "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
    # 科创板
    "m:1+t:23",
    # 北交所
    "m:0+t:81+s:2048",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://quote.eastmoney.com/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}

fields = "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"

success_pages = 0
failed_pages = 0

for market in markets:
    print(f"\n  市场: {market}")
    
    for page in range(1, 30):
        params = f"pn={page}&pz=500&po=1&np=1&fltt=2&invt=2&fid=f3&fs={market}&fields={fields}&ut=bd1d9ddb04089700cf9c27f6f7426281"
        url = base_url + "?" + params
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                if data.get('data') and data['data'].get('diff'):
                    stocks = data['data']['diff']
                    if not stocks:
                        break
                    
                    for s in stocks:
                        code = str(s.get('f12', ''))
                        name = s.get('f14', '')
                        if not code or not name:
                            continue
                        
                        all_stocks.append({
                            'code': code,
                            'name': name,
                            'price': s.get('f2', 0) or 0,
                            'change_pct': s.get('f3', 0) or 0,
                            'pe': s.get('f9', 0) or -1,
                            'pb': s.get('f23', 0) or -1,
                            'mkt_cap': s.get('f20', 0) or 0,
                            'roe': s.get('f37', 0) or -1,
                            'dividend': s.get('f116', 0) or 0,
                        })
                    
                    success_pages += 1
                    total = data['data'].get('total', 0)
                    print(f"    第{page}页: +{len(stocks)}只, 累计{len(all_stocks)}只 (总数{total})")
                    time.sleep(0.5)
                else:
                    break
        except Exception as e:
            failed_pages += 1
            err_str = str(e)
            if 'Remote end closed' in err_str or 'Connection reset' in err_str:
                print(f"    第{page}页被断开 (接口限流)")
                time.sleep(3)
                if failed_pages > 3:
                    break
            elif 'timed out' in err_str.lower():
                print(f"    第{page}页超时")
                time.sleep(2)
            else:
                print(f"    第{page}页失败: {err_str[:50]}")
                time.sleep(1)
            continue
    
    if len(all_stocks) > 4000:
        break

print(f"\n\n{'='*80}")
print(f"  结果汇总")
print(f"{'='*80}")
print(f"  总共获取: {len(all_stocks)}只")
print(f"  成功页面: {success_pages}")
print(f"  失败页面: {failed_pages}")

valid_pe = len([s for s in all_stocks if s['pe'] and s['pe'] > 0])
valid_pb = len([s for s in all_stocks if s['pb'] and s['pb'] > 0])
valid_roe = len([s for s in all_stocks if s['roe'] and s['roe'] > 0])
valid_div = len([s for s in all_stocks if s['dividend'] and s['dividend'] > 0])

print(f"  有效PE: {valid_pe}只")
print(f"  有效PB: {valid_pb}只")
print(f"  有效ROE: {valid_roe}只")
print(f"  有效股息: {valid_div}只")

# 市值分布
if all_stocks[0]['mkt_cap'] and all_stocks[0]['mkt_cap'] > 0:
    large = len([s for s in all_stocks if s.get('mkt_cap', 0) > 10000000000])
    mid = len([s for s in all_stocks if 1000000000 < s.get('mkt_cap', 0) <= 10000000000])
    small = len([s for s in all_stocks if 0 < s.get('mkt_cap', 0) <= 1000000000])
    print(f"  大盘(>100亿): {large}只")
    print(f"  中盘(10-100亿): {mid}只")
    print(f"  小盘(<10亿): {small}只")

# 去重
codes = set()
dedup = []
for s in all_stocks:
    if s['code'] not in codes:
        codes.add(s['code'])
        dedup.append(s)
print(f"  去重后: {len(dedup)}只")

# 预览
print(f"\n  前20只预览:")
for s in dedup[:20]:
    pe = f"{s['pe']:.1f}" if s['pe'] and s['pe'] > 0 else '-'
    print(f"    {s['code']} {s['name']} 现价:{s['price']} PE:{pe}")

# 保存
if len(dedup) > 1000:
    save_path = r'C:\Users\12408\.qclaw\workspace\all_stocks_dedup.json'
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(dedup, f, ensure_ascii=False)
        print(f"\n  已保存: {save_path}")
    except Exception as e:
        print(f"  保存失败: {e}")
        try:
            alt = r'C:\Users\12408\.qclaw\all_stocks.json'
            with open(alt, 'w', encoding='utf-8') as f:
                json.dump(dedup, f, ensure_ascii=False)
            print(f"  已保存: {alt}")
        except:
            pass

print(f"\n{'='*80}")
