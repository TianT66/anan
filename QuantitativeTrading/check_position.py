# -*- coding: utf-8 -*-
"""
完整实时股价查询 - 支持股票+ETF
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re

def get_price_sina(code):
    """从新浪财经获取股价"""
    # ETF特殊处理
    etf_map = {
        '588000': 'sh588000',  # 科创50ETF
        '515980': 'sh515980',  # 人工智能ETF
        '512400': 'sh512400',  # 有色金属ETF
        '513060': 'sh513060',  # 恒生医疗ETF
        '516010': 'sz159998',  # 游戏ETF
        '562500': 'sh562500',  # 机器人ETF
        '159998': 'sz159998',  # 计算机ETF
    }
    
    if code in etf_map:
        full_code = etf_map[code]
    elif code.startswith('6'):
        full_code = f'sh{code}'
    elif code.startswith('0') or code.startswith('3'):
        full_code = f'sz{code}'
    elif code.startswith('5'):
        full_code = f'sh{code}'
    elif code.startswith('1'):
        full_code = f'sz{code}'
    else:
        full_code = code
    
    url = f'http://hq.sinajs.cn/list={full_code}'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://finance.sina.com.cn/'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk')
            
            match = re.search(r'="([^"]+)"', data)
            if match:
                parts = match.group(1).split(',')
                if len(parts) >= 4 and parts[0]:
                    try:
                        return {
                            'name': parts[0],
                            'open': float(parts[1]) if parts[1] else 0,
                            'last_close': float(parts[2]) if parts[2] else 0,
                            'current': float(parts[3]) if parts[3] else 0,
                            'high': float(parts[4]) if parts[4] else 0,
                            'low': float(parts[5]) if parts[5] else 0,
                            'volume': int(parts[8]) if len(parts) > 8 and parts[8] else 0,
                            'amount': float(parts[9]) if len(parts) > 9 and parts[9] else 0,
                            'success': True
                        }
                    except:
                        pass
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'No data'}


def analyze_position(code, cost, quantity_pct):
    """分析持仓盈亏"""
    result = get_price_sina(code)
    
    if not result.get('success'):
        return None
    
    current = result['current']
    name = result.get('name', code)
    
    profit_pct = (current - cost) / cost * 100
    stop_loss_price = cost * 0.92  # -8%止损
    take_profit_price = cost * 1.15  # +15%止盈
    
    return {
        'code': code,
        'name': name,
        'cost': cost,
        'current': current,
        'profit_pct': profit_pct,
        'stop_loss': stop_loss_price,
        'take_profit': take_profit_price,
        'position_pct': quantity_pct,
        'status': '盈利' if profit_pct > 0 else '亏损',
        'alert': '已触及止损线！' if current <= stop_loss_price else ('接近止损线' if profit_pct < -6 else '')
    }


if __name__ == "__main__":
    # 你的持仓
    positions = [
        ('512400', 3.38, 3.77),
        ('513060', 55.48, 0.01),
        ('515980', 0.92, 12.07),
        ('516010', 1.47, 7.93),
        ('562500', 0.97, 8.12),
        ('588000', 1.50, 11.84),
        ('600309', 78.96, 8.18),
        ('601899', 35.48, 11.26),
        ('159998', 1.07, 8.53),
        ('300760', 178.48, 13.10),
    ]
    
    print("=" * 80)
    print("  持仓实时分析报告")
    print("  数据来源: 新浪财经")
    print("=" * 80)
    
    total_profit = 0
    total_position = 0
    alerts = []
    
    print(f"\n  {'代码':<8} {'名称':<12} {'成本':<10} {'现价':<10} {'盈亏%':<10} {'仓位':<8} {'状态'}")
    print(f"  {'-'*75}")
    
    for code, cost, pct in positions:
        result = analyze_position(code, cost, pct)
        if result:
            profit = result['profit_pct']
            total_profit += profit * pct / 100
            total_position += pct
            
            alert_mark = ' [!]' if result['alert'] else ''
            print(f"  {code:<8} {result['name']:<10} {cost:<10.2f} {result['current']:<10.2f} {profit:>+8.2f}%  {pct:>5.1f}%  {result['status']}{alert_mark}")
            
            if result['alert']:
                alerts.append(f"{result['name']}({code}): {result['alert']}")
        else:
            print(f"  {code:<8} {'获取失败':<10}")
    
    print(f"  {'-'*75}")
    print(f"  总仓位: {total_position:.1f}%  |  预估整体盈亏: {total_profit:+.2f}%")
    
    if alerts:
        print(f"\n  [警告] 止损提醒:")
        for alert in alerts:
            print(f"    - {alert}")
    
    print("\n" + "=" * 80)
