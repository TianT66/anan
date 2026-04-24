# -*- coding: utf-8 -*-
"""
全市场股票获取 - 带重试版本
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, json, time, os

def get_all_stocks():
    all_stocks = []
    seen = set()
    fs = 'm%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23%2Cm%3A0%2Bt%3A81%2Cs%3A2048'

    for page in range(1, 70):
        url = (
            'http://push2.eastmoney.com/api/qt/clist/get'
            '?pn=' + str(page) + '&pz=100&po=1&np=1'
            '&ut=bd1d9ddb04089700cf9c27f6f7426281'
            '&fltt=2&invt=2&fid=f3&fs=' + fs +
            '&fields=f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25'
        )
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
            'Accept': 'application/json, text/plain, */*',
        }

        success = False
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if data.get('data') and data['data'].get('diff'):
                        stocks = data['data']['diff']
                        if not stocks:
                            print('第' + str(page) + '页无数据，停止')
                            return all_stocks
                        added = 0
                        for s in stocks:
                            code = s.get('f12', '')
                            name = s.get('f14', '')
                            price = s.get('f2', 0)
                            if code and name and code not in seen and price and price != '-':
                                seen.add(code)
                                mkt = s.get('f13', 0)
                                prefix = 'sh' if mkt == 1 else 'sz'
                                chg = s.get('f3', 0)
                                pe = s.get('f9', 0)
                                pb = s.get('f23', 0)
                                mc = s.get('f20', 0)
                                to = s.get('f8', 0)
                                vr = s.get('f10', 0)
                                amp = s.get('f7', 0)
                                all_stocks.append({
                                    'code': str(code),
                                    'name': name,
                                    'prefix': prefix,
                                    'price': float(price)/100 if isinstance(price, int) else float(price),
                                    'change_pct': float(chg)/100 if isinstance(chg, int) else float(chg or 0),
                                    'pe': float(pe) if pe and pe != '-' else 0,
                                    'pb': float(pb) if pb and pb != '-' else 0,
                                    'market_cap': float(mc) if mc else 0,
                                    'turnover': float(to) if to else 0,
                                    'volume_ratio': float(vr) if vr else 0,
                                    'amplitude': float(amp) if amp else 0,
                                })
                                added += 1
                        print('第' + str(page) + '页 +' + str(added) + '只，累计' + str(len(all_stocks)) + '只')
                        success = True
                        break
                    else:
                        print('第' + str(page) + '页返回空，停止')
                        return all_stocks
            except Exception as e:
                print('第' + str(page) + '页第' + str(attempt+1) + '次失败: ' + str(e))
                time.sleep(3)

        if not success:
            print('第' + str(page) + '页3次均失败，跳过')
        time.sleep(0.5)

    return all_stocks


print('=' * 60)
print('  全市场股票数据获取（带重试）')
print('=' * 60)

stocks = get_all_stocks()
print('\n共获取 ' + str(len(stocks)) + ' 只股票')

save_path = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\all_stocks.json'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
with open(save_path, 'w', encoding='utf-8') as f:
    json.dump(stocks, f, ensure_ascii=False, indent=2)

print('已保存到: ' + save_path)
print('前5只预览:')
for s in stocks[:5]:
    print('  ' + s['prefix'] + s['code'] + ' ' + s['name'] + ' 现价:' + str(s['price']) + ' 涨跌:' + str(s['change_pct']) + '% PE:' + str(s['pe']))
