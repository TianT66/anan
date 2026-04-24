# -*- coding: utf-8 -*-
"""
全市场股票获取 - 新浪财经接口（分页拉全量）
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, json, os, time

def get_all_stocks_sina():
    """新浪财经分页拉取全市场A股"""
    all_stocks = []
    seen = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://finance.sina.com.cn/',
    }

    # 新浪按节点分类：hs_a=沪深A股
    for page in range(1, 60):
        url = (
            'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/'
            'Market_Center.getHQNodeData?page=' + str(page) +
            '&num=100&sort=symbol&asc=1&node=hs_a&symbol=&_s_r_a=page'
        )
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode('gbk', errors='replace')
                data = json.loads(content)
                if not data:
                    print('第' + str(page) + '页无数据，停止')
                    break
                added = 0
                for item in data:
                    code = str(item.get('symbol', ''))
                    name = item.get('name', '')
                    price = item.get('trade', 0) or 0
                    if not code or code in seen or not price:
                        continue
                    seen.add(code)
                    prefix = 'sh' if code.startswith('6') else 'sz'
                    chg = item.get('pricechange', 0) or 0
                    chg_pct = item.get('changepercent', 0) or 0
                    pe = item.get('per', 0) or 0
                    pb = item.get('pb', 0) or 0
                    mktcap = item.get('mktcap', 0) or 0
                    nmc = item.get('nmc', 0) or 0
                    volume = item.get('volume', 0) or 0
                    amount = item.get('amount', 0) or 0
                    turnover = item.get('turnoverratio', 0) or 0
                    open_ = item.get('open', 0) or 0
                    high = item.get('high', 0) or 0
                    low = item.get('low', 0) or 0
                    prev = item.get('settlement', 0) or 0

                    all_stocks.append({
                        'code': code,
                        'name': name,
                        'prefix': prefix,
                        'price': float(price),
                        'change': float(chg),
                        'change_pct': float(chg_pct),
                        'open': float(open_),
                        'high': float(high),
                        'low': float(low),
                        'prev_close': float(prev),
                        'volume': float(volume),
                        'amount': float(amount),
                        'turnover': float(turnover),
                        'pe': float(pe),
                        'pb': float(pb),
                        'market_cap': float(mktcap),
                        'float_cap': float(nmc),
                    })
                    added += 1
                print('第' + str(page) + '页 +' + str(added) + '只，累计' + str(len(all_stocks)) + '只')
                time.sleep(0.3)
        except Exception as e:
            print('第' + str(page) + '页失败: ' + str(e))
            time.sleep(2)
            continue

    return all_stocks


print('=' * 60)
print('  全市场股票数据获取 - 新浪财经接口')
print('=' * 60)

stocks = get_all_stocks_sina()
print('\n共获取 ' + str(len(stocks)) + ' 只股票')

save_path = r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\data\all_stocks.json'
os.makedirs(os.path.dirname(save_path), exist_ok=True)
with open(save_path, 'w', encoding='utf-8') as f:
    json.dump(stocks, f, ensure_ascii=False, indent=2)
print('已保存到: ' + save_path)

# 统计
up = len([s for s in stocks if s['change_pct'] > 0])
down = len([s for s in stocks if s['change_pct'] < 0])
flat = len([s for s in stocks if s['change_pct'] == 0])
limit_up = len([s for s in stocks if s['change_pct'] >= 9.9])
limit_down = len([s for s in stocks if s['change_pct'] <= -9.9])

print('\n今日市场概况:')
print('  上涨: ' + str(up) + '只  下跌: ' + str(down) + '只  平盘: ' + str(flat) + '只')
print('  涨停: ' + str(limit_up) + '只  跌停: ' + str(limit_down) + '只')

print('\n涨幅前10:')
top10 = sorted(stocks, key=lambda x: x['change_pct'], reverse=True)[:10]
for s in top10:
    print('  ' + s['prefix'] + s['code'] + ' ' + s['name'] + ' 现价:' + str(s['price']) + ' 涨跌:+' + str(round(s['change_pct'],2)) + '%')
