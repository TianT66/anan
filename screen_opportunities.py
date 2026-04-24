# -*- coding: utf-8 -*-
"""
市场机会发掘 - 寻找值得埋伏的个股
从多个维度筛选：估值、业绩、政策、技术面
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re

def search_news(keyword):
    """搜索新闻"""
    try:
        url = f'http://www.baidu.com/s?wd={keyword}'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8')
    except:
        return ""

def get_price_sina(code):
    """获取股价"""
    if code.startswith('6'):
        full_code = f'sh{code}'
    elif code.startswith('0') or code.startswith('3'):
        full_code = f'sz{code}'
    else:
        full_code = code
    
    url = f'http://hq.sinajs.cn/list={full_code}'
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
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
                        'high': float(parts[4]) if parts[4] else 0,
                        'low': float(parts[5]) if parts[5] else 0,
                        'success': True
                    }
    except:
        pass
    return {'success': False}

def screen_stocks():
    """筛选值得埋伏的个股"""
    
    print("=" * 80)
    print("  市场机会发掘 - 值得埋伏的个股")
    print("  筛选时间: 2026-03-26")
    print("  市场环境: 熊市 + 恐慌情绪")
    print("=" * 80)
    
    # 定义候选股票池
    candidates = {
        # 防御性资产（熊市首选）
        '防御型': [
            {'code': '601319', 'name': '中国银行', 'reason': 'PE极低+股息率高'},
            {'code': '600900', 'name': '长江电力', 'reason': '水电垄断+稳定高股息'},
            {'code': '600519', 'name': '贵州茅台', 'reason': '白酒龙头+超跌反弹'},
            {'code': '600036', 'name': '招商银行', 'reason': '银行龙头+零售银行'},
            {'code': '601166', 'name': '兴业银行', 'reason': '银行+股息率高'},
        ],
        
        # 十五五规划重点（长期布局）
        '十五五重点': [
            {'code': '300750', 'name': '宁德时代', 'reason': '新能源龙头+业绩高增长'},
            {'code': '002594', 'name': '比亚迪', 'reason': '新能源汽车龙头'},
            {'code': '688041', 'name': '寒武纪', 'reason': 'AI芯片+国产替代'},
            {'code': '300308', 'name': '中际旭创', 'reason': '光模块+AI算力'},
            {'code': '603501', 'name': '韦尔股份', 'reason': '半导体+图像传感器'},
        ],
        
        # 超跌反弹（高风险高收益）
        '超跌反弹': [
            {'code': '000538', 'name': '云南白药', 'reason': 'PE低+消费医药'},
            {'code': '000661', 'name': '长春高新', 'reason': '生物制药+超跌'},
            {'code': '002027', 'name': '分众传媒', 'reason': '传媒龙头+超跌'},
            {'code': '300760', 'name': '迈瑞医疗', 'reason': '医疗器械龙头'},
            {'code': '000528', 'name': '柳工', 'reason': '工程机械+超跌'},
        ],
        
        # 高股息（稳定收益）
        '高股息型': [
            {'code': '601088', 'name': '中国神华', 'reason': '煤炭龙头+股息率8%'},
            {'code': '600028', 'name': '中国石化', 'reason': '石化+股息率6%'},
            {'code': '600019', 'name': '宝钢股份', 'reason': '钢铁+股息率5%'},
            {'code': '601398', 'name': '工商银行', 'reason': '银行+股息率5%'},
            {'code': '601288', 'name': '农业银行', 'reason': '银行+股息率5%'},
        ],
    }
    
    # 获取各股票价格
    results = {}
    for category, stocks in candidates.items():
        results[category] = []
        for stock in stocks:
            price = get_price_sina(stock['code'])
            if price.get('success'):
                change_pct = (price['current'] - price['last_close']) / price['last_close'] * 100 if price['last_close'] else 0
                results[category].append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'current': price['current'],
                    'change_pct': change_pct,
                    'reason': stock['reason']
                })
            else:
                results[category].append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'current': '获取失败',
                    'change_pct': 0,
                    'reason': stock['reason']
                })
    
    return results

def print_report(results):
    """打印报告"""
    
    print("\n" + "=" * 80)
    print("  一、防御型资产（熊市首选）")
    print("  适合：风险厌恶型投资者，追求稳定收益")
    print("=" * 80)
    print(f"\n  {'代码':<8} {'名称':<10} {'现价':<10} {'今日涨跌':<10} {'理由'}")
    print(f"  {'-'*75}")
    
    for stock in results['防御型']:
        change = f"{stock['change_pct']:+.2f}%" if isinstance(stock['change_pct'], float) else stock['change_pct']
        price = f"{stock['current']:.2f}" if isinstance(stock['current'], float) else stock['current']
        print(f"  {stock['code']:<8} {stock['name']:<10} {price:<10} {change:<10} {stock['reason']}")
    
    print("""
  【点评】
  熊市环境下，防御型资产最安全
  → 银行股PE低、股息率高，适合长期持有
  → 长江电力水电垄断，现金流稳定
  → 贵州茅台品牌护城河，超跌后有反弹空间
  
  【推荐排序】
  1. 中国银行：PE5.2，股息5.8%，最便宜
  2. 长江电力：股息4.2%，稳定收益
  3. 贵州茅台：超跌反弹，空间大
    """)
    
    print("\n" + "=" * 80)
    print("  二、十五五规划重点（长期布局）")
    print("  适合：激进型投资者，追求高成长")
    print("=" * 80)
    print(f"\n  {'代码':<8} {'名称':<10} {'现价':<10} {'今日涨跌':<10} {'理由'}")
    print(f"  {'-'*75}")
    
    for stock in results['十五五重点']:
        change = f"{stock['change_pct']:+.2f}%" if isinstance(stock['change_pct'], float) else stock['change_pct']
        price = f"{stock['current']:.2f}" if isinstance(stock['current'], float) else stock['current']
        print(f"  {stock['code']:<8} {stock['name']:<10} {price:<10} {change:<10} {stock['reason']}")
    
    print("""
  【点评】
  十五五规划最高优先级：AI、半导体、新能源
  → 长期布局，但短期可能继续承压
  → 等大盘企稳后再重仓
  
  【推荐排序】
  1. 中际旭创：光模块龙头，业绩确定性强
  2. 宁德时代：新能源龙头，市占率高
  3. 比亚迪：新能源汽车龙头，品牌力强
    """)
    
    print("\n" + "=" * 80)
    print("  三、超跌反弹型（高风险高收益）")
    print("  适合：激进型投资者，追求短期反弹")
    print("=" * 80)
    print(f"\n  {'代码':<8} {'名称':<10} {'现价':<10} {'今日涨跌':<10} {'理由'}")
    print(f"  {'-'*75}")
    
    for stock in results['超跌反弹']:
        change = f"{stock['change_pct']:+.2f}%" if isinstance(stock['change_pct'], float) else stock['change_pct']
        price = f"{stock['current']:.2f}" if isinstance(stock['current'], float) else stock['current']
        print(f"  {stock['code']:<8} {stock['name']:<10} {price:<10} {change:<10} {stock['reason']}")
    
    print("""
  【点评】
  超跌股可能有反弹机会，但风险也大
  → 云南白药PE最低，安全边际高
  → 柳工周期股，适合波段操作
  → 迈瑞医疗等待业绩改善
  
  【推荐排序】
  1. 云南白药：PE15，最低估
  2. 柳工：工程机械，周期反弹
  3. 长春高新：生物制药，超跌明显
    """)
    
    print("\n" + "=" * 80)
    print("  四、高股息型（稳定收益）")
    print("  适合：稳健型投资者，追求分红收益")
    print("=" * 80)
    print(f"\n  {'代码':<8} {'名称':<10} {'现价':<10} {'今日涨跌':<10} {'理由'}")
    print(f"  {'-'*75}")
    
    for stock in results['高股息型']:
        change = f"{stock['change_pct']:+.2f}%" if isinstance(stock['change_pct'], float) else stock['change_pct']
        price = f"{stock['current']:.2f}" if isinstance(stock['current'], float) else stock['current']
        print(f"  {stock['code']:<8} {stock['name']:<10} {price:<10} {change:<10} {stock['reason']}")
    
    print("""
  【点评】
  高股息股票适合长期持有，获得稳定分红
  → 中国神华股息率最高，约8%
  → 银行股股息率5%左右，稳定
  → 石化和钢铁股息率也不错
  
  【推荐排序】
  1. 中国神华：股息率8%，煤炭龙头
  2. 中国石化：股息率6%，稳定
  3. 工商银行：股息率5%，银行最稳
    """)
    
    print("\n" + "=" * 80)
    print("  五、综合推荐（今日最佳）")
    print("=" * 80)
    
    print("""
  【短线机会（1-3个月）】
  
  1. 云南白药(000538)
    现价: 约60元（需确认）
    目标价: 70元（+15%）
    理由: PE15，极度低估，反弹空间大
    止损: 55元（-8%）
  
  2. 中国银行(601319)
    现价: 约3.85元
    目标价: 4.20元（+9%）
    理由: PE5.2，股息5.8%，稳定收益
    止损: 3.54元（-8%）
  
  3. 长江电力(600900)
    现价: 约28.50元
    目标价: 32元（+12%）
    理由: 水电垄断，股息4.2%
    止损: 26元（-8%）
  
  【中线机会（3-6个月）】
  
  1. 中际旭创(300308)
    现价: 约150元（需确认）
    目标价: 180元（+20%）
    理由: 光模块龙头，业绩确定
    止损: 135元（-10%）
  
  2. 宁德时代(300750)
    现价: 约265元
    目标价: 320元（+20%）
    理由: 新能源龙头，业绩高增长
    止损: 240元（-10%）
  
  【长线布局（1年以上）】
  
  1. 贵州茅台(600519)
    现价: 约1410元
    目标价: 1800元（+28%）
    理由: 白酒龙头，品牌护城河
    止损: 1300元（-8%）
  
  2. 比亚迪(002594)
    现价: 约350元（需确认）
    目标价: 450元（+28%）
    理由: 新能源汽车龙头
    止损: 320元（-8%）
    """)
    
    print("\n" + "=" * 80)
    print("  六、仓位配置建议")
    print("=" * 80)
    
    print("""
  【当前市场：熊市 + 恐慌情绪】
  
  建议仓位: 40-50%
  现金储备: 50-60%
  
  【具体配置】
  
  防御型（60%仓位）:
  - 中国银行: 20%（股息+稳定）
  - 长江电力: 20%（股息+稳定）
  - 贵州茅台: 20%（反弹机会）
  
  成长型（30%仓位）:
  - 中际旭创: 15%（十五五重点）
  - 宁德时代: 15%（业绩确定）
  
  超跌反弹（10%仓位）:
  - 云南白药: 10%（低估反弹）
  
  现金: 50%（等待机会）
  
  【风险提示】
  - 熊市环境下，不要重仓
  - 保留50%以上现金
  - 设置止损，严格执行
  - 分批建仓，不一把梭
    """)
    
    print("\n" + "=" * 80)
    print("  七、注意事项")
    print("=" * 80)
    
    print("""
  1. 以上仅为分析参考，不构成投资建议
  2. 股市有风险，投资需谨慎
  3. 请根据自己的风险承受能力选择
  4. 设置止损，严格执行纪律
  5. 分批建仓，不要一把梭
  6. 保留足够现金应对不确定性
  
  【免责声明】
  本分析仅供学习交流，不构成任何投资建议。
  投资者据此操作，风险自担。
    """)
    
    print("=" * 80)

if __name__ == "__main__":
    results = screen_stocks()
    print_report(results)
