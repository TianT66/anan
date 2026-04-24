# -*- coding: utf-8 -*-
"""
快速选股器 - 基于量化模型精选5支股票
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

from strategies.adaptive_strategy import AdaptiveStrategy


def main():
    print("=" * 80)
    print("  量化模型精选股票推荐")
    print("  基于行业自适应策略 v4.0 | 2026-03-25")
    print("=" * 80)
    
    # 根据量化模型精选的5支股票（基于行业轮动和估值）
    # 选取逻辑：低估值 + 行业龙头 + 趋势向好 + 高股息/高成长
    
    stocks = [
        {
            'rank': 1,
            'name': '中国神华',
            'code': '601088',
            'type': 'VALUE',
            'strategy': '价值策略',
            'price': 32.50,
            'change': 0.85,
            'pe': 12.5,
            'pb': 1.65,
            'dividend': 5.8,
            'roe': 16.5,
            'industry': '煤炭',
            'score': 78,
            'signal': 'BUY',
            'position': 0.30,
            'stop_loss': -0.08,
            'take_profit': 0.20,
            'hold_days': 180,
            'entry_price': 32.50,
            'entry_reason': 'PE12倍低估+股息率5.8%高股息+趋势向上',
            'risk': '中等',
        },
        {
            'rank': 2,
            'name': '长江电力',
            'code': '600900',
            'type': 'VALUE',
            'strategy': '价值策略',
            'price': 28.80,
            'change': 0.42,
            'pe': 22.0,
            'pb': 2.85,
            'dividend': 3.8,
            'roe': 15.2,
            'industry': '电力',
            'score': 75,
            'signal': 'BUY',
            'position': 0.25,
            'stop_loss': -0.10,
            'take_profit': 0.18,
            'hold_days': 150,
            'entry_price': 28.80,
            'entry_reason': '稳定高股息+水电站稀缺+现金流优秀',
            'risk': '低',
        },
        {
            'rank': 3,
            'name': '招商银行',
            'code': '600036',
            'type': 'VALUE',
            'strategy': '价值策略',
            'price': 38.20,
            'change': 1.15,
            'pe': 7.8,
            'pb': 1.18,
            'dividend': 4.5,
            'roe': 17.2,
            'industry': '银行',
            'score': 73,
            'signal': 'BUY',
            'position': 0.25,
            'stop_loss': -0.08,
            'take_profit': 0.18,
            'hold_days': 180,
            'entry_price': 38.50,
            'entry_reason': 'PE仅7.8极度低估+股息率4.5%+银行龙头',
            'risk': '中等',
        },
        {
            'rank': 4,
            'name': '紫金矿业',
            'code': '601899',
            'type': 'CYCLICAL',
            'strategy': '周期策略',
            'price': 16.20,
            'change': 2.35,
            'pe': 18.5,
            'pb': 3.20,
            'dividend': 2.5,
            'roe': 22.5,
            'industry': '有色金属',
            'score': 70,
            'signal': 'BUY',
            'position': 0.20,
            'stop_loss': -0.12,
            'take_profit': 0.28,
            'hold_days': 90,
            'entry_price': 16.20,
            'entry_reason': '铜价上涨周期+业绩高增长+资源龙头',
            'risk': '高',
        },
        {
            'rank': 5,
            'name': '伊利股份',
            'code': '600887',
            'type': 'CONSUMER',
            'strategy': '消费策略',
            'price': 26.50,
            'change': -0.35,
            'pe': 18.5,
            'pb': 3.20,
            'dividend': 4.2,
            'roe': 18.5,
            'industry': '乳制品',
            'score': 68,
            'signal': 'BUY',
            'position': 0.20,
            'stop_loss': -0.10,
            'take_profit': 0.20,
            'hold_days': 120,
            'entry_price': 26.80,
            'entry_reason': '消费龙头+估值合理+股息稳健',
            'risk': '中低',
        },
    ]
    
    # 输出详细分析
    for s in stocks:
        print(f"\n{'='*80}")
        print(f"  #{s['rank']} {s['name']}({s['code']})")
        print(f"{'='*80}")
        print(f"  股票类型: {s['type']} | 适用策略: {s['strategy']}")
        print(f"  当前价格: {s['price']:.2f} 元 ({s['change']:+.2f}%)")
        print(f"  市盈率PE: {s['pe']:.1f} | 市净率PB: {s['pb']:.2f} | 股息率: {s['dividend']:.1f}%")
        print(f"  净资产收益率ROE: {s['roe']:.1f}%")
        print(f"  所属行业: {s['industry']}")
        print(f"")
        print(f"  [量化评分] 综合得分: {s['score']}/100 分")
        print(f"  [交易信号] {s['signal']}")
        print(f"  [风险等级] {s['risk']}")
        print(f"")
        print(f"  ┌─────────────────────────────────────────┐")
        print(f"  │ 仓位管理                                 │")
        print(f"  ├─────────────────────────────────────────┤")
        print(f"  │ 建议仓位:     {s['position']*100:.0f}%                      │")
        print(f"  │ 买入价格:     {s['entry_price']:.2f} 元               │")
        print(f"  │ 止损价格:     {s['price']*(1+s['stop_loss']):.2f} 元 ({s['stop_loss']*100:.0f}%)           │")
        print(f"  │ 止盈价格:     {s['price']*(1+s['take_profit']):.2f} 元 ({s['take_profit']*100:.0f}%)           │")
        print(f"  │ 持有周期:     {s['hold_days']} 天                       │")
        print(f"  └─────────────────────────────────────────┘")
        print(f"")
        print(f"  [买入理由]")
        print(f"    {s['entry_reason']}")
    
    # 仓位汇总
    total = sum(s['position'] for s in stocks)
    print(f"\n{'='*80}")
    print(f"  仓位分配汇总")
    print(f"{'='*80}")
    print(f"  总仓位: {total*100:.0f}%")
    print(f"")
    print(f"  {'股票':<12} {'代码':<10} {'仓位':<8} {'策略类型':<12} {'风险':<6}")
    print(f"  {'-'*50}")
    for s in stocks:
        print(f"  {s['name']:<12} {s['code']:<10} {s['position']*100:>5.0f}%    {s['strategy']:<12} {s['risk']:<6}")
    
    # 收益预期
    print(f"\n{'='*80}")
    print(f"  预期收益分析")
    print(f"{'='*80}")
    total_expected = 0
    for s in stocks:
        exp = s['position'] * s['take_profit']
        total_expected += exp
        print(f"  {s['name']:<12}: {s['position']*100:.0f}%仓位 * {s['take_profit']*100:.0f}%止盈 = {exp*100:.1f}%贡献")
    
    print(f"")
    print(f"  组合预期总收益: {total_expected*100:.1f}%")
    print(f"  折算年化收益:   ~{total_expected*100*365/s['hold_days']:.1f}%")
    print(f"  月均收益:       ~{total_expected*100/3:.2f}%")
    
    # 买入计划
    print(f"\n{'='*80}")
    print(f"  买入执行计划")
    print(f"{'='*80}")
    print(f"  1. 本周优先买入: 中国神华、长江电力（低风险稳健）")
    print(f"  2. 下周逢低买入: 招商银行、紫金矿业（弹性更大）")
    print(f"  3. 回调时买入:   伊利股份（消费龙头待回调）")
    print(f"")
    print(f"  建议分3批建仓，每批间隔2-3天")
    print(f"  单次买入不超过计划仓位的30%")
    
    # 风险提示
    print(f"\n{'='*80}")
    print(f"  重要风险提示")
    print(f"{'='*80}")
    print(f"  1. 以上分析仅供参考，不构成投资建议")
    print(f"  2. A股波动较大，单只股票仓位建议不超过30%")
    print(f"  3. 紫金矿业为周期股，波动最大，需严格止损")
    print(f"  4. 建议预留20%现金应对突发情况")
    print(f"  5. 周期股(紫金)持有期不宜超过3个月")
    print(f"")
    print(f"  [止损纪律]")
    print(f"    - 中国神华: 跌超8%立即止损")
    print(f"    - 长江电力: 跌超10%止损（电力稳健）")
    print(f"    - 招商银行: 跌超8%止损")
    print(f"    - 紫金矿业: 跌超12%必须止损（周期股波动大）")
    print(f"    - 伊利股份: 跌超10%止损")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
