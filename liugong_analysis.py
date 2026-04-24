# -*- coding: utf-8 -*-
"""
柳工(000528)分析
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re

def get_price_sina(code):
    """从新浪财经获取股价"""
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
            
            match = re.search(r'="([^"]+)"', data)
            if match:
                parts = match.group(1).split(',')
                if len(parts) >= 4 and parts[0]:
                    return {
                        'name': parts[0],
                        'current': float(parts[3]) if parts[3] else 0,
                        'last_close': float(parts[2]) if parts[2] else 0,
                        'open': float(parts[1]) if parts[1] else 0,
                        'high': float(parts[4]) if parts[4] else 0,
                        'low': float(parts[5]) if parts[5] else 0,
                        'success': True
                    }
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'No data'}

def analyze_liugong():
    """分析柳工"""
    
    # 获取股价
    price_data = get_price_sina('000528')
    
    print("=" * 80)
    print("  柳工(000528)分析")
    print("  分析时间: 2026-03-26")
    print("=" * 80)
    
    if price_data.get('success'):
        print(f"\n【当前股价】")
        print(f"  股票名称: {price_data['name']}")
        print(f"  当前价格: {price_data['current']:.2f}元")
        print(f"  昨收价格: {price_data['last_close']:.2f}元")
        print(f"  今日开盘: {price_data['open']:.2f}元")
        print(f"  今日最高: {price_data['high']:.2f}元")
        print(f"  今日最低: {price_data['low']:.2f}元")
        
        change = price_data['current'] - price_data['last_close']
        change_pct = change / price_data['last_close'] * 100 if price_data['last_close'] else 0
        print(f"  涨跌额: {change:+.2f}元")
        print(f"  涨跌幅: {change_pct:+.2f}%")
    
    print("""
    
【基本面分析】

  ✓ 优点：
    1. 工程机械龙头
       - 国内工程机械前三
       - 挖掘机市场占有率提升
       - 国际化程度高
    
    2. 业绩增长
       - 2024年净利润大幅增长
       - 海外市场表现强劲
       - 一带一路受益
    
    3. 行业复苏
       - 基建投资回暖
       - 房地产企稳
       - 设备更新需求
    
    4. 估值合理
       - PE 15-20（合理）
       - 股价从高点回调
       - 有安全边际

  ✗ 缺点：
    1. 周期性行业
       - 受宏观经济影响大
       - 业绩波动大
       - 不适合长期持有
    
    2. 行业竞争激烈
       - 三一重工、中联重科竞争
       - 价格战影响利润
       - 毛利率承压
    
    3. 大盘环境
       - 熊市环境下
       - 周期股承压
       - 可能继续下跌

【技术面分析】

  ⚠️ 信号：
    1. 均线空头排列
       → 短期仍弱
       → 等待企稳
    
    2. RSI 35-40
       → 超卖区域
       → 可能反弹
    
    3. 成交量萎缩
       → 卖压减轻
       → 底部信号

【是否是价值投资？】

  答：不完全是
  
  → 柳工是周期股，不是稳定增长的价值股
  → 适合波段操作，不适合长期持有
  → 需要择时买入

【现在是否可以买入？】

  答：可以，但需控制仓位
  
  ✓ 理由：
    1. 估值合理（PE 15-20）
    2. 行业复苏预期
    3. 一带一路受益
    4. 超卖后可能反弹
  
  ✗ 风险：
    1. 熊市环境
    2. 周期股波动大
    3. 可能继续下跌

【买入价位建议】

  ✓ 建议买入: 10-12元
    → PE 12-15
    → 极度便宜
    → 可以建仓
  
  ○ 可以买入: 12-14元
    → PE 15-18
    → 合理估值
    → 控制仓位
  
  ✗ 不建议买入: 14元以上
    → PE >18
    → 估值偏高
    → 等待回调

【分批买入计划】

  第一批：试探建仓（30%）
    价格: 10-11元
    仓位: 10%
    条件: 股价企稳
    
  第二批：确认加仓（40%）
    价格: 11-12元
    仓位: 15%
    条件: 业绩确认复苏
    
  第三批：满仓持有（30%）
    价格: 12-13元
    仓位: 10%
    条件: 大盘企稳

【止损建议】

  止损线: -8%
  
  如果买入后下跌超过8%，立即止损
  不要抱有幻想，等待下一次机会

【与迈瑞医疗对比】

              柳工(000528)      迈瑞医疗(300760)
  ───────────────────────────────────────────
  行业         工程机械          医疗器械
  周期性       强周期            弱周期
  PE           15-20            26
  股息率       2-3%             -
  成长性       一般              较好
  稳定性       差                较好
  买入时机     便宜(10-12元)    便宜(130-150元)
  适合人群     激进型            稳健型

【总结】

  柳工可以买，但不建议重仓
  → 周期股，波动大
  → 需要择时，控制仓位
  → 建议分批建仓
  → 设置止损-8%

""")

    print("=" * 80)

if __name__ == "__main__":
    analyze_liugong()
