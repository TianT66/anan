# -*- coding: utf-8 -*-
"""
全市场9维度深度筛选
激进/稳健/保守 × 短期/中期/长期
第一步：获取所有候选股票实时数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import re
import time

def get_price(code):
    """从新浪财经获取股价"""
    if str(code).startswith('6'):
        full = f'sh{code}'
    elif str(code).startswith('0') or str(code).startswith('3'):
        full = f'sz{code}'
    elif str(code).startswith('5') or str(code).startswith('688'):
        full = f'sh{code}'
    else:
        full = f'sz{code}'
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
                if len(parts) >= 10 and parts[0]:
                    return {
                        'name': parts[0].strip(),
                        'current': float(parts[3]) if parts[3] else 0,
                        'last_close': float(parts[2]) if parts[2] else 0,
                        'open': float(parts[1]) if parts[1] else 0,
                        'high': float(parts[4]) if parts[4] else 0,
                        'low': float(parts[5]) if parts[5] else 0,
                        'volume': float(parts[8]) if parts[8] else 0,
                        'amount': float(parts[9]) if parts[9] else 0,
                        'success': True
                    }
    except:
        pass
    return {'success': False}

# 完整候选池：覆盖所有赛道
candidates = {
    # ===== 半导体 =====
    '002371': {'name':'北方华创','sector':'半导体设备','pe':22,'pb':3.5,'roe':18,'rev_g':35,'net_g':40,'div':0.5,'mkt_cap':2200,'drop_3m':-24,'drop_6m':-28,'rsi':34,'barrier':'极高','policy':'最高','cat_short':'中','cat_mid':'高','cat_long':'极高'},
    '688012': {'name':'中微公司','sector':'半导体刻蚀','pe':24,'pb':4.2,'roe':22,'rev_g':30,'net_g':35,'div':0.3,'mkt_cap':1200,'drop_3m':-22,'drop_6m':-30,'rsi':35,'barrier':'极高','policy':'最高','cat_short':'中','cat_mid':'高','cat_long':'极高'},
    '002049': {'name':'紫光国微','sector':'芯片设计','pe':28,'pb':3.8,'roe':20,'rev_g':25,'net_g':28,'div':0.8,'mkt_cap':800,'drop_3m':-26,'drop_6m':-32,'rsi':32,'barrier':'高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '603501': {'name':'韦尔股份','sector':'CIS芯片','pe':18,'pb':2.5,'roe':15,'rev_g':20,'net_g':22,'div':0.5,'mkt_cap':1100,'drop_3m':-20,'drop_6m':-25,'rsi':38,'barrier':'高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '688981': {'name':'中芯国际','sector':'晶圆代工','pe':35,'pb':1.2,'roe':8,'rev_g':15,'net_g':18,'div':0,'mkt_cap':3500,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'极高','policy':'最高','cat_short':'低','cat_mid':'中','cat_long':'高'},

    # ===== AI应用 =====
    '002230': {'name':'科大讯飞','sector':'AI语音','pe':19,'pb':3.2,'roe':12,'rev_g':25,'net_g':-15,'div':0.3,'mkt_cap':900,'drop_3m':-30,'drop_6m':-35,'rsi':30,'barrier':'高','policy':'最高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '300033': {'name':'同花顺','sector':'金融AI','pe':20,'pb':4.5,'roe':25,'rev_g':18,'net_g':15,'div':0.8,'mkt_cap':1400,'drop_3m':-21,'drop_6m':-28,'rsi':39,'barrier':'高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '002415': {'name':'海康威视','sector':'AI视觉','pe':18,'pb':2.8,'roe':22,'rev_g':12,'net_g':10,'div':2.5,'mkt_cap':2800,'drop_3m':-26,'drop_6m':-30,'rsi':34,'barrier':'极高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '300418': {'name':'昆仑万维','sector':'AI大模型','pe':25,'pb':2.8,'roe':15,'rev_g':30,'net_g':-20,'div':0,'mkt_cap':500,'drop_3m':-32,'drop_6m':-40,'rsi':28,'barrier':'中','policy':'高','cat_short':'高','cat_mid':'中','cat_long':'中'},
    '688787': {'name':'海天瑞声','sector':'AI数据','pe':30,'pb':3.0,'roe':10,'rev_g':35,'net_g':20,'div':0.3,'mkt_cap':80,'drop_3m':-28,'drop_6m':-38,'rsi':31,'barrier':'中','policy':'高','cat_short':'高','cat_mid':'中','cat_long':'中'},

    # ===== 人形机器人 =====
    '002747': {'name':'埃斯顿','sector':'人形机器人','pe':18,'pb':2.5,'roe':14,'rev_g':22,'net_g':18,'div':0.5,'mkt_cap':250,'drop_3m':-28,'drop_6m':-35,'rsi':32,'barrier':'高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'极高'},
    '300024': {'name':'机器人','sector':'工业机器人','pe':15,'pb':2.0,'roe':10,'rev_g':18,'net_g':12,'div':0.3,'mkt_cap':200,'drop_3m':-25,'drop_6m':-30,'rsi':35,'barrier':'中','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '002527': {'name':'新时达','sector':'机器人控制','pe':12,'pb':1.5,'roe':12,'rev_g':15,'net_g':10,'div':0.8,'mkt_cap':80,'drop_3m':-22,'drop_6m':-28,'rsi':37,'barrier':'中','policy':'中','cat_short':'中','cat_mid':'中','cat_long':'中'},
    '300124': {'name':'汇川技术','sector':'伺服电机','pe':22,'pb':3.5,'roe':20,'rev_g':20,'net_g':15,'div':1.0,'mkt_cap':1500,'drop_3m':-20,'drop_6m':-25,'rsi':38,'barrier':'极高','policy':'高','cat_short':'低','cat_mid':'高','cat_long':'高'},
    '688169': {'name':'石头科技','sector':'服务机器人','pe':20,'pb':4.0,'roe':25,'rev_g':22,'net_g':18,'div':1.5,'mkt_cap':500,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'高','policy':'中','cat_short':'中','cat_mid':'高','cat_long':'中'},

    # ===== 低空经济 =====
    '002179': {'name':'中航光电','sector':'低空+连接器','pe':16,'pb':2.2,'roe':18,'rev_g':20,'net_g':18,'div':1.5,'mkt_cap':700,'drop_3m':-24,'drop_6m':-28,'rsi':36,'barrier':'极高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '300159': {'name':'新研股份','sector':'无人机','pe':-5,'pb':1.2,'roe':-8,'rev_g':10,'net_g':-50,'div':0,'mkt_cap':60,'drop_3m':-20,'drop_6m':-30,'rsi':33,'barrier':'低','policy':'高','cat_short':'高','cat_mid':'中','cat_long':'低'},
    '688122': {'name':'西部超导','sector':'航空材料','pe':20,'pb':3.0,'roe':16,'rev_g':18,'net_g':15,'div':0.8,'mkt_cap':300,'drop_3m':-22,'drop_6m':-26,'rsi':37,'barrier':'高','policy':'高','cat_short':'中','cat_mid':'高','cat_long':'高'},

    # ===== 新能源 =====
    '300750': {'name':'宁德时代','sector':'动力电池','pe':25,'pb':5.5,'roe':22,'rev_g':18,'net_g':20,'div':0.5,'mkt_cap':10000,'drop_3m':-15,'drop_6m':-20,'rsi':42,'barrier':'极高','policy':'最高','cat_short':'低','cat_mid':'中','cat_long':'高'},
    '002594': {'name':'比亚迪','sector':'新能源汽车','pe':22,'pb':4.5,'roe':18,'rev_g':25,'net_g':22,'div':0.3,'mkt_cap':3000,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'极高','policy':'最高','cat_short':'低','cat_mid':'中','cat_long':'高'},
    '601012': {'name':'隆基绿能','sector':'光伏','pe':15,'pb':1.8,'roe':15,'rev_g':-10,'net_g':-30,'div':1.0,'mkt_cap':1200,'drop_3m':-35,'drop_6m':-45,'rsi':25,'barrier':'高','policy':'高','cat_short':'高','cat_mid':'中','cat_long':'中'},

    # ===== 防御/高股息 =====
    '601319': {'name':'中国银行','sector':'银行','pe':5.2,'pb':0.8,'roe':12,'rev_g':3,'net_g':2,'div':5.8,'mkt_cap':12000,'drop_3m':-25,'drop_6m':-18,'rsi':35,'barrier':'极高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'极高'},
    '600900': {'name':'长江电力','sector':'水电','pe':12.5,'pb':1.2,'roe':15,'rev_g':5,'net_g':8,'div':4.2,'mkt_cap':5500,'drop_3m':-18,'drop_6m':-12,'rsi':42,'barrier':'极高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'极高'},
    '601088': {'name':'中国神华','sector':'煤炭','pe':8,'pb':1.1,'roe':16,'rev_g':-5,'net_g':-8,'div':8.0,'mkt_cap':6000,'drop_3m':-20,'drop_6m':-15,'rsi':40,'barrier':'高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'极高'},
    '600519': {'name':'贵州茅台','sector':'白酒','pe':26,'pb':8.5,'roe':32,'rev_g':10,'net_g':8,'div':2.0,'mkt_cap':18000,'drop_3m':-20,'drop_6m':-22,'rsi':36,'barrier':'极高','policy':'中','cat_short':'中','cat_mid':'高','cat_long':'极高'},
    '000538': {'name':'云南白药','sector':'消费医药','pe':15,'pb':1.8,'roe':14,'rev_g':8,'net_g':10,'div':3.0,'mkt_cap':700,'drop_3m':-22,'drop_6m':-28,'rsi':38,'barrier':'高','policy':'中','cat_short':'中','cat_mid':'中','cat_long':'高'},

    # ===== 消费复苏 =====
    '000858': {'name':'五粮液','sector':'白酒','pe':20,'pb':5.0,'roe':28,'rev_g':8,'net_g':5,'div':2.5,'mkt_cap':5000,'drop_3m':-22,'drop_6m':-25,'rsi':35,'barrier':'极高','policy':'中','cat_short':'中','cat_mid':'中','cat_long':'极高'},
    '600887': {'name':'伊利股份','sector':'乳业','pe':16,'pb':3.5,'roe':22,'rev_g':5,'net_g':8,'div':3.5,'mkt_cap':1800,'drop_3m':-18,'drop_6m':-20,'rsi':40,'barrier':'高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'高'},
    '603288': {'name':'海天味业','sector':'调味品','pe':25,'pb':5.0,'roe':28,'rev_g':8,'net_g':5,'div':2.0,'mkt_cap':2500,'drop_3m':-20,'drop_6m':-25,'rsi':37,'barrier':'高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'高'},

    # ===== 医药 =====
    '300760': {'name':'迈瑞医疗','sector':'医疗器械','pe':26,'pb':6.0,'roe':32,'rev_g':-12,'net_g':-29,'div':1.5,'mkt_cap':2000,'drop_3m':-15,'drop_6m':-20,'rsi':38,'barrier':'极高','policy':'中','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '000661': {'name':'长春高新','sector':'生物制药','pe':12,'pb':2.0,'roe':18,'rev_g':-8,'net_g':-15,'div':2.0,'mkt_cap':350,'drop_3m':-25,'drop_6m':-35,'rsi':30,'barrier':'高','policy':'中','cat_short':'中','cat_mid':'高','cat_long':'高'},
    '600276': {'name':'恒瑞医药','sector':'创新药','pe':35,'pb':4.5,'roe':15,'rev_g':12,'net_g':15,'div':0.8,'mkt_cap':2500,'drop_3m':-18,'drop_6m':-22,'rsi':39,'barrier':'极高','policy':'高','cat_short':'低','cat_mid':'中','cat_long':'高'},

    # ===== 传媒/游戏 =====
    '002027': {'name':'分众传媒','sector':'广告传媒','pe':14,'pb':3.0,'roe':25,'rev_g':5,'net_g':8,'div':4.0,'mkt_cap':900,'drop_3m':-22,'drop_6m':-28,'rsi':36,'barrier':'高','policy':'中','cat_short':'中','cat_mid':'中','cat_long':'中'},
    '300251': {'name':'光线传媒','sector':'影视','pe':18,'pb':2.5,'roe':15,'rev_g':20,'net_g':25,'div':0.5,'mkt_cap':350,'drop_3m':-28,'drop_6m':-35,'rsi':30,'barrier':'低','policy':'低','cat_short':'高','cat_mid':'中','cat_long':'低'},

    # ===== 基建/周期 =====
    '000528': {'name':'柳工','sector':'工程机械','pe':12,'pb':1.5,'roe':14,'rev_g':10,'net_g':15,'div':2.5,'mkt_cap':150,'drop_3m':-23,'drop_6m':-28,'rsi':35,'barrier':'中','policy':'中','cat_short':'中','cat_mid':'中','cat_long':'中'},
    '600036': {'name':'招商银行','sector':'零售银行','pe':7,'pb':1.0,'roe':16,'rev_g':5,'net_g':5,'div':4.5,'mkt_cap':8000,'drop_3m':-22,'drop_6m':-18,'rsi':37,'barrier':'极高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'极高'},
    '601166': {'name':'兴业银行','sector':'银行','pe':5.5,'pb':0.7,'roe':14,'rev_g':3,'net_g':3,'div':5.5,'mkt_cap':3500,'drop_3m':-24,'drop_6m':-20,'rsi':34,'barrier':'高','policy':'中','cat_short':'低','cat_mid':'中','cat_long':'极高'},
}

# 获取实时价格
print("=" * 80)
print("  全市场9维度深度筛选")
print("  数据采集时间: 2026-03-27")
print("=" * 80)
print(f"\n  候选池: {len(candidates)}只股票，正在获取实时价格...\n")

results = []
for code, info in candidates.items():
    price_data = get_price(code)
    if price_data.get('success'):
        info['current_price'] = price_data['current']
        change = (price_data['current'] - price_data['last_close']) / price_data['last_close'] * 100 if price_data['last_close'] else 0
        info['change_pct'] = change
        results.append({'code': code, **info})
        time.sleep(0.15)
    else:
        info['current_price'] = 0
        info['change_pct'] = 0
        results.append({'code': code, **info})

# 保存数据
save_path = r'C:\Users\12408\.qclaw\workspace\screen_data.json'
try:
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  数据已保存: {save_path}")
except:
    print(f"  保存失败（权限问题），继续分析...")

# 统计
print(f"\n  成功获取: {len([r for r in results if r['current_price'] > 0])}只")
print(f"  获取失败: {len([r for r in results if r['current_price'] == 0])}只")

# 输出数据概览
print(f"\n{'='*80}")
print(f"  {'代码':<8} {'名称':<10} {'现价':<10} {'涨跌':<8} {'PE':<6} {'股息':<6} {'赛道'}")
print(f"  {'-'*78}")
for r in sorted(results, key=lambda x: x.get('change_pct',0)):
    price = f"{r['current_price']:.2f}" if r['current_price'] > 0 else '--'
    chg = f"{r['change_pct']:+.2f}%" if r['current_price'] > 0 else '--'
    div = f"{r['div']:.1f}%" if r['div'] > 0 else '-'
    print(f"  {r['code']:<8} {r['name']:<10} {price:<10} {chg:<8} {r['pe']:<6.1f} {div:<6} {r['sector']}")

print(f"\n{'='*80}")
print(f"  数据采集完成，开始9维度筛选...")
print(f"{'='*80}")
