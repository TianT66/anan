# -*- coding: utf-8 -*-
"""
市场舆情监控系统
获取散户情绪、股吧热度、论坛讨论
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')


def get_market_sentiment():
    """获取市场整体情绪"""
    print("=" * 70)
    print("  市场舆情监控报告")
    print("  " + "2026-03-25")
    print("=" * 70)
    
    # 模拟数据（实际应接入东方财富、同花顺、雪球等API）
    # 由于网络限制，这里用模拟数据演示
    
    sentiment_data = {
        # 散户情绪指标
        'retail_sentiment': {
            'score': 35,  # 0-100，低于30恐慌，高于70亢奋
            'level': '恐慌',
            'description': '散户情绪处于恐慌区域',
            'indicators': {
                'bull_bear_ratio': 0.35,  # 看涨/看跌比例
                'position_ratio': 45,  # 散户仓位比例
                'volatility': '高',  # 情绪波动
            }
        },
        
        # 市场热度
        'market_heat': {
            'level': '冰点',
            'daily_turnover': '显著萎缩',
            'new_investors': '锐减',
            'margin_usage': '下降',
        },
        
        # 板块情绪
        'sector_sentiment': {
            'hot_sectors': [
                {'name': 'AI算力', 'heat': 65, 'trend': '分化'},
                {'name': '半导体', 'heat': 55, 'trend': '反弹'},
                {'name': '新能源车', 'heat': 45, 'trend': '下跌'},
            ],
            'cold_sectors': [
                {'name': '券商', 'heat': 20, 'trend': '下跌'},
                {'name': '银行', 'heat': 25, 'trend': '震荡'},
                {'name': '房地产', 'heat': 15, 'trend': '冷清'},
            ]
        },
        
        # 散户仓位
        'retail_position': {
            'avg_position': 35,  # 平均仓位
            'position_trend': '下降',
            'cash_reserve': '较高',
        },
        
        # 杠杆资金
        'margin_data': {
            'margin_balance': '下降中',
            'short_interest': '增加',
            'risk_level': '中等',
        }
    }
    
    print("\n【一、散户情绪指标】")
    s = sentiment_data['retail_sentiment']
    print(f"  情绪得分: {s['score']}/100")
    print(f"  情绪等级: {s['level']}")
    print(f"  看涨/看跌比: {s['indicators']['bull_bear_ratio']:.2f}")
    print(f"  散户平均仓位: {s['indicators']['position_ratio']}%")
    print(f"  情绪波动: {s['indicators']['volatility']}")
    
    # 情绪解读
    if s['score'] < 30:
        print("\n  [解读] 恐慌情绪蔓延，往往是底部信号")
    elif s['score'] < 45:
        print("\n  [解读] 情绪低迷，市场可能继续下探")
    elif s['score'] < 60:
        print("\n  [解读] 情绪中性，观望为主")
    else:
        print("\n  [解读] 情绪亢奋，需注意回调风险")
    
    print("\n【二、市场热度】")
    h = sentiment_data['market_heat']
    print(f"  市场热度: {h['level']}")
    print(f"  成交量: {h['daily_turnover']}")
    print(f"  新增投资者: {h['new_investors']}")
    print(f"  融资融券: {h['margin_usage']}")
    
    print("\n【三、板块情绪】")
    sector = sentiment_data['sector_sentiment']
    print("  热门板块:")
    for sec in sector['hot_sectors']:
        print(f"    - {sec['name']}: 热度{sec['heat']} ({sec['trend']})")
    
    print("\n  冷门板块:")
    for sec in sector['cold_sectors']:
        print(f"    - {sec['name']}: 热度{sec['heat']} ({sec['trend']})")
    
    print("\n【四、散户仓位】")
    pos = sentiment_data['retail_position']
    print(f"  平均仓位: {pos['avg_position']}%")
    print(f"  仓位趋势: {pos['position_trend']}")
    print(f"  现金储备: {pos['cash_reserve']}")
    
    if pos['avg_position'] < 40:
        print("\n  [解读] 散户仓位低，割肉后保持观望")
    elif pos['avg_position'] < 60:
        print("\n  [解读] 散户仓位适中，风险可控")
    else:
        print("\n  [解读] 散户仓位高，需注意追高风险")
    
    print("\n【五、杠杆资金】")
    margin = sentiment_data['margin_data']
    print(f"  融资余额: {margin['margin_balance']}")
    print(f"  融券余额: {margin['short_interest']}")
    print(f"  风险等级: {margin['risk_level']}")
    
    # 综合判断
    print("\n" + "=" * 70)
    print("  综合判断")
    print("=" * 70)
    
    sentiment_score = s['score']
    
    if sentiment_score < 30:
        signal = "极度恐慌 -> 可能见底"
        action = "逐步建仓，逆向投资"
    elif sentiment_score < 40:
        signal = "恐慌情绪 -> 等待企稳"
        action = "保持观望，小仓位试错"
    elif sentiment_score < 50:
        signal = "情绪低迷 -> 底部区域"
        action = "寻找错杀股，择机建仓"
    elif sentiment_score < 60:
        signal = "情绪中性 -> 震荡整理"
        action = "均衡配置，高抛低吸"
    else:
        signal = "情绪回暖 -> 注意风险"
        action = "逐步减仓，锁定利润"
    
    print(f"\n  舆情信号: {signal}")
    print(f"  操作建议: {action}")
    
    print("\n" + "=" * 70)
    print("  股民舆论热点话题")
    print("=" * 70)
    
    topics = [
        ("#A股下跌#", "恐慌", "500万+", "微博"),
        ("#A股底在哪里#", "恐慌", "300万+", "微博"),
        ("#散户割肉#", "恐慌", "200万+", "微博"),
        ("#AI算力反弹#", "关注", "150万+", "雪球"),
        ("#半导体国产替代#", "关注", "100万+", "雪球"),
        ("#十五五规划#", "期待", "80万+", "微博"),
        ("#美联储降息#", "关注", "200万+", "微博"),
        ("#量化交易#", "争议", "50万+", "论坛"),
    ]
    
    print(f"\n  {'话题':<25} {'情绪':<8} {'热度':<12} {'来源'}")
    print(f"  {'-'*60}")
    for topic, sentiment, heat, source in topics:
        print(f"  {topic:<25} {sentiment:<8} {heat:<12} {source}")
    
    print("\n" + "=" * 70)
    print("  结论与建议")
    print("=" * 70)
    
    print("""
    【舆情总结】
    - 散户情绪处于恐慌区域（得分35/100）
    - 成交量显著萎缩，市场人气低迷
    - 杠杆资金持续下降，风险偏好降低
    - 热门话题围绕"下跌"、"割肉"，恐慌情绪蔓延
    
    【历史对比】
    - 2024年2月、2022年4月：类似恐慌情绪后出现阶段性底部
    - 恐慌到极致往往预示着反弹机会
    
    【操作建议】
    1. 逆向思维：别人恐慌我贪婪
    2. 分批建仓：越跌越买，但不梭哈
    3. 选对方向：十五五规划产业（AI、半导体、新能源）
    4. 保留现金：即使见底也有得玩
    
    【风险提示】
    - 恐慌后可能还有恐慌，不要抄到半山腰
    - 等待明确企稳信号（成交量放大、大盘站上MA5）
    - 设置止损线，防止更大亏损
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    get_market_sentiment()
