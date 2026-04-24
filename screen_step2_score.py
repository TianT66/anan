# -*- coding: utf-8 -*-
"""
全市场9维度深度筛选 - 第二步：评分模型 + 9维度推荐
激进/稳健/保守 × 短期/中期/长期
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import time

# 37只股票完整数据
stocks = [
    {'code':'002371','name':'北方华创','sector':'半导体设备','pe':22,'pb':3.5,'roe':18,'rev_g':35,'net_g':40,'div':0.5,'mkt_cap':2200,'drop_3m':-24,'drop_6m':-28,'rsi':34,'barrier':'极高','policy':'最高','price':446.11,'chg':-3.90},
    {'code':'688012','name':'中微公司','sector':'半导体刻蚀','pe':24,'pb':4.2,'roe':22,'rev_g':30,'net_g':35,'div':0.3,'mkt_cap':1200,'drop_3m':-22,'drop_6m':-30,'rsi':35,'barrier':'极高','policy':'最高','price':306.00,'chg':-1.79},
    {'code':'002049','name':'紫光国微','sector':'芯片设计','pe':28,'pb':3.8,'roe':20,'rev_g':25,'net_g':28,'div':0.8,'mkt_cap':800,'drop_3m':-26,'drop_6m':-32,'rsi':32,'barrier':'高','policy':'高','price':67.72,'chg':-1.83},
    {'code':'603501','name':'韦尔股份','sector':'CIS芯片','pe':18,'pb':2.5,'roe':15,'rev_g':20,'net_g':22,'div':0.5,'mkt_cap':1100,'drop_3m':-20,'drop_6m':-25,'rsi':38,'barrier':'高','policy':'高','price':100.00,'chg':-2.30},
    {'code':'688981','name':'中芯国际','sector':'晶圆代工','pe':35,'pb':1.2,'roe':8,'rev_g':15,'net_g':18,'div':0,'mkt_cap':3500,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'极高','policy':'最高','price':96.88,'chg':-3.11},
    {'code':'002230','name':'科大讯飞','sector':'AI语音','pe':19,'pb':3.2,'roe':12,'rev_g':25,'net_g':-15,'div':0.3,'mkt_cap':900,'drop_3m':-30,'drop_6m':-35,'rsi':30,'barrier':'高','policy':'最高','price':46.57,'chg':-2.10},
    {'code':'300033','name':'同花顺','sector':'金融AI','pe':20,'pb':4.5,'roe':25,'rev_g':18,'net_g':15,'div':0.8,'mkt_cap':1400,'drop_3m':-21,'drop_6m':-28,'rsi':39,'barrier':'高','policy':'高','price':296.84,'chg':-4.74},
    {'code':'002415','name':'海康威视','sector':'AI视觉','pe':18,'pb':2.8,'roe':22,'rev_g':12,'net_g':10,'div':2.5,'mkt_cap':2800,'drop_3m':-26,'drop_6m':-30,'rsi':34,'barrier':'极高','policy':'高','price':30.37,'chg':-1.33},
    {'code':'300418','name':'昆仑万维','sector':'AI大模型','pe':25,'pb':2.8,'roe':15,'rev_g':30,'net_g':-20,'div':0,'mkt_cap':500,'drop_3m':-32,'drop_6m':-40,'rsi':28,'barrier':'中','policy':'高','price':50.70,'chg':-0.35},
    {'code':'688787','name':'海天瑞声','sector':'AI数据','pe':30,'pb':3.0,'roe':10,'rev_g':35,'net_g':20,'div':0.3,'mkt_cap':80,'drop_3m':-28,'drop_6m':-38,'rsi':31,'barrier':'中','policy':'高','price':135.67,'chg':-3.09},
    {'code':'002747','name':'埃斯顿','sector':'人形机器人','pe':18,'pb':2.5,'roe':14,'rev_g':22,'net_g':18,'div':0.5,'mkt_cap':250,'drop_3m':-28,'drop_6m':-35,'rsi':32,'barrier':'高','policy':'高','price':20.09,'chg':-0.94},
    {'code':'300024','name':'机器人','sector':'工业机器人','pe':15,'pb':2.0,'roe':10,'rev_g':18,'net_g':12,'div':0.3,'mkt_cap':200,'drop_3m':-25,'drop_6m':-30,'rsi':35,'barrier':'中','policy':'高','price':14.88,'chg':-1.26},
    {'code':'002527','name':'新时达','sector':'机器人控制','pe':12,'pb':1.5,'roe':12,'rev_g':15,'net_g':10,'div':0.8,'mkt_cap':80,'drop_3m':-22,'drop_6m':-28,'rsi':37,'barrier':'中','policy':'中','price':13.51,'chg':-1.82},
    {'code':'300124','name':'汇川技术','sector':'伺服电机','pe':22,'pb':3.5,'roe':20,'rev_g':20,'net_g':15,'div':1.0,'mkt_cap':1500,'drop_3m':-20,'drop_6m':-25,'rsi':38,'barrier':'极高','policy':'高','price':67.52,'chg':-0.72},
    {'code':'688169','name':'石头科技','sector':'服务机器人','pe':20,'pb':4.0,'roe':25,'rev_g':22,'net_g':18,'div':1.5,'mkt_cap':500,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'高','policy':'中','price':122.50,'chg':-1.91},
    {'code':'002179','name':'中航光电','sector':'低空+连接器','pe':16,'pb':2.2,'roe':18,'rev_g':20,'net_g':18,'div':1.5,'mkt_cap':700,'drop_3m':-24,'drop_6m':-28,'rsi':36,'barrier':'极高','policy':'高','price':33.39,'chg':-1.01},
    {'code':'300159','name':'新研股份','sector':'无人机','pe':-5,'pb':1.2,'roe':-8,'rev_g':10,'net_g':-50,'div':0,'mkt_cap':60,'drop_3m':-20,'drop_6m':-30,'rsi':33,'barrier':'低','policy':'高','price':2.99,'chg':-0.99},
    {'code':'688122','name':'西部超导','sector':'航空材料','pe':20,'pb':3.0,'roe':16,'rev_g':18,'net_g':15,'div':0.8,'mkt_cap':300,'drop_3m':-22,'drop_6m':-26,'rsi':37,'barrier':'高','policy':'高','price':71.85,'chg':0.32},
    {'code':'300750','name':'宁德时代','sector':'动力电池','pe':25,'pb':5.5,'roe':22,'rev_g':18,'net_g':20,'div':0.5,'mkt_cap':10000,'drop_3m':-15,'drop_6m':-20,'rsi':42,'barrier':'极高','policy':'最高','price':402.50,'chg':1.18},
    {'code':'002594','name':'比亚迪','sector':'新能源汽车','pe':22,'pb':4.5,'roe':18,'rev_g':25,'net_g':22,'div':0.3,'mkt_cap':3000,'drop_3m':-18,'drop_6m':-22,'rsi':40,'barrier':'极高','policy':'最高','price':103.14,'chg':-3.25},
    {'code':'601012','name':'隆基绿能','sector':'光伏','pe':15,'pb':1.8,'roe':15,'rev_g':-10,'net_g':-30,'div':1.0,'mkt_cap':1200,'drop_3m':-35,'drop_6m':-45,'rsi':25,'barrier':'高','policy':'高','price':18.37,'chg':-2.75},
    {'code':'601319','name':'中国银行','sector':'银行','pe':5.2,'pb':0.8,'roe':12,'rev_g':3,'net_g':2,'div':5.8,'mkt_cap':12000,'drop_3m':-25,'drop_6m':-18,'rsi':35,'barrier':'极高','policy':'中','price':7.76,'chg':-3.60},
    {'code':'600900','name':'长江电力','sector':'水电','pe':12.5,'pb':1.2,'roe':15,'rev_g':5,'net_g':8,'div':4.2,'mkt_cap':5500,'drop_3m':-18,'drop_6m':-12,'rsi':42,'barrier':'极高','policy':'中','price':27.31,'chg':0.37},
    {'code':'601088','name':'中国神华','sector':'煤炭','pe':8,'pb':1.1,'roe':16,'rev_g':-5,'net_g':-8,'div':8.0,'mkt_cap':6000,'drop_3m':-20,'drop_6m':-15,'rsi':40,'barrier':'高','policy':'中','price':47.69,'chg':0.93},
    {'code':'600519','name':'贵州茅台','sector':'白酒','pe':26,'pb':8.5,'roe':32,'rev_g':10,'net_g':8,'div':2.0,'mkt_cap':18000,'drop_3m':-20,'drop_6m':-22,'rsi':36,'barrier':'极高','policy':'中','price':1401.18,'chg':-0.64},
    {'code':'000538','name':'云南白药','sector':'消费医药','pe':15,'pb':1.8,'roe':14,'rev_g':8,'net_g':10,'div':3.0,'mkt_cap':700,'drop_3m':-22,'drop_6m':-28,'rsi':38,'barrier':'高','policy':'中','price':54.26,'chg':-2.04},
    {'code':'000858','name':'五粮液','sector':'白酒','pe':20,'pb':5.0,'roe':28,'rev_g':8,'net_g':5,'div':2.5,'mkt_cap':5000,'drop_3m':-22,'drop_6m':-25,'rsi':35,'barrier':'极高','policy':'中','price':101.28,'chg':-1.14},
    {'code':'600887','name':'伊利股份','sector':'乳业','pe':16,'pb':3.5,'roe':22,'rev_g':5,'net_g':8,'div':3.5,'mkt_cap':1800,'drop_3m':-18,'drop_6m':-20,'rsi':40,'barrier':'高','policy':'中','price':25.95,'chg':0.27},
    {'code':'603288','name':'海天味业','sector':'调味品','pe':25,'pb':5.0,'roe':28,'rev_g':8,'net_g':5,'div':2.0,'mkt_cap':2500,'drop_3m':-20,'drop_6m':-25,'rsi':37,'barrier':'高','policy':'中','price':36.95,'chg':-0.14},
    {'code':'300760','name':'迈瑞医疗','sector':'医疗器械','pe':26,'pb':6.0,'roe':32,'rev_g':-12,'net_g':-29,'div':1.5,'mkt_cap':2000,'drop_3m':-15,'drop_6m':-20,'rsi':38,'barrier':'极高','policy':'中','price':164.30,'chg':-1.89},
    {'code':'000661','name':'长春高新','sector':'生物制药','pe':12,'pb':2.0,'roe':18,'rev_g':-8,'net_g':-15,'div':2.0,'mkt_cap':350,'drop_3m':-25,'drop_6m':-35,'rsi':30,'barrier':'高','policy':'中','price':84.70,'chg':-1.29},
    {'code':'600276','name':'恒瑞医药','sector':'创新药','pe':35,'pb':4.5,'roe':15,'rev_g':12,'net_g':15,'div':0.8,'mkt_cap':2500,'drop_3m':-18,'drop_6m':-22,'rsi':39,'barrier':'极高','policy':'高','price':51.63,'chg':-4.57},
    {'code':'002027','name':'分众传媒','sector':'广告传媒','pe':14,'pb':3.0,'roe':25,'rev_g':5,'net_g':8,'div':4.0,'mkt_cap':900,'drop_3m':-22,'drop_6m':-28,'rsi':36,'barrier':'高','policy':'中','price':6.42,'chg':-0.47},
    {'code':'300251','name':'光线传媒','sector':'影视','pe':18,'pb':2.5,'roe':15,'rev_g':20,'net_g':25,'div':0.5,'mkt_cap':350,'drop_3m':-28,'drop_6m':-35,'rsi':30,'barrier':'低','policy':'低','price':14.81,'chg':-2.76},
    {'code':'000528','name':'柳工','sector':'工程机械','pe':12,'pb':1.5,'roe':14,'rev_g':10,'net_g':15,'div':2.5,'mkt_cap':150,'drop_3m':-23,'drop_6m':-28,'rsi':35,'barrier':'中','policy':'中','price':9.32,'chg':-1.79},
    {'code':'600036','name':'招商银行','sector':'零售银行','pe':7,'pb':1.0,'roe':16,'rev_g':5,'net_g':5,'div':4.5,'mkt_cap':8000,'drop_3m':-22,'drop_6m':-18,'rsi':37,'barrier':'极高','policy':'中','price':39.56,'chg':0.76},
    {'code':'601166','name':'兴业银行','sector':'银行','pe':5.5,'pb':0.7,'roe':14,'rev_g':3,'net_g':3,'div':5.5,'mkt_cap':3500,'drop_3m':-24,'drop_6m':-20,'rsi':34,'barrier':'高','policy':'中','price':18.88,'chg':0.64},
]

# ============================================================
# 评分模型
# ============================================================

def score_valuation(s):
    """估值评分 0-100"""
    score = 0
    pe = abs(s['pe']) if s['pe'] < 0 else s['pe']
    if pe <= 8: score += 30
    elif pe <= 12: score += 25
    elif pe <= 16: score += 20
    elif pe <= 20: score += 15
    elif pe <= 25: score += 10
    elif pe <= 35: score += 5
    else: score += 0
    
    if s['pb'] <= 1.0: score += 25
    elif s['pb'] <= 1.5: score += 22
    elif s['pb'] <= 2.0: score += 18
    elif s['pb'] <= 3.0: score += 12
    elif s['pb'] <= 4.0: score += 8
    else: score += 4
    
    if s['div'] >= 5: score += 25
    elif s['div'] >= 3: score += 20
    elif s['div'] >= 2: score += 15
    elif s['div'] >= 1: score += 10
    elif s['div'] >= 0.5: score += 5
    else: score += 0
    
    # 亏损扣分
    if s['net_g'] < 0: score -= 15
    
    return max(0, min(100, score))

def score_growth(s):
    """成长性评分 0-100"""
    score = 0
    if s['net_g'] >= 40: score += 35
    elif s['net_g'] >= 25: score += 30
    elif s['net_g'] >= 15: score += 22
    elif s['net_g'] >= 8: score += 15
    elif s['net_g'] >= 0: score += 8
    else: score += 0  # 亏损不加分但也不扣
    
    if s['rev_g'] >= 30: score += 25
    elif s['rev_g'] >= 20: score += 20
    elif s['rev_g'] >= 10: score += 15
    elif s['rev_g'] >= 5: score += 10
    else: score += 5
    
    if s['roe'] >= 25: score += 25
    elif s['roe'] >= 20: score += 20
    elif s['roe'] >= 15: score += 15
    elif s['roe'] >= 10: score += 10
    else: score += 5
    
    if s['net_g'] < 0: score -= 10
    if s['rev_g'] < 0: score -= 5
    
    return max(0, min(100, score))

def score_technical(s):
    """技术面评分 0-100"""
    score = 0
    # 超跌程度（跌越多，反弹空间越大）
    drop = abs(s['drop_6m'])
    if drop >= 40: score += 35
    elif drop >= 30: score += 30
    elif drop >= 20: score += 25
    elif drop >= 15: score += 18
    else: score += 10
    
    # RSI超卖
    if s['rsi'] <= 25: score += 30
    elif s['rsi'] <= 30: score += 27
    elif s['rsi'] <= 35: score += 22
    elif s['rsi'] <= 40: score += 15
    elif s['rsi'] <= 45: score += 8
    else: score += 3
    
    # 短期超跌
    drop3 = abs(s['drop_3m'])
    if drop3 >= 30: score += 25
    elif drop3 >= 25: score += 20
    elif drop3 >= 20: score += 15
    else: score += 8
    
    return max(0, min(100, score))

def score_quality(s):
    """基本面质量评分 0-100"""
    score = 0
    
    # 护城河
    barrier_map = {'极高': 30, '高': 22, '中': 12, '低': 5}
    score += barrier_map.get(s['barrier'], 10)
    
    # ROE
    if s['roe'] >= 25: score += 25
    elif s['roe'] >= 20: score += 20
    elif s['roe'] >= 15: score += 15
    elif s['roe'] >= 10: score += 10
    else: score += 5
    
    # 市值（流动性）
    if s['mkt_cap'] >= 1000: score += 20
    elif s['mkt_cap'] >= 500: score += 16
    elif s['mkt_cap'] >= 200: score += 12
    elif s['mkt_cap'] >= 100: score += 8
    else: score += 5
    
    # 盈利稳定性
    if s['net_g'] >= 10: score += 15
    elif s['net_g'] >= 0: score += 10
    elif s['net_g'] >= -15: score += 5
    else: score += 0
    
    return max(0, min(100, score))

def score_policy(s):
    """政策面评分 0-100"""
    policy_map = {'最高': 50, '高': 35, '中': 20, '低': 5}
    score = policy_map.get(s['policy'], 15)
    
    # 十五五重点加分
    hot_sectors = ['半导体', 'AI', '机器人', '低空', '新能源', '创新药']
    sector_bonus = sum(10 for h in hot_sectors if h in s['sector'])
    score += min(30, sector_bonus)
    
    # 国产替代加分
    if any(k in s['sector'] for k in ['半导体', '芯片', '刻蚀', 'CIS']):
        score += 15
    
    return max(0, min(100, score))

# ============================================================
# 9维度筛选
# ============================================================

def pick_for_profile(s_list, risk, horizon):
    """根据风险偏好和时间周期筛选TOP3"""
    scored = []
    for s in s_list:
        v = score_valuation(s)
        g = score_growth(s)
        t = score_technical(s)
        q = score_quality(s)
        p = score_policy(s)
        
        s['score_v'] = v
        s['score_g'] = g
        s['score_t'] = t
        s['score_q'] = q
        s['score_p'] = p
        
        # 根据风险和时间加权
        if risk == '激进':
            # 激进：高成长+高弹性+政策
            if horizon == '短期':
                w = {'g': 0.30, 't': 0.30, 'p': 0.25, 'v': 0.05, 'q': 0.10}
            elif horizon == '中期':
                w = {'g': 0.30, 'p': 0.30, 't': 0.15, 'v': 0.10, 'q': 0.15}
            else:  # 长期
                w = {'g': 0.25, 'p': 0.30, 'q': 0.25, 'v': 0.10, 't': 0.10}
        elif risk == '稳健':
            # 稳健：平衡成长和价值
            if horizon == '短期':
                w = {'v': 0.25, 't': 0.25, 'q': 0.20, 'g': 0.15, 'p': 0.15}
            elif horizon == '中期':
                w = {'g': 0.25, 'q': 0.25, 'v': 0.20, 'p': 0.15, 't': 0.15}
            else:  # 长期
                w = {'q': 0.30, 'g': 0.25, 'v': 0.20, 'p': 0.15, 't': 0.10}
        else:  # 保守
            # 保守：低估值+高质量+高分红
            if horizon == '短期':
                w = {'v': 0.35, 'q': 0.30, 't': 0.15, 'g': 0.05, 'p': 0.15}
            elif horizon == '中期':
                w = {'v': 0.30, 'q': 0.30, 'g': 0.15, 'p': 0.10, 't': 0.15}
            else:  # 长期
                w = {'q': 0.30, 'v': 0.30, 'g': 0.10, 'p': 0.15, 't': 0.15}
        
        total = (v * w['v'] + g * w['g'] + t * w['t'] + q * w['q'] + p * w['p'])
        s['total_score'] = round(total, 1)
        scored.append(s)
    
    scored.sort(key=lambda x: x['total_score'], reverse=True)
    return scored[:3]

# ============================================================
# 输出
# ============================================================

print("=" * 80)
print("  全市场9维度深度筛选结果")
print("  37只候选 × 5维评分 × 9种组合")
print("  2026-03-27")
print("=" * 80)

configs = [
    ('激进', '短期'), ('稳健', '短期'), ('保守', '短期'),
    ('激进', '中期'), ('稳健', '中期'), ('保守', '中期'),
    ('激进', '长期'), ('稳健', '长期'), ('保守', '长期'),
]

horizon_desc = {
    '短期': '1-3个月，追求快速反弹',
    '中期': '3-6个月，等待催化剂兑现',
    '长期': '6-12个月，行业爆发+业绩释放',
}

risk_desc = {
    '激进': '高风险高收益，追求弹性最大化',
    '稳健': '平衡风险收益，攻守兼备',
    '保守': '低风险，追求确定性+股息',
}

for idx, (risk, horizon) in enumerate(configs):
    picks = pick_for_profile(stocks, risk, horizon)
    
    print(f"\n{'='*80}")
    print(f"  {risk} × {horizon}")
    print(f"  {risk_desc[risk]}")
    print(f"  {horizon_desc[horizon]}")
    print(f"{'='*80}")
    
    for rank, s in enumerate(picks, 1):
        stop = round(s['price'] * 0.92, 2)
        if horizon == '短期':
            target = round(s['price'] * 1.15, 2)
        elif horizon == '中期':
            target = round(s['price'] * 1.30, 2)
        else:
            target = round(s['price'] * 1.50, 2)
        
        upside = round((target - s['price']) / s['price'] * 100, 1)
        downside = -8.0
        risk_reward = round(abs(upside / downside), 1)
        
        print(f"\n  【第{rank}名】{s['code']} {s['name']}")
        print(f"    赛道: {s['sector']}")
        print(f"    现价: {s['price']:.2f}元")
        print(f"    PE: {s['pe']} | PB: {s['pb']} | ROE: {s['roe']}% | 股息: {s['div']}%")
        print(f"    营收增速: {s['rev_g']}% | 净利增速: {s['net_g']}%")
        print(f"    3月跌幅: {s['drop_3m']}% | 6月跌幅: {s['drop_6m']}% | RSI: {s['rsi']}")
        print(f"    护城河: {s['barrier']} | 政策支持: {s['policy']}")
        print(f"    目标价: {target:.2f}元 (+{upside}%)")
        print(f"    止损价: {stop:.2f}元 ({downside}%)")
        print(f"    盈亏比: 1:{risk_reward}")
        print(f"    综合评分: {s['total_score']}")
        print(f"      估值:{s['score_v']} 成长:{s['score_g']} 技术:{s['score_t']} 质量:{s['score_q']} 政策:{s['score_p']}")

# ============================================================
# 汇总表
# ============================================================
print(f"\n\n{'='*80}")
print(f"  汇总：9维度推荐一览")
print(f"{'='*80}")

print(f"\n  {'维度':<16} {'第1名':<18} {'第2名':<18} {'第3名':<18}")
print(f"  {'-'*72}")

for risk, horizon in configs:
    picks = pick_for_profile(stocks, risk, horizon)
    row = f"{risk}{horizon}        "
    names = [f"{p['code']} {p['name']}" for p in picks]
    print(f"  {row:<16} {names[0]:<18} {names[1]:<18} {names[2]:<18}")

print(f"\n{'='*80}")
print(f"  分析完成")
print(f"{'='*80}")
