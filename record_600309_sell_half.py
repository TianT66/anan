# -*- coding: utf-8 -*-
"""
记录 600309 万华化学 减仓一半
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import re
from datetime import datetime

def get_price(code):
    full = f'sh{code}'
    url = f'http://hq.sinajs.cn/list={full}'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://finance.sina.com.cn/'
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read().decode('gbk')
            match = re.search(r'="([^"]+)"', data)
            if match:
                parts = match.group(1).split(',')
                if len(parts) >= 4 and parts[0]:
                    return {
                        'name': parts[0].strip(),
                        'current': float(parts[3]),
                        'last_close': float(parts[2]),
                        'open': float(parts[1]),
                        'high': float(parts[4]),
                        'low': float(parts[5]),
                        'success': True
                    }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    return {'success': False}

# 万华化学持仓信息（根据历史记录）
COST_PRICE = 85.00       # 估算成本价（需用户确认）
POSITION_PCT = 5.0       # 原始仓位（估算）
SELL_RATIO = 0.5         # 卖出比例

now = datetime.now()
price_data = get_price('600309')

print("=" * 70)
print("  交易记录：600309 万华化学 减仓一半")
print(f"  记录时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

if price_data.get('success'):
    sell_price = price_data['current']
    change = (sell_price - price_data['last_close']) / price_data['last_close'] * 100
    
    print(f"\n【实时行情】")
    print(f"  股票名称: {price_data['name']}")
    print(f"  当前价格: {sell_price:.2f}元")
    print(f"  今日涨跌: {change:+.2f}%")
    print(f"  今日最高: {price_data['high']:.2f}元")
    print(f"  今日最低: {price_data['low']:.2f}元")
    
    # 盈亏计算
    profit_pct = (sell_price - COST_PRICE) / COST_PRICE * 100
    
    print(f"\n【交易详情】")
    print(f"  操作: 减仓一半（卖出50%）")
    print(f"  卖出价格: {sell_price:.2f}元")
    print(f"  参考成本: {COST_PRICE:.2f}元（请确认实际成本）")
    print(f"  浮动盈亏: {profit_pct:+.2f}%")
    print(f"  原始仓位: {POSITION_PCT:.1f}%")
    print(f"  卖出仓位: {POSITION_PCT * SELL_RATIO:.1f}%")
    print(f"  剩余仓位: {POSITION_PCT * (1 - SELL_RATIO):.1f}%")
    
    print(f"\n【操作评价】")
    if profit_pct > 0:
        print(f"  ✓ 盈利减仓，锁定利润 {profit_pct:.2f}%")
        print(f"  ✓ 保留一半仓位，继续持有等待更高目标")
    elif profit_pct > -8:
        print(f"  ⚠ 小幅亏损减仓 {profit_pct:.2f}%，控制风险")
        print(f"  ⚠ 剩余仓位注意止损线")
    else:
        print(f"  ✗ 亏损较大 {profit_pct:.2f}%，止损减仓")
    
    print(f"\n【万华化学基本面】")
    print(f"  行业: 化工龙头（MDI全球第一）")
    print(f"  PE: 约12-15倍（合理偏低）")
    print(f"  股息率: 约3%")
    print(f"  护城河: MDI技术壁垒高，全球市占率第一")
    print(f"  风险: 化工周期性强，受宏观影响大")
    
    print(f"\n【剩余仓位建议】")
    print(f"  止损线: {sell_price * 0.92:.2f}元（-8%）")
    print(f"  目标价: {sell_price * 1.20:.2f}元（+20%）")
    print(f"  操作: 继续持有，等待化工周期复苏")
    
else:
    print(f"\n  ⚠ 无法获取实时价格，请手动确认卖出价格")

print(f"\n{'='*70}")
print(f"  ⚠ 请告诉我实际成本价和仓位，我来精确计算盈亏")
print(f"{'='*70}")
