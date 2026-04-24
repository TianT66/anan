# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request

codes = ['sz300760', 'sh601899', 'sh600309', 'sh515980', 'sh562500', 'sz159998']
url = 'https://qt.gtimg.cn/q=' + ','.join(codes)

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = resp.read().decode('gbk')

from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
print('=' * 70)
print(f'  📊 持仓股票行情 ({today})')
print('=' * 70)
print()

# 成本数据
costs = {
    '300760': 178.48,  # 迈瑞医疗
    '600309': 79.18,   # 万华化学(减仓后剩余成本)
    '515980': 1.0098,  # AI ETF
    # 其他待确认
}

prices = {}

for line in data.strip().split('\n'):
    if not line:
        continue
    parts = line.split('~')
    if len(parts) < 40:
        continue
    
    code = parts[2]
    name = parts[1]
    price = float(parts[3])
    prev_close = float(parts[4])
    change_pct = (price - prev_close) / prev_close * 100
    high = float(parts[33]) if parts[33] and parts[33] != '0' else price
    low = float(parts[34]) if parts[34] and parts[34] != '0' else price
    
    prices[code] = price
    
    direction = '🟢' if change_pct > 0 else '🔴' if change_pct < 0 else '⚪'
    
    cost_info = ''
    if code in costs:
        cost = costs[code]
        pnl_pct = (price - cost) / cost * 100
        cost_info = f' | 成本{cost:.2f}, 浮盈{pnl_pct:+.2f}%'
    
    print(f'{direction} {name}({code}): {price:.3f}元 ({change_pct:+.2f}%)')
    print(f'   最高{high:.3f} 最低{low:.3f}{cost_info}')

print()
print('=' * 70)
print('  💡 止损监控')
print('=' * 70)
print()

# 止损线检查
positions = [
    {'code': '300760', 'name': '迈瑞医疗', 'cost': 178.48},
    {'code': '600309', 'name': '万华化学', 'cost': 79.18},
]

for pos in positions:
    code = pos['code']
    price = prices.get(code, 0)
    cost = pos['cost']
    stop_loss = cost * 0.92
    pnl_pct = (price - cost) / cost * 100
    distance_to_stop = (price - stop_loss) / price * 100
    
    if price <= stop_loss:
        status = '🚨 触发止损!'
    elif pnl_pct <= -6:
        status = f'⚠️ 接近止损线(距止损{distance_to_stop:.1f}%)'
    else:
        status = f'✅ 正常(距止损{distance_to_stop:.1f}%)'
    
    print(f'{pos["name"]}: 现价{price:.2f}, 成本{cost:.2f}, 止损{stop_loss:.2f}')
    print(f'   浮盈{pnl_pct:+.2f}% | {status}')
    print()
