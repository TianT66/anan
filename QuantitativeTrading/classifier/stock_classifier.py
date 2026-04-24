# -*- coding: utf-8 -*-
"""
股票分类器
根据基本面和行业特征将股票分为6大类型
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import sys
sys.path.insert(0, 'C:/Users/12408/.qclaw/workspace/QuantitativeTrading')
from config import settings
from data import data_fetcher


class StockClassifier:
    """A股股票分类器"""
    
    def __init__(self):
        self.config = settings.CLASSIFIER_CONFIG
    
    def classify_stock(self, code, fundamentals=None):
        """
        分类股票
        
        Args:
            code: 股票代码
            fundamentals: 基本面数据dict，如果为None则自动获取
            
        Returns:
            dict: {
                'type': 'VALUE'/'CONSUMER'/'GROWTH'/'CYCLICAL'/'DEFENSIVE'/'NEW_ENERGY',
                'confidence': 0.0-1.0,
                'reasons': ['原因1', '原因2', ...],
                'fundamentals': 基本面数据
            }
        """
        if fundamentals is None:
            fundamentals = data_fetcher.get_stock_fundamentals(code)
        
        industry = fundamentals.get('industry', '未知')
        pe = fundamentals.get('pe', 15)
        pb = fundamentals.get('pb', 1.5)
        roe = fundamentals.get('roe', 10)
        dividend_yield = fundamentals.get('dividend_yield', 0)
        revenue_growth = fundamentals.get('revenue_growth', 0)
        profit_growth = fundamentals.get('profit_growth', 0)
        rd_ratio = fundamentals.get('rd_ratio', 0)
        
        reasons = []
        scores = {}
        
        # ==========================================
        # 1. 首先判断是否为周期股 (CYCLICAL)
        # ==========================================
        cyclical_score = 0
        cyclical_reasons = []
        
        # 行业判断
        for ind in self.config['cyclical_industries']:
            if ind in industry:
                cyclical_score += 2
                cyclical_reasons.append(f'行业:{ind}(周期行业)')
                break
        
        # PB<1 且 ROE<10%
        if pb < self.config['cyclical_pb_threshold'] and roe < self.config['cyclical_roe_threshold']:
            cyclical_score += 2
            cyclical_reasons.append('PB<1且ROE<10%(周期特征)')
        
        scores['CYCLICAL'] = cyclical_score
        reasons.extend(cyclical_reasons)
        
        # ==========================================
        # 2. 判断是否为医药医疗 (DEFENSIVE)
        # ==========================================
        defensive_score = 0
        defensive_reasons = []
        
        for ind in self.config['defensive_industries']:
            if ind in industry:
                defensive_score += 3
                defensive_reasons.append(f'行业:{ind}(防御性行业)')
                break
        
        scores['DEFENSIVE'] = defensive_score
        reasons.extend(defensive_reasons)
        
        # ==========================================
        # 3. 判断是否为新能源/高端制造 (NEW_ENERGY)
        # ==========================================
        new_energy_score = 0
        new_energy_reasons = []
        
        for ind in self.config['new_energy_industries']:
            if ind in industry:
                new_energy_score += 3
                new_energy_reasons.append(f'行业:{ind}(新能源/高端制造)')
                break
        
        # 政策驱动特征：营收增速>30%
        if revenue_growth > 30:
            new_energy_score += 1
            new_energy_reasons.append(f'营收增速{round(revenue_growth*100)}%(高成长)')
        
        scores['NEW_ENERGY'] = new_energy_score
        reasons.extend(new_energy_reasons)
        
        # ==========================================
        # 4. 判断是否为科技成长 (GROWTH)
        # ==========================================
        growth_score = 0
        growth_reasons = []
        
        # 营收增速>20%
        if revenue_growth > self.config['growth_revenue_threshold'] * 100:
            growth_score += 2
            growth_reasons.append(f'营收增速{round(revenue_growth, 1)}%(高成长)')
        
        # 研发费用占比>5%
        if rd_ratio > self.config['growth_rd_ratio_threshold'] * 100:
            growth_score += 2
            growth_reasons.append(f'研发占比{round(rd_ratio, 1)}%(高研发)')
        
        # PE>30
        if pe > self.config['growth_pe_threshold']:
            growth_score += 1
            growth_reasons.append(f'PE={round(pe, 1)}(高估值成长)')
        
        scores['GROWTH'] = growth_score
        reasons.extend(growth_reasons)
        
        # ==========================================
        # 5. 判断是否为消费龙头 (CONSUMER)
        # ==========================================
        consumer_score = 0
        consumer_reasons = []
        
        # 行业判断
        for ind in self.config['consumer_industries']:
            if ind in industry:
                consumer_score += 2
                consumer_reasons.append(f'行业:{ind}(消费行业)')
                break
        
        # ROE>15%
        if roe > self.config['consumer_roe_threshold']:
            consumer_score += 2
            consumer_reasons.append(f'ROE={round(roe, 1)}%(高盈利能力)')
        
        # 净利润增速>营收增速（规模效应）
        if profit_growth > revenue_growth and profit_growth > 0:
            consumer_score += 1
            consumer_reasons.append('利润增速>营收增速(规模效应)')
        
        scores['CONSUMER'] = consumer_score
        reasons.extend(consumer_reasons)
        
        # ==========================================
        # 6. 判断是否为价值蓝筹 (VALUE)
        # ==========================================
        value_score = 0
        value_reasons = []
        
        # PE<20
        if pe < self.config['value_pe_threshold']:
            value_score += 2
            value_reasons.append(f'PE={round(pe, 1)}(低估值)')
        
        # 股息率>2%
        if dividend_yield > self.config['value_dividend_threshold'] * 100:
            value_score += 2
            value_reasons.append(f'股息率{round(dividend_yield, 1)}%(高股息)')
        
        # 行业判断
        for ind in self.config['value_industries']:
            if ind in industry:
                value_score += 2
                value_reasons.append(f'行业:{ind}(价值行业)')
                break
        
        scores['VALUE'] = value_score
        reasons.extend(value_reasons)
        
        # ==========================================
        # 选择最高分类
        # ==========================================
        if not scores or max(scores.values()) == 0:
            # 默认价值股
            stock_type = 'VALUE'
            confidence = 0.3
            if not reasons:
                reasons = ['PE<20(默认分类)']
        else:
            stock_type = max(scores, key=scores.get)
            score = scores[stock_type]
            
            # 置信度计算
            if score >= 6:
                confidence = 0.9
            elif score >= 4:
                confidence = 0.7
            elif score >= 2:
                confidence = 0.5
            else:
                confidence = 0.3
        
        return {
            'type': stock_type,
            'confidence': confidence,
            'reasons': reasons[:5],  # 最多5个原因
            'fundamentals': fundamentals,
            'scores': scores
        }
    
    def get_strategy_name(self, stock_type):
        """获取股票类型对应的策略名称"""
        strategy_map = {
            'VALUE': '均值回归策略',
            'CONSUMER': '趋势跟踪策略',
            'GROWTH': '动量突破策略',
            'CYCLICAL': '周期择时策略',
            'DEFENSIVE': '政策驱动策略',
            'NEW_ENERGY': '政策催化策略'
        }
        return strategy_map.get(stock_type, '未知策略')


# 单例
classifier = StockClassifier()


def classify_stock(code, fundamentals=None):
    return classifier.classify_stock(code, fundamentals)


def get_strategy_name(stock_type):
    return classifier.get_strategy_name(stock_type)


# 测试
if __name__ == '__main__':
    test_codes = ['000528', '600519', '300750', '601318', '600036', '002594']
    
    print("=" * 60)
    print("股票分类测试")
    print("=" * 60)
    
    for code in test_codes:
        result = classify_stock(code)
        print(f"\n代码: {code}")
        print(f"类型: {result['type']}")
        print(f"置信度: {result['confidence']}")
        print(f"原因: {result['reasons']}")
        print("-" * 40)