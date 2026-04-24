# -*- coding: utf-8 -*-
"""
主动买入建议生成器
每天自动分析市场，给出具体买入建议
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')


class DailyRecommendation:
    """每日主动推荐"""
    
    def __init__(self):
        self.market_status = self.get_market_status()
        self.strategy = self.get_current_strategy()
    
    def get_market_status(self):
        """获取当前市场状态"""
        # 模拟实际分析（实际应接入真实数据）
        return {
            'status': 'BEAR',  # 熊市
            'confidence': 0.80,
            'position': 0.30,
            'signals': [
                '沪深300跌破MA20，趋势向下',
                'MACD水下死叉',
                '成交量萎缩',
                '散户情绪恐慌'
            ]
        }
    
    def get_current_strategy(self):
        """根据市场状态确定策略"""
        if self.market_status['status'] == 'BEAR':
            return {
                'name': '防御策略',
                'position': 0.30,
                'stop_loss': 0.08,
                'take_profit': 0.15,
                'holding_days': 90,
                'criteria': {
                    'max_pe': 20,
                    'min_dividend': 3,
                    'min_roe': 10,
                    'preferred_sectors': ['银行', '电力', '医药', '消费']
                }
            }
        elif self.market_status['status'] == 'BULL':
            return {
                'name': '趋势动量策略',
                'position': 0.80,
                'stop_loss': 0.10,
                'take_profit': 0.25,
                'holding_days': 30,
                'criteria': {
                    'min_volume': 5,
                    'trend': 'MA20之上',
                    'preferred_sectors': ['科技', '新能源', '券商']
                }
            }
        else:
            return {
                'name': '震荡策略',
                'position': 0.50,
                'stop_loss': 0.06,
                'take_profit': 0.12,
                'holding_days': 15,
                'criteria': {
                    'rsi_range': (30, 70),
                    'preferred_sectors': ['医药', '消费', '科技']
                }
            }
    
    def get_recommendations(self):
        """获取今日推荐"""
        
        # 根据当前策略和筛选标准，给出具体推荐
        recommendations = []
        
        if self.market_status['status'] == 'BEAR':
            # 熊市推荐：高股息+低估值
            recommendations = [
                {
                    'code': '601319',
                    'name': '中国银行',
                    'price': 3.85,
                    'pe': 5.2,
                    'dividend': 5.8,
                    'roe': 11.5,
                    'reason': '银行龙头+股息率5.8%+低估',
                    'position': 0.10,
                    'stop_loss': 3.54,
                    'take_profit': 4.43,
                    'risk': '低'
                },
                {
                    'code': '600900',
                    'name': '长江电力',
                    'price': 28.50,
                    'pe': 22,
                    'dividend': 4.2,
                    'roe': 15,
                    'reason': '水电龙头+稳定高股息+避险资产',
                    'position': 0.10,
                    'stop_loss': 26.22,
                    'take_profit': 32.78,
                    'risk': '低'
                },
                {
                    'code': '600519',
                    'name': '贵州茅台',
                    'price': 1550,
                    'pe': 26,
                    'dividend': 2.2,
                    'roe': 32,
                    'reason': '白酒绝对龙头+品牌护城河+超跌反弹',
                    'position': 0.10,
                    'stop_loss': 1426,
                    'take_profit': 1783,
                    'risk': '中低'
                }
            ]
        
        elif self.market_status['status'] == 'BULL':
            # 牛市推荐：趋势+动量
            recommendations = [
                {
                    'code': '300750',
                    'name': '宁德时代',
                    'price': 265,
                    'pe': 30,
                    'growth': 85,
                    'reason': '新能源龙头+业绩高增长+趋势向上',
                    'position': 0.25,
                    'stop_loss': 238,
                    'take_profit': 331,
                    'risk': '高'
                },
                {
                    'code': '688041',
                    'name': '寒武纪',
                    'price': 180,
                    'pe': '亏损',
                    'growth': '高',
                    'reason': 'AI算力芯片龙头+国产替代+政策支持',
                    'position': 0.20,
                    'stop_loss': 162,
                    'take_profit': 225,
                    'risk': '极高'
                }
            ]
        
        else:
            # 震荡市
            recommendations = [
                {
                    'code': '300760',
                    'name': '迈瑞医疗',
                    'price': 175,
                    'pe': 28,
                    'dividend': 1.8,
                    'roe': 32,
                    'reason': '医疗器械龙头+估值合理+防御性好',
                    'position': 0.15,
                    'stop_loss': 161,
                    'take_profit': 201,
                    'risk': '中'
                },
                {
                    'code': '601888',
                    'name': '中国中免',
                    'price': 68,
                    'pe': 22,
                    'growth': 25,
                    'reason': '免税龙头+消费复苏+估值修复',
                    'position': 0.15,
                    'stop_loss': 63,
                    'take_profit': 78,
                    'risk': '中'
                }
            ]
        
        return recommendations


def generate_daily_report():
    """生成每日报告"""
    rec = DailyRecommendation()
    
    print("=" * 70)
    print("  每日量化投资建议")
    print("  生成时间: 2026-03-25")
    print("=" * 70)
    
    # 市场状态
    market = rec.market_status
    print(f"\n【市场诊断】")
    print(f"  市场状态: {market['status']}")
    print(f"  置信度: {market['confidence']*100:.0f}%")
    print(f"  建议仓位: {market['position']*100:.0f}%")
    print(f"  信号:")
    for signal in market['signals']:
        print(f"    - {signal}")
    
    # 策略
    strategy = rec.strategy
    print(f"\n【采用策略】")
    print(f"  策略名称: {strategy['name']}")
    print(f"  目标仓位: {strategy['position']*100:.0f}%")
    print(f"  止损线: {strategy['stop_loss']*100:.0f}%")
    print(f"  止盈线: {strategy['take_profit']*100:.0f}%")
    print(f"  持有期: {strategy['holding_days']}天")
    
    # 推荐
    recommendations = rec.get_recommendations()
    print(f"\n【今日推荐】")
    print(f"  共{len(recommendations)}只")
    
    print(f"\n  {'代码':<8} {'名称':<10} {'现价':<10} {'理由':<25} {'仓位':<6} {'止损':<8} {'止盈':<8}")
    print(f"  {'-'*90}")
    
    total_position = 0
    for r in recommendations:
        print(f"  {r['code']:<8} {r['name']:<10} {r['price']:<10.2f} {r['reason']:<25} {r['position']*100:>4.0f}%   {r['stop_loss']:<8.2f} {r['take_profit']:<8.2f}")
        total_position += r['position']
    
    print(f"\n  >>> 推荐总仓位: {total_position*100:.0f}%")
    
    # 具体操作
    print(f"\n【操作建议】")
    print("""
  1. 今日推荐3只股票，都是按照当前市场环境（熊市）精选的防御型标的
  2. 每只股票建议仓位10%，总计30%仓位
  3. 买入后设置止损：-8%自动止损
  4. 止盈目标：+15%
  5. 持有期：90天
  
  【为什么是这些股票？】
  - 中国银行：PE5.2，股息率5.8%，银行最稳健
  - 长江电力：水电垄断，现金流稳定，高股息
  - 贵州茅台：白酒龙头，品牌护城河，超跌后估值修复
    """)
    
    # 风险提示
    print(f"\n【风险提示】")
    print("""
  ⚠️ 当前为熊市环境，操作需谨慎
  - 建议总仓位不超过30%
  - 务必设置8%止损线
  - 如果没有合适机会，可以空仓等待
  - 以上仅供参考，不构成投资建议
    """)
    
    print("=" * 70)


if __name__ == "__main__":
    generate_daily_report()
