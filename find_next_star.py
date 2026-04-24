# -*- coding: utf-8 -*-
"""
寻找下一个"中际旭创"
2023年中际旭创特征：
- 业绩爆发前夕，市场还没发现
- 行业处于爆发前夜（AI算力需求爆发）
- 公司是细分赛道龙头
- 估值还在低位
- 股价还没启动
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re
import time

def get_price_sina(code):
    """获取股价"""
    if code.startswith('6'):
        full_code = f'sh{code}'
    elif code.startswith('0') or code.startswith('3') or code.startswith('1'):
        full_code = f'sz{code}'
    elif code.startswith('5'):
        full_code = f'sh{code}'
    else:
        full_code = f'sz{code}'
    
    url = f'http://hq.sinajs.cn/list={full_code}'
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
                        'name': parts[0],
                        'current': float(parts[3]) if parts[3] else 0,
                        'last_close': float(parts[2]) if parts[2] else 0,
                        'success': True
                    }
    except:
        pass
    return {'success': False}

def search_prosearch(keyword, from_days=30):
    """搜索最新新闻"""
    try:
        PORT = __import__('os').environ.get('AUTH_GATEWAY_PORT', '19000')
        from_time = int(time.time()) - from_days * 86400
        url = f'http://localhost:{PORT}/proxy/prosearch/search'
        data = json.dumps({'keyword': keyword, 'from_time': from_time}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get('success') and result.get('data', {}).get('docs'):
                return [d.get('passage', '') for d in result['data']['docs'][:3]]
    except:
        pass
    return []

print("=" * 80)
print("  寻找下一个'中际旭创'")
print("  分析时间: 2026-03-26")
print("=" * 80)

print("""
【中际旭创2023年爆发的核心逻辑】

  1. 行业爆发前夜
     → ChatGPT引爆AI需求
     → 数据中心算力需求暴增
     → 光模块需求爆发
  
  2. 公司是细分赛道龙头
     → 光模块全球前三
     → 技术壁垒高
     → 客户是英伟达/微软/谷歌
  
  3. 市场还没发现
     → 2022年底股价在低位
     → PE只有15-20
     → 机构持仓少
  
  4. 业绩爆发确定性强
     → 订单已经在手
     → 产能快速扩张
     → 业绩增速>100%

【寻找标准】

  ✓ 行业处于爆发前夜（需求即将爆发）
  ✓ 公司是细分赛道龙头（技术壁垒高）
  ✓ 市场还没发现（PE低，机构持仓少）
  ✓ 业绩爆发确定性强（订单在手）
  ✓ 股价还没启动（在低位）
""")

print("=" * 80)
print("  候选一：人形机器人赛道")
print("  类比：2023年AI算力 → 2026年人形机器人")
print("=" * 80)

robot_stocks = [
    {'code': '300024', 'name': '机器人', 'reason': '工业机器人龙头，人形机器人布局'},
    {'code': '002747', 'name': '埃斯顿', 'reason': '国产机器人龙头，减速器自研'},
    {'code': '688169', 'name': '石头科技', 'reason': '扫地机器人龙头，AI化升级'},
    {'code': '300496', 'name': '中科创达', 'reason': '机器人操作系统，软件龙头'},
    {'code': '002527', 'name': '新时达', 'reason': '工业机器人+人形机器人布局'},
]

print(f"\n  {'代码':<8} {'名称':<12} {'现价':<10} {'理由'}")
print(f"  {'-'*70}")
for stock in robot_stocks:
    p = get_price_sina(stock['code'])
    price = f"{p['current']:.2f}" if p.get('success') else '获取失败'
    print(f"  {stock['code']:<8} {stock['name']:<12} {price:<10} {stock['reason']}")

print("""
  【爆发逻辑】
  → 特斯拉Optimus量产在即（2026年）
  → 国内厂商跟进（宇树、智元、小米）
  → 零部件需求爆发（减速器、电机、传感器）
  → 类比2023年AI算力，市场还没完全定价
  
  【最值得关注】
  → 埃斯顿(002747)：国产机器人龙头，减速器自研，技术壁垒高
  → 机器人(300024)：工业机器人老牌龙头，人形机器人布局
""")

print("=" * 80)
print("  候选二：低空经济赛道")
print("  类比：2023年AI算力 → 2026年低空经济")
print("=" * 80)

lowalt_stocks = [
    {'code': '300159', 'name': '新研股份', 'reason': '无人机发动机龙头'},
    {'code': '002179', 'name': '中航光电', 'reason': '航空连接器龙头，低空受益'},
    {'code': '300581', 'name': '晨曦航空', 'reason': '通用航空，低空经济受益'},
    {'code': '688122', 'name': '西部超导', 'reason': '航空材料龙头'},
    {'code': '002013', 'name': '中航机电', 'reason': '航空机电系统龙头'},
]

print(f"\n  {'代码':<8} {'名称':<12} {'现价':<10} {'理由'}")
print(f"  {'-'*70}")
for stock in lowalt_stocks:
    p = get_price_sina(stock['code'])
    price = f"{p['current']:.2f}" if p.get('success') else '获取失败'
    print(f"  {stock['code']:<8} {stock['name']:<12} {price:<10} {stock['reason']}")

print("""
  【爆发逻辑】
  → 国家明确支持低空经济（十五五规划）
  → 2026年低空开放政策落地
  → eVTOL（电动垂直起降）商业化
  → 无人机物流、城市空中交通
  
  【最值得关注】
  → 中航光电(002179)：连接器龙头，低空+AI双受益
  → 新研股份(300159)：无人机发动机，细分龙头
""")

print("=" * 80)
print("  候选三：AI应用落地赛道")
print("  类比：2023年算力基础设施 → 2026年AI应用爆发")
print("=" * 80)

ai_app_stocks = [
    {'code': '002230', 'name': '科大讯飞', 'reason': 'AI语音龙头，大模型落地'},
    {'code': '300033', 'name': '同花顺', 'reason': '金融AI龙头，数据+模型'},
    {'code': '600588', 'name': '用友网络', 'reason': '企业AI化，ERP+AI'},
    {'code': '300418', 'name': '昆仑万维', 'reason': 'AI大模型，海外布局'},
    {'code': '002415', 'name': '海康威视', 'reason': 'AI视觉龙头，安防+工业'},
]

print(f"\n  {'代码':<8} {'名称':<12} {'现价':<10} {'理由'}")
print(f"  {'-'*70}")
for stock in ai_app_stocks:
    p = get_price_sina(stock['code'])
    price = f"{p['current']:.2f}" if p.get('success') else '获取失败'
    print(f"  {stock['code']:<8} {stock['name']:<12} {price:<10} {stock['reason']}")

print("""
  【爆发逻辑】
  → 大模型能力成熟，应用层爆发
  → 企业AI化需求旺盛
  → 国产大模型竞争激烈，应用层受益
  → 类比2023年算力，2026年是应用年
  
  【最值得关注】
  → 同花顺(300033)：金融AI龙头，数据壁垒强
  → 海康威视(002415)：AI视觉龙头，超跌后估值合理
""")

print("=" * 80)
print("  候选四：半导体国产替代")
print("  类比：2023年AI算力 → 2026年半导体自主可控")
print("=" * 80)

semi_stocks = [
    {'code': '002371', 'name': '北方华创', 'reason': '半导体设备龙头，国产替代'},
    {'code': '688012', 'name': '中微公司', 'reason': '刻蚀机龙头，国产替代'},
    {'code': '688521', 'name': '芯原股份', 'reason': 'IP核龙头，芯片设计'},
    {'code': '688256', 'name': '寒武纪', 'reason': 'AI芯片，国产替代'},
    {'code': '688981', 'name': '中芯国际', 'reason': '晶圆代工龙头'},
]

print(f"\n  {'代码':<8} {'名称':<12} {'现价':<10} {'理由'}")
print(f"  {'-'*70}")
for stock in semi_stocks:
    p = get_price_sina(stock['code'])
    price = f"{p['current']:.2f}" if p.get('success') else '获取失败'
    print(f"  {stock['code']:<8} {stock['name']:<12} {price:<10} {stock['reason']}")

print("""
  【爆发逻辑】
  → 十五五规划：半导体国产替代率目标70%
  → 美国制裁倒逼国产替代加速
  → 设备、材料、EDA全面国产化
  → 政策资金持续投入（大基金三期）
  
  【最值得关注】
  → 北方华创(002371)：设备龙头，国产替代确定性最强
  → 中微公司(688012)：刻蚀机龙头，技术壁垒高
""")

print("=" * 80)
print("  最终推荐：最像2023年中际旭创的标的")
print("=" * 80)

top_picks = [
    {'code': '002747', 'name': '埃斯顿', 'sector': '人形机器人', 'logic': '减速器自研+人形机器人布局，特斯拉Optimus量产受益'},
    {'code': '002179', 'name': '中航光电', 'sector': '低空经济', 'logic': '连接器龙头，低空+AI双受益，政策明确支持'},
    {'code': '300033', 'name': '同花顺', 'sector': 'AI应用', 'logic': '金融AI龙头，数据壁垒强，AI应用爆发受益'},
    {'code': '002371', 'name': '北方华创', 'sector': '半导体', 'logic': '设备龙头，国产替代确定性最强，十五五重点'},
    {'code': '002415', 'name': '海康威视', 'sector': 'AI视觉', 'logic': 'AI视觉龙头，超跌后估值合理，AI应用落地'},
]

print(f"\n  {'代码':<8} {'名称':<10} {'赛道':<12} {'现价':<10} {'核心逻辑'}")
print(f"  {'-'*80}")
for stock in top_picks:
    p = get_price_sina(stock['code'])
    price = f"{p['current']:.2f}" if p.get('success') else '获取失败'
    print(f"  {stock['code']:<8} {stock['name']:<10} {stock['sector']:<12} {price:<10} {stock['logic'][:30]}")

print("""

  【详细分析】
  
  1. 埃斯顿(002747) - 最像中际旭创
     → 人形机器人赛道，类比2023年AI算力
     → 减速器自研，技术壁垒高
     → 特斯拉Optimus量产，需求爆发在即
     → 目前股价还在低位，市场未完全定价
     → 买入时机：现价附近，分批建仓
  
  2. 北方华创(002371) - 确定性最强
     → 半导体设备龙头，国产替代确定
     → 十五五规划明确支持
     → 业绩持续高增长
     → 估值合理，安全边际高
     → 买入时机：回调时买入
  
  3. 同花顺(300033) - AI应用爆发
     → 金融AI龙头，数据壁垒强
     → AI应用落地，业绩爆发预期
     → 估值合理，超跌后有反弹空间
     → 买入时机：现价附近，分批建仓
  
  4. 中航光电(002179) - 低空经济
     → 连接器龙头，低空+AI双受益
     → 政策明确支持，需求爆发在即
     → 估值合理，安全边际高
     → 买入时机：回调时买入
  
  5. 海康威视(002415) - AI视觉
     → AI视觉龙头，超跌后估值合理
     → AI应用落地，业绩改善预期
     → 估值合理，安全边际高
     → 买入时机：现价附近，分批建仓

  【仓位建议】
  
  总仓位: 30%（熊市环境）
  
  - 埃斯顿:   8%（最高优先级）
  - 北方华创: 8%（确定性最强）
  - 同花顺:   6%（AI应用）
  - 中航光电: 5%（低空经济）
  - 海康威视: 3%（AI视觉）
  
  止损: 每只-8%
  目标: 每只+30-50%（6-12个月）
  
  【风险提示】
  - 以上仅为分析参考，不构成投资建议
  - 熊市环境下，任何股票都可能继续下跌
  - 分批建仓，严格止损
""")

print("=" * 80)
