# -*- coding: utf-8 -*-
"""
全市场扫描 - 第一步：获取所有A股列表
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time
import os

def get_all_stocks():
    """从东方财富获取全市场股票列表"""
    all_stocks = []
    
    # 分页获取
    for page in range(1, 60):  # 约5000只股票，每页100条
        url = (
            f'http://push2.eastmoney.com/api/qt/clist/get'
            f'?pn={page}&pz=100&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281'
            f'&fltt=2&invt=2&fid=f3&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23%2Cm%3A0%2Bt%3A81%2Bs%3A2048'
            f'&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        )
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://quote.eastmoney.com/'
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                
                if data.get('data') and data['data'].get('diff'):
                    stocks = data['data']['diff']
                    if not stocks:
                        break
                    
                    for s in stocks:
                        code = s.get('f12', '')
                        name = s.get('f14', '')
                        price = s.get('f2', 0)
                        change_pct = s.get('f3', 0)
                        pe = s.get('f9', 0)
                        pb = s.get('f23', 0)
                        market_cap = s.get('f20', 0)  # 总市值
                        volume_ratio = s.get('f10', 0)  # 量比
                        turnover = s.get('f8', 0)  # 换手率
                        
                        if code and name and price and price != '-':
                            all_stocks.append({
                                'code': str(code),
                                'name': name,
                                'price': float(price) / 100 if isinstance(price, int) else float(price),
                                'change_pct': float(change_pct) / 100 if isinstance(change_pct, int) else float(change_pct),
                                'pe': float(pe) if pe and pe != '-' else 0,
                                'pb': float(pb) if pb and pb != '-' else 0,
                                'market_cap': float(market_cap) if market_cap else 0,
                                'volume_ratio': float(volume_ratio) if volume_ratio else 0,
                                'turnover': float(turnover) if turnover else 0,
                            })
                    
                    print(f'  已获取第{page}页，累计{len(all_stocks)}只股票...')
                    time.sleep(0.3)
                else:
                    break
        except Exception as e:
            print(f'  第{page}页获取失败: {e}')
            time.sleep(1)
            continue
    
    return all_stocks

print("=" * 70)
print("  全市场扫描 - 获取股票列表")
print("=" * 70)
print("\n  正在获取全市场股票数据...")

stocks = get_all_stocks()

print(f"\n  共获取 {len(stocks)} 只股票")

# 保存到文件
save_path = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\all_stocks.json'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
with open(save_path, 'w', encoding='utf-8') as f:
    json.dump(stocks, f, ensure_ascii=False, indent=2)

print(f"  已保存到: {save_path}")
print(f"\n  前5只股票预览:")
for s in stocks[:5]:
    print(f"    {s['code']} {s['name']} 现价:{s['price']} PE:{s['pe']} PB:{s['pb']}")
