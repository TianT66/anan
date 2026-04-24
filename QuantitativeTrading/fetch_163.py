# -*- coding: utf-8 -*-
"""
全市场股票获取 - 网易财经接口（一次拉全量）
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request, json, os, time

def get_all_stocks_163():
    """网易财经 - 一次拉5000只"""
    url = (
        'http://quotes.money.163.com/hs/service/diyrank.php'
        '?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php'
        '&page=0&query=STATUS:1'
        '&fields=SYMBOL,NAME,PRICE,PERCENT,OPEN,HIGH,LOW,YESTCLOSE,VOLUME,TURNOVER,'
        'PE,PB,MARKET_CAPITAL,FLOAT_MARKET_CAPITAL,INDUSTRY,MAIN_NETINFLOW'
        '&sort=PERCENT&order=desc&count=5000&type=query'
    )
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://quotes.money.163.com/',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    stocks = []
    for item in data.get('list', []):
        code = str(item.get('SYMBOL', ''))
        if not code:
            continue
        if code.startswith('6'):
            prefix = 'sh'
        elif code.startswith(('0', '3', '8', '4')):
            prefix = 'sz'
        else:
            continue
        
        price = item.get('PRICE', 0) or 0
        if price == 0:
            continue
        
        stocks.append({
            'code': code,
            'name': item.get('NAME', ''),
            'prefix': prefix,
            'price': float(price),
            'change_pct': float(item.get('PERCENT', 0) or 0),
            'open': float(item.get('OPEN', 0) or 0),
            'high': float(item.get('HIGH', 0) or 0),
            'low': float(item.get('LOW', 0) or 0),
            'prev_close': float(item.get('YESTCLOSE', 0) or 0),
            'volume': float(item.get('VOLUME', 0) or 0),
            'turnover': float(item.get('TURNOVER', 0) or 0),
            'pe': float(item.get('PE', 0) or 0),
            'pb': float(item.get('PB', 0) or 0),
            'market_cap': float(item.get('MARKET_CAPITAL', 0) or 0),
            'float_cap': float(item.get('FLOAT_MARKET_CAPITAL', 0) or 0),
            'industry': item.get('INDUSTRY', ''),
            'main_netinflow': float(item.get('MAIN_NETINFLOW', 0) or 0),
        })
    return stocks


print('=' * 60)
print('  全市场股票数据获取 - 网易财经接口')
print('=' * 60)

try:
    print('正在请求网易财经...')
    stocks = get_all_stocks_163()
    print('获取成功！共 ' + str(len(stocks)) + ' 只股票')
    
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
    
    print('\n前10只涨幅最大:')
    top10 = sorted(stocks, key=lambda x: x['change_pct'], reverse=True)[:10]
    for s in top10:
        print('  ' + s['prefix'] + s['code'] + ' ' + s['name'] + ' 现价:' + str(s['price']) + ' 涨跌:+' + str(round(s['change_pct'],2)) + '% 行业:' + s['industry'])

except Exception as e:
    print('网易接口失败: ' + str(e))
    import traceback
    traceback.print_exc()
