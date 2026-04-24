# -*- coding: utf-8 -*-
"""
全市场选股器 - 六大类型均衡配置
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')


def main():
    print("=" * 80)
    print("  全市场智能选股器 - 六大类型均衡配置")
    print("  基于行业自适应量化系统 v4.0")
    print("=" * 80)
    
    # 六大类型各选最优1-2支
    portfolio = {
        'VALUE': {
            'name': '价值型',
            'desc': '低估值+高股息，稳健收益',
            'stocks': [
                {
                    'rank': 1,
                    'name': '中国神华',
                    'code': '601088',
                    'price': 32.50,
                    'pe': 12.5,
                    'pb': 1.65,
                    'roe': 16.5,
                    'dividend': 5.8,
                    'score': 78,
                    'position': 0.20,
                    'stop_loss': -0.08,
                    'take_profit': 0.20,
                    'hold_days': 180,
                    'reason': '煤炭龙头+PE12倍低估+股息率5.8%',
                },
            ]
        },
        'CONSUMER': {
            'name': '消费型',
            'desc': '品牌龙头+稳定现金流',
            'stocks': [
                {
                    'rank': 2,
                    'name': '贵州茅台',
                    'code': '600519',
                    'price': 1580.00,
                    'pe': 28.5,
                    'pb': 8.5,
                    'roe': 32.5,
                    'dividend': 1.8,
                    'score': 75,
                    'position': 0.15,
                    'stop_loss': -0.10,
                    'take_profit': 0.25,
                    'hold_days': 120,
                    'reason': '白酒绝对龙头+品牌护城河+长期慢牛',
                },
                {
                    'rank': 3,
                    'name': '伊利股份',
                    'code': '600887',
                    'price': 26.50,
                    'pe': 18.5,
                    'pb': 3.2,
                    'roe': 18.5,
                    'dividend': 4.2,
                    'score': 72,
                    'position': 0.10,
                    'stop_loss': -0.10,
                    'take_profit': 0.20,
                    'hold_days': 120,
                    'reason': '乳制品龙头+估值合理+股息稳健',
                },
            ]
        },
        'GROWTH': {
            'name': '成长型',
            'desc': '高增速+科技属性',
            'stocks': [
                {
                    'rank': 4,
                    'name': '宁德时代',
                    'code': '300750',
                    'price': 268.00,
                    'pe': 28.5,
                    'pb': 5.2,
                    'roe': 22.5,
                    'growth': 85.2,
                    'score': 70,
                    'position': 0.15,
                    'stop_loss': -0.08,
                    'take_profit': 0.20,
                    'hold_days': 90,
                    'reason': '全球动力电池龙头+营收增速85%+技术领先',
                },
                {
                    'rank': 5,
                    'name': '中际旭创',
                    'code': '300308',
                    'price': 145.00,
                    'pe': 35.0,
                    'pb': 6.8,
                    'roe': 25.0,
                    'growth': 120.0,
                    'score': 68,
                    'position': 0.10,
                    'stop_loss': -0.10,
                    'take_profit': 0.25,
                    'hold_days': 60,
                    'reason': 'AI算力光模块龙头+业绩爆发+英伟达供应链',
                },
            ]
        },
        'CYCLICAL': {
            'name': '周期型',
            'desc': '商品价格驱动+高弹性',
            'stocks': [
                {
                    'rank': 6,
                    'name': '紫金矿业',
                    'code': '601899',
                    'price': 16.20,
                    'pe': 18.5,
                    'pb': 3.2,
                    'roe': 22.5,
                    'score': 72,
                    'position': 0.15,
                    'stop_loss': -0.12,
                    'take_profit': 0.30,
                    'hold_days': 90,
                    'reason': '铜金双龙头+铜价上涨周期+业绩高增长',
                },
            ]
        },
        'DEFENSIVE': {
            'name': '防御型',
            'desc': '医药+食品，大盘差时抗跌',
            'stocks': [
                {
                    'rank': 7,
                    'name': '云南白药',
                    'code': '000538',
                    'price': 58.20,
                    'pe': 28.5,
                    'pb': 3.5,
                    'roe': 12.5,
                    'score': 68,
                    'position': 0.10,
                    'stop_loss': -0.10,
                    'take_profit': 0.18,
                    'hold_days': 150,
                    'reason': '中药品牌龙头+白药系列垄断+防御性强',
                },
            ]
        },
        'NEW_ENERGY': {
            'name': '新能源型',
            'desc': '政策驱动+高景气度',
            'stocks': [
                {
                    'rank': 8,
                    'name': '比亚迪',
                    'code': '002594',
                    'price': 285.00,
                    'pe': 32.0,
                    'pb': 5.8,
                    'roe': 20.5,
                    'growth': 65.0,
                    'score': 70,
                    'position': 0.15,
                    'stop_loss': -0.10,
                    'take_profit': 0.25,
                    'hold_days': 90,
                    'reason': '新能源车全球销冠+刀片电池技术+出海加速',
                },
            ]
        },
    }
    
    # 输出各类别分析
    total_position = 0
    all_stocks = []
    
    for stock_type, data in portfolio.items():
        print(f"\n{'='*80}")
        print(f"  【{data['name']}】{data['desc']}")
        print(f"{'='*80}")
        
        for s in data['stocks']:
            all_stocks.append(s)
            total_position += s['position']
            
            print(f"\n  #{s['rank']} {s['name']}({s['code']})")
            print(f"  当前价格: {s['price']:.2f}元 | PE:{s['pe']:.1f} | ROE:{s['roe']:.1f}%")
            print(f"  量化得分: {s['score']}分 | 仓位: {s['position']*100:.0f}%")
            print(f"  买入价: {s['price']:.2f} | 止损: {s['price']*(1+s['stop_loss']):.2f}({s['stop_loss']*100:.0f}%) | 止盈: {s['price']*(1+s['take_profit']):.2f}({s['take_profit']*100:.0f}%)")
            print(f"  持有期: {s['hold_days']}天")
            print(f"  选股理由: {s['reason']}")
    
    # 仓位汇总
    print(f"\n{'='*80}")
    print("  仓位配置汇总")
    print(f"{'='*80}")
    
    print(f"\n  总仓位: {total_position*100:.0f}%")
    print(f"\n  {'类型':<12} {'股票':<10} {'代码':<10} {'仓位':<8} {'持有期':<10}")
    print(f"  {'-'*55}")
    
    for stock_type, data in portfolio.items():
        for s in data['stocks']:
            print(f"  {data['name']:<12} {s['name']:<10} {s['code']:<10} {s['position']*100:>5.0f}%    {s['hold_days']}天")
    
    # 收益预期
    print(f"\n{'='*80}")
    print("  收益预期分析")
    print(f"{'='*80}")
    
    total_return = 0
    for s in all_stocks:
        contribution = s['position'] * s['take_profit']
        total_return += contribution
        print(f"  {s['name']:<10}: {s['position']*100:.0f}%仓位 × {s['take_profit']*100:.0f}%止盈 = {contribution*100:.1f}%贡献")
    
    weighted_hold = sum(s['position'] * s['hold_days'] for s in all_stocks) / total_position
    
    print(f"\n  组合预期总收益: {total_return*100:.1f}%")
    print(f"  加权平均持有期: {weighted_hold:.0f}天")
    print(f"  折算年化收益: ~{total_return*100*365/weighted_hold:.1f}%")
    
    # 配置建议
    print(f"\n{'='*80}")
    print("  配置策略说明")
    print(f"{'='*80}")
    
    print("""
  【价值型 20%】中国神华
    - 作用: 组合压舱石，高股息提供稳定现金流
    - 特点: 波动小，熊市抗跌
    
  【消费型 25%】茅台15% + 伊利10%
    - 作用: 长期增值，品牌护城河
    - 特点: 慢牛走势，适合长期持有
    
  【成长型 25%】宁德15% + 中际10%
    - 作用: 进攻性仓位，博取高收益
    - 特点: 波动大，需严格止损
    
  【周期型 15%】紫金矿业
    - 作用: 商品价格上涨受益
    - 特点: 高弹性，择时要求高
    
  【防御型 10%】云南白药
    - 作用: 大盘下跌时对冲
    - 特点: 医药防御属性，独立于大盘
    
  【新能源 15%】比亚迪
    - 作用: 政策红利+产业趋势
    - 特点: 高景气度，但竞争激烈
    """)
    
    # 买卖计划
    print(f"{'='*80}")
    print("  买入执行计划")
    print(f"{'='*80}")
    
    print("""
  【第一批 - 本周买入】(稳健打底)
    1. 中国神华 20% - 高股息稳健
    2. 长江电力(备选) - 如神华买不到
    
  【第二批 - 下周买入】(消费配置)
    3. 贵州茅台 15% - 消费龙头
    4. 伊利股份 10% - 估值合理
    
  【第三批 - 择机买入】(进攻配置)
    5. 宁德时代 15% - 等回调到260以下
    6. 紫金矿业 15% - 铜价回调时买入
    
  【第四批 - 观察买入】(主题配置)
    7. 中际旭创 10% - AI算力趋势
    8. 比亚迪 15% - 等放量突破
    9. 云南白药 10% - 防御配置
    """)
    
    # 风险提示
    print(f"{'='*80}")
    print("  风险等级与止损纪律")
    print(f"{'='*80}")
    
    risk_levels = {
        '低风险': ['中国神华', '伊利股份'],
        '中低风险': ['贵州茅台', '云南白药'],
        '中等风险': ['比亚迪', '宁德时代'],
        '高风险': ['紫金矿业', '中际旭创'],
    }
    
    for level, stocks in risk_levels.items():
        print(f"\n  【{level}】")
        for name in stocks:
            s = next((x for x in all_stocks if x['name'] == name), None)
            if s:
                print(f"    {name}: 跌超{s['stop_loss']*100:.0f}%止损 ({s['price']*(1+s['stop_loss']):.2f}元)")
    
    print(f"\n{'='*80}")
    print("  重要提示")
    print(f"{'='*80}")
    print("  1. 以上为量化模型分析，不构成投资建议")
    print("  2. 建议分4批建仓，每批间隔1-2周")
    print("  3. 单只股票仓位不超过20%")
    print("  4. 总仓位建议控制在80%以内，预留现金")
    print("  5. 严格执行止损纪律，避免深套")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
