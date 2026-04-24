# -*- coding: utf-8 -*-
"""
行业自适应策略测试 - v4.0
验证不同类型股票使用对应策略的效果
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

import time
from classifier.stock_classifier import StockClassifier
from strategies.adaptive_strategy import AdaptiveStrategy
from strategies.value_strategy import ValueStrategy
from strategies.cycle_strategy import CycleStrategy
from strategies.short_term import ShortTermStrategy
from strategies.defensive_strategy import DefensiveStrategy


# 测试股票池（每种类型2-3只）
TEST_STOCKS = {
    'VALUE': [
        {'code': '601318', 'name': '中国平安', 'pe': 8.5, 'pb': 1.2, 'roe': 12.5, 'dividend': 5.2, 'industry': '保险'},
        {'code': '600036', 'name': '招商银行', 'pe': 7.2, 'pb': 1.1, 'roe': 16.8, 'dividend': 4.8, 'industry': '银行'},
        {'code': '600028', 'name': '中国石化', 'pe': 9.1, 'pb': 0.8, 'roe': 8.5, 'dividend': 6.5, 'industry': '石油'},
    ],
    'CONSUMER': [
        {'code': '600519', 'name': '贵州茅台', 'pe': 32.5, 'pb': 12.5, 'roe': 32.5, 'dividend': 1.8, 'industry': '白酒'},
        {'code': '000858', 'name': '五粮液', 'pe': 22.5, 'pb': 5.8, 'roe': 25.8, 'dividend': 2.5, 'industry': '白酒'},
        {'code': '000333', 'name': '美的集团', 'pe': 15.2, 'pb': 3.2, 'roe': 24.5, 'dividend': 3.5, 'industry': '家电'},
    ],
    'GROWTH': [
        {'code': '300750', 'name': '宁德时代', 'pe': 28.5, 'pb': 5.2, 'roe': 22.5, 'revenue_growth': 85.2, 'industry': '新能源'},
        {'code': '002475', 'name': '立讯精密', 'pe': 25.2, 'pb': 4.8, 'roe': 22.5, 'revenue_growth': 45.2, 'industry': '电子'},
        {'code': '300059', 'name': '东方财富', 'pe': 35.2, 'pb': 5.8, 'roe': 18.5, 'revenue_growth': 35.2, 'industry': '券商'},
    ],
    'CYCLICAL': [
        {'code': '000528', 'name': '柳工', 'pe': 15.5, 'pb': 0.95, 'roe': 8.5, 'industry': '工程机械'},
        {'code': '601899', 'name': '紫金矿业', 'pe': 18.5, 'pb': 2.8, 'roe': 22.5, 'industry': '有色金属'},
        {'code': '600019', 'name': '宝钢股份', 'pe': 12.5, 'pb': 0.75, 'roe': 9.5, 'industry': '钢铁'},
    ],
    'DEFENSIVE': [
        {'code': '000538', 'name': '云南白药', 'pe': 28.5, 'pb': 3.5, 'roe': 12.5, 'revenue_growth': 8.5, 'industry': '中药'},
        {'code': '600276', 'name': '恒瑞医药', 'pe': 65.5, 'pb': 8.5, 'roe': 15.2, 'revenue_growth': 12.5, 'industry': '医药'},
    ],
    'NEW_ENERGY': [
        {'code': '002594', 'name': '比亚迪', 'pe': 35.5, 'pb': 6.5, 'roe': 18.5, 'revenue_growth': 65.2, 'industry': '新能源车'},
        {'code': '601012', 'name': '隆基绿能', 'pe': 22.5, 'pb': 3.5, 'roe': 25.5, 'revenue_growth': 55.2, 'industry': '光伏'},
    ],
}

# 模拟股票数据
def get_mock_stock_data(close_price=10):
    return {
        'close': close_price,
        'ma5': close_price * 0.98,
        'ma20': close_price * 1.02,
        'ma60': close_price * 1.05,
        'rsi6': 45,
        'rsi14': 52,
        'macd': 0.05,
        'volume_ratio': 1.2,
        'price_3d_change': 3.5,
        'price_5d_change': 5.2,
        'price_20d_change': 8.5,
        'is_limit_up': False,
        'limit_count': 0,
    }


def main():
    print("=" * 70)
    print("  行业自适应量化策略系统 v4.0")
    print("=" * 70)
    
    # 1. 测试股票分类
    print("\n" + "-" * 70)
    print("  第一部分：股票分类测试")
    print("-" * 70)
    
    classifier = StockClassifier()
    
    # 分类结果汇总
    classifications = {}
    
    for stock_type, stocks in TEST_STOCKS.items():
        print(f"\n[{stock_type}类型]")
        for stock in stocks:
            fundamentals = {
                'pe': stock.get('pe', 15),
                'pb': stock.get('pb', 1.5),
                'roe': stock.get('roe', 10),
                'dividend_yield': stock.get('dividend', 2),
                'revenue_growth': stock.get('revenue_growth', 10),
                'profit_growth': stock.get('revenue_growth', 10) * 0.8,
                'rd_ratio': stock.get('rd_ratio', 3),
                'industry': stock.get('industry', '未知'),
            }
            
            result = classifier.classify_stock(stock['code'], fundamentals)
            
            match = "OK" if result['type'] == stock_type else "MISMATCH"
            print(f"  {stock['code']} {stock['name']:<10} -> {result['type']:<10} [{match}] 置信度:{result['confidence']:.0%}")
            print(f"    原因: {', '.join(result['reasons'][:3])}")
            
            classifications[stock['code']] = result['type']
    
    # 2. 测试各策略信号
    print("\n" + "-" * 70)
    print("  第二部分：策略信号测试")
    print("-" * 70)
    
    # 测试单只股票详细分析
    test_stock = TEST_STOCKS['CYCLICAL'][0]  # 柳工
    print(f"\n[{test_stock['code']} {test_stock['name']} 详细分析]")
    print(f"  基本面: PE={test_stock['pe']}, PB={test_stock['pb']}, ROE={test_stock['roe']}%")
    
    fundamentals = {
        'pe': test_stock['pe'],
        'pb': test_stock['pb'],
        'roe': test_stock['roe'],
        'dividend_yield': test_stock.get('dividend', 2),
        'revenue_growth': test_stock.get('revenue_growth', 10),
        'profit_growth': test_stock.get('revenue_growth', 10) * 0.8,
        'industry': test_stock['industry'],
    }
    
    stock_data = get_mock_stock_data(10)
    
    # 自适应策略
    adaptive = AdaptiveStrategy()
    result = adaptive.analyze(stock_data, fundamentals)
    
    print(f"\n  分类结果: {result['stock_type']} (置信度: {result['type_confidence']:.0%})")
    print(f"  适用策略: {result['strategy']}")
    print(f"  综合得分: {result['score']} 分")
    print(f"  交易信号: {result['signal']}")
    print(f"  建议仓位: {result['position']*100:.0f}%")
    print(f"  止损位: {result['stop_loss']*100:.0f}%")
    print(f"  止盈位: {result['take_profit']*100:.0f}%")
    print(f"  主要理由:")
    for reason in result['reasons'][:5]:
        print(f"    - {reason}")
    
    # 3. 各类型股票策略对比
    print("\n" + "-" * 70)
    print("  第三部分：各类型股票策略对比")
    print("-" * 70)
    
    print(f"\n{'代码':<8} {'名称':<10} {'类型':<12} {'策略':<15} {'得分':<6} {'信号':<12} {'仓位':<6}")
    print("-" * 75)
    
    for stock_type, stocks in TEST_STOCKS.items():
        for stock in stocks:
            fundamentals = {
                'pe': stock.get('pe', 15),
                'pb': stock.get('pb', 1.5),
                'roe': stock.get('roe', 10),
                'dividend_yield': stock.get('dividend', 2),
                'revenue_growth': stock.get('revenue_growth', 10),
                'profit_growth': stock.get('revenue_growth', 10) * 0.8,
                'rd_ratio': stock.get('rd_ratio', 3),
                'industry': stock.get('industry', '未知'),
            }
            
            result = adaptive.analyze(get_mock_stock_data(10), fundamentals)
            
            print(f"{stock['code']:<8} {stock['name']:<10} {result['stock_type']:<12} "
                  f"{result['strategy']:<15} {result['score']:<6} {result['signal']:<12} "
                  f"{result['position']*100:>5.0f}%")
    
    # 4. 策略建议总结
    print("\n" + "=" * 70)
    print("  第四部分：策略建议总结")
    print("=" * 70)
    
    print("""
    【价值蓝筹股】 - 招行/平安/石化
      最佳策略: 均值回归 + 高股息
      核心指标: PE分位、PB、股息率
      建议仓位: 30-40%
      持有周期: 6-12个月
      预期收益: 年化10-15%
    
    【消费龙头股】 - 茅台/五粮液/美的
      最佳策略: 趋势跟踪 + 回调买入
      核心指标: MA20/60、RSI、品牌力
      建议仓位: 25-35%
      持有周期: 3-6个月
      预期收益: 年化15-25%（长持更优）
    
    【成长科技股】 - 宁德/立讯/东财
      最佳策略: 动量突破 + 板块联动
      核心指标: 营收增速、MACD、量比
      建议仓位: 20-30%
      持有周期: 1-3个月（短线为主）
      预期收益: 高弹性，注意止损
    
    【周期股】 - 柳工/宝钢/紫金
      最佳策略: PB择时 + 商品驱动
      核心指标: PB、PPI、螺纹钢指数
      建议仓位: 30-50%
      持有周期: 3-6个月
      预期收益: 高波动，注意择时
    
    【医药防御股】 - 白药/恒瑞
      最佳策略: 政策底买入 + 稳定持有
      核心指标: PE、研发管线、政策
      建议仓位: 25-35%
      持有周期: 3-6个月
      预期收益: 稳健，年化10-15%
    
    【新能源股】 - 比亚迪/隆基
      最佳策略: 政策催化 + 产能周期
      核心指标: 政策密集度、产能利用率
      建议仓位: 25-35%
      持有周期: 1-4个月
      预期收益: 高波动，紧跟政策
    """)
    
    print("=" * 70)
    print("  测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
