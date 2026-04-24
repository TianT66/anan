# -*- coding: utf-8 -*-
"""
网页爬取实时股价
从新浪财经/东方财富获取实时行情
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re

def get_price_sina(code):
    """从新浪财经获取股价"""
    # 判断市场
    if code.startswith('6'):
        full_code = f'sh{code}'
    elif code.startswith('0') or code.startswith('3'):
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
            
            # 解析: var hq_str_sz300760="迈瑞医疗,203.50,202.00,205.20,206.00,..."
            match = re.search(r'="([^"]+)"', data)
            if match:
                parts = match.group(1).split(',')
                if len(parts) >= 4:
                    return {
                        'name': parts[0],
                        'open': float(parts[1]),
                        'last_close': float(parts[2]),
                        'current': float(parts[3]),
                        'high': float(parts[4]) if parts[4] else 0,
                        'low': float(parts[5]) if parts[5] else 0,
                        'volume': int(parts[8]) if len(parts) > 8 and parts[8] else 0,
                        'amount': float(parts[9]) if len(parts) > 9 and parts[9] else 0,
                        'success': True
                    }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'No data'}


def get_price_eastmoney(code):
    """从东方财富获取股价"""
    # 判断市场代码
    if code.startswith('6'):
        secid = f'1.{code}'
    else:
        secid = f'0.{code}'
    
    url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f170,f171'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('data'):
                d = data['data']
                return {
                    'current': d.get('f43', 0) / 100 if d.get('f43') else 0,
                    'high': d.get('f44', 0) / 100 if d.get('f44') else 0,
                    'low': d.get('f45', 0) / 100 if d.get('f45') else 0,
                    'open': d.get('f46', 0) / 100 if d.get('f46') else 0,
                    'last_close': d.get('f60', 0) / 100 if d.get('f60') else 0,
                    'volume': d.get('f47', 0),
                    'amount': d.get('f48', 0),
                    'change_pct': d.get('f170', 0) / 100 if d.get('f170') else 0,
                    'success': True
                }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'No data'}


def get_price(code):
    """获取股价，优先新浪，失败换东方财富"""
    result = get_price_sina(code)
    if result.get('success'):
        result['source'] = '新浪财经'
        return result
    
    result = get_price_eastmoney(code)
    if result.get('success'):
        result['source'] = '东方财富'
        return result
    
    return {'success': False, 'error': 'All sources failed'}


def get_prices(codes):
    """批量获取多只股票价格"""
    results = {}
    for code in codes:
        result = get_price(code)
        results[code] = result
    return results


if __name__ == "__main__":
    # 测试
    test_codes = ['300760', '601899', '600519', '588000', '515980']
    
    print("=" * 60)
    print("  实时股价查询")
    print("=" * 60)
    
    for code in test_codes:
        result = get_price(code)
        if result.get('success'):
            name = result.get('name', code)
            current = result.get('current', 0)
            change = result.get('change_pct', 0)
            print(f"  {code} {name}: {current:.2f} 元 ({change:+.2f}%)")
        else:
            print(f"  {code}: 获取失败 - {result.get('error', 'Unknown')}")
    
    print("=" * 60)
