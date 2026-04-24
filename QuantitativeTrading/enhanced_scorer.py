# -*- coding: utf-8 -*-
"""
P1改进：主力资金因子 + 大盘择时增强
增加主力资金追踪和更精准的择时系统
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')


class FundFlowAnalyzer:
    """主力资金分析"""
    
    def __init__(self):
        self.weight = 0.15  # 资金流向因子权重
    
    def analyze(self, code):
        """
        分析单只股票的主力资金流向
        
        Returns:
            dict: {
                'main_inflow': 主净流入金额,
                'main_inflow_ratio': 主净流入/流通市值,
                'direction': 'inflow'/'outflow'/'neutral',
                'score': -20到+20分,
                'signals': ['信号1', '信号2']
            }
        """
        # 模拟数据（实际应接入AKShare/东方财富）
        import random
        import pandas as pd
        
        # 随机生成模拟数据
        net_inflow = random.uniform(-5000, 5000) * 10000  # -5000万到+5000万
        turnover = random.uniform(1, 10)  # 换手率1-10%
        
        score = 0
        signals = []
        
        # 主力资金判断
        if net_inflow > 30000000:  # 3000万以上
            score += 20
            signals.append('主力大幅净流入')
            direction = 'inflow'
        elif net_inflow > 10000000:
            score += 10
            signals.append('主力净流入')
            direction = 'inflow'
        elif net_inflow > 0:
            score += 5
            signals.append('主力小幅净流入')
            direction = 'inflow'
        elif net_inflow > -10000000:
            score -= 5
            signals.append('主力小幅净流出')
            direction = 'outflow'
        elif net_inflow > -30000000:
            score -= 10
            signals.append('主力净流出')
            direction = 'outflow'
        else:
            score -= 20
            signals.append('主力大幅净流出')
            direction = 'outflow'
        
        # 换手率判断
        if turnover > 15:
            score -= 5
            signals.append('换手率过高，谨慎')
        elif turnover > 8:
            pass  # 正常
        elif turnover < 2:
            score += 5
            signals.append('换手率低，惜售')
        
        return {
            'code': code,
            'net_inflow': net_inflow,
            'turnover': turnover,
            'direction': direction,
            'score': max(-20, min(20, score)),
            'signals': signals,
            'weight': self.weight
        }
    
    def get_sector_flow(self):
        """获取板块资金流向"""
        # 模拟板块资金流向
        sectors = [
            {'name': 'AI算力', 'flow': '流入', 'strength': '强'},
            {'name': '半导体', 'flow': '流入', 'strength': '中'},
            {'name': '新能源', 'flow': '流出', 'strength': '强'},
            {'name': '医药', 'flow': '流入', 'strength': '弱'},
            {'name': '银行', 'flow': '流出', 'strength': '中'},
        ]
        return sectors


class EnhancedMarketTiming:
    """增强版大盘择时"""
    
    def __init__(self):
        self.index_codes = {
            '沪深300': '000300',
            '上证指数': '000001',
            '创业板指': '399006',
            '科创50': '000688'
        }
    
    def get_market_status(self):
        """
        获取多指数综合判断
        
        Returns:
            dict: {
                'status': 'BULL'/'BEAR'/'OSCILLATION',
                'confidence': 0.0-1.0,
                'indices': {...},
                'position': 0.0-1.0,
                'signals': [...]
            }
        """
        # 模拟多指数分析
        indices = {
            '沪深300': {
                'close': 3800,
                'ma20': 3850,
                'ma60': 3920,
                'macd': -25,
                'rsi': 35,
                'trend': '下跌'
            },
            '上证指数': {
                'close': 3400,
                'ma20': 3420,
                'ma60': 3480,
                'macd': -15,
                'rsi': 38,
                'trend': '震荡'
            },
            '创业板指': {
                'close': 1750,
                'ma20': 1800,
                'ma60': 1900,
                'macd': -30,
                'rsi': 30,
                'trend': '下跌'
            },
            '科创50': {
                'close': 850,
                'ma20': 880,
                'ma60': 920,
                'macd': -20,
                'rsi': 32,
                'trend': '下跌'
            }
        }
        
        # 综合评分
        bull_count = 0
        bear_count = 0
        total_score = 0
        
        for name, data in indices.items():
            score = 0
            
            # MA判断
            if data['close'] > data['ma20']:
                score += 2
            else:
                score -= 2
            
            if data['close'] > data['ma60']:
                score += 1
            else:
                score -= 1
            
            # MACD判断
            if data['macd'] > 0:
                score += 2
            elif data['macd'] > -10:
                score += 0
            else:
                score -= 2
            
            # RSI判断
            if data['rsi'] < 30:
                score += 1  # 超卖可能是机会
            elif data['rsi'] > 70:
                score -= 1  # 超买注意风险
            
            total_score += score
            
            if score >= 2:
                bull_count += 1
            elif score <= -2:
                bear_count += 1
        
        avg_score = total_score / len(indices)
        
        # 判断市场状态
        if avg_score >= 2 and bull_count >= 3:
            status = 'BULL'
            position = 0.80
            confidence = 0.8
        elif avg_score <= -2 and bear_count >= 3:
            status = 'BEAR'
            position = 0.30
            confidence = 0.8
        elif avg_score >= 1:
            status = 'OSCILLATION_UP'
            position = 0.60
            confidence = 0.5
        elif avg_score <= -1:
            status = 'OSCILLATION_DOWN'
            position = 0.40
            confidence = 0.5
        else:
            status = 'OSCILLATION'
            position = 0.50
            confidence = 0.4
        
        # 生成信号
        signals = []
        
        # 创业板/科创板先行指标
        if indices['创业板指']['rsi'] < 25:
            signals.append('创业板RSI超卖，可能先行反弹')
        
        if indices['科创50']['close'] < indices['科创50']['ma60'] * 0.9:
            signals.append('科创板大幅下跌，恐慌情绪严重')
        
        # 背离判断
        if indices['沪深300']['close'] < indices['沪深300']['ma20'] and indices['沪深300']['rsi'] < 35:
            signals.append('沪深300 RSI底背离，关注反弹')
        
        return {
            'status': status,
            'confidence': confidence,
            'indices': indices,
            'position': position,
            'avg_score': avg_score,
            'bull_count': bull_count,
            'bear_count': bear_count,
            'signals': signals
        }


class SentimentEnhancer:
    """舆情增强模块"""
    
    def __init__(self):
        self.keywords_positive = [
            '利好', '突破', '创新高', '订单', '业绩增长', 
            '获批', '合作', '回购', '增持', '产能释放'
        ]
        self.keywords_negative = [
            '利空', '减持', '亏损', '诉讼', '监管',
            '问询', '减持', '业绩下滑', '预警', '造假'
        ]
    
    def analyze_news(self, news_list):
        """分析新闻情绪"""
        if not news_list:
            return {'score': 0, 'sentiment': 'neutral', 'signals': []}
        
        score = 0
        signals = []
        
        for news in news_list:
            news_lower = news.lower()
            for kw in self.keywords_positive:
                if kw in news_lower:
                    score += 5
                    signals.append(f'正面: {news[:30]}...')
            for kw in self.keywords_negative:
                if kw in news_lower:
                    score -= 5
                    signals.append(f'负面: {news[:30]}...')
        
        # 归一化到 -10 到 +10
        score = max(-10, min(10, score))
        
        sentiment = 'positive' if score > 3 else 'negative' if score < -3 else 'neutral'
        
        return {
            'score': score,
            'sentiment': sentiment,
            'signals': signals[:5],
            'news_count': len(news_list)
        }


class EnhancedScorer:
    """增强版评分系统"""
    
    def __init__(self):
        self.fund_flow = FundFlowAnalyzer()
        self.market_timing = EnhancedMarketTiming()
        self.sentiment = SentimentEnhancer()
        
        # 新的权重配置
        self.weights = {
            'technical': 0.25,      # 技术面
            'fund_flow': 0.15,       # 主力资金（新增）
            'sentiment': 0.10,       # 舆情（调整）
            'fundamental': 0.20,    # 基本面
            'market_timing': 0.20,   # 大盘择时（新增）
            'policy': 0.10,         # 政策（新增）
        }
    
    def score_stock(self, code, fundamentals, news_list=None):
        """
        综合评分
        
        Returns:
            dict: {
                'total_score': 0-100,
                'component_scores': {...},
                'signals': [...],
                'recommendation': 'BUY'/'SELL'/'HOLD'
            }
        """
        scores = {}
        signals = []
        
        # 1. 技术面得分（简化的技术分析）
        # 实际应该计算真实的技术指标
        technical_score = 50 + (hash(code) % 40 - 20)  # 模拟
        scores['technical'] = technical_score
        if technical_score > 60:
            signals.append('技术面企稳')
        elif technical_score < 40:
            signals.append('技术面弱势')
        
        # 2. 主力资金得分
        fund_data = self.fund_flow.analyze(code)
        fund_score = 50 + fund_data['score']
        scores['fund_flow'] = fund_score
        signals.extend(fund_data['signals'][:2])
        
        # 3. 舆情得分
        sentiment_data = self.sentiment.analyze_news(news_list or [])
        sentiment_score = 50 + sentiment_data['score'] * 5
        scores['sentiment'] = sentiment_score
        signals.extend(sentiment_data['signals'][:2])
        
        # 4. 基本面得分
        pe = fundamentals.get('pe', 15)
        roe = fundamentals.get('roe', 10)
        
        fundamental_score = 50
        
        # PE评分
        if pe < 10:
            fundamental_score += 15
        elif pe < 20:
            fundamental_score += 10
        elif pe < 30:
            fundamental_score += 5
        elif pe > 50:
            fundamental_score -= 10
        
        # ROE评分
        if roe > 20:
            fundamental_score += 15
        elif roe > 15:
            fundamental_score += 10
        elif roe > 10:
            fundamental_score += 5
        elif roe < 5:
            fundamental_score -= 10
        
        scores['fundamental'] = fundamental_score
        
        # 5. 大盘择时调整
        market = self.market_timing.get_market_status()
        market_score = 50 + (market['position'] - 0.5) * 40
        scores['market_timing'] = market_score
        signals.extend(market['signals'][:2])
        
        # 6. 政策因子（简化）
        # 十五五规划受益行业加分
        policy_score = 50
        industry = fundamentals.get('industry', '')
        if any(x in industry for x in ['AI', '人工智能', '半导体', '新能源', '医药']):
            policy_score += 15
            signals.append('十五五规划受益行业')
        
        scores['policy'] = policy_score
        
        # 计算总分
        total = sum(scores[k] * self.weights[k] for k in self.weights)
        
        # 生成建议
        if total >= 70:
            recommendation = 'STRONG_BUY'
        elif total >= 60:
            recommendation = 'BUY'
        elif total >= 45:
            recommendation = 'HOLD'
        elif total >= 35:
            recommendation = 'SELL'
        else:
            recommendation = 'STRONG_SELL'
        
        return {
            'total_score': round(total, 1),
            'component_scores': {k: round(v, 1) for k, v in scores.items()},
            'weights': self.weights,
            'signals': signals[:8],
            'recommendation': recommendation,
            'market_status': market['status'],
            'position_suggestion': market['position']
        }


def test_enhanced_system():
    """测试增强系统"""
    print("=" * 70)
    print("  增强版量化系统 v5.1 测试")
    print("  P1改进: 主力资金 + 大盘择时")
    print("=" * 70)
    
    # 测试大盘择时
    print("\n【多指数择时分析】")
    timing = EnhancedMarketTiming()
    market = timing.get_market_status()
    
    status_map = {
        'BULL': '牛市',
        'BEAR': '熊市',
        'OSCILLATION': '震荡',
        'OSCILLATION_UP': '震荡偏多',
        'OSCILLATION_DOWN': '震荡偏空'
    }
    
    print(f"  市场状态: {status_map.get(market['status'], market['status'])}")
    print(f"  置信度: {market['confidence']*100:.0f}%")
    print(f"  建议仓位: {market['position']*100:.0f}%")
    
    print(f"\n  各指数状态:")
    for name, data in market['indices'].items():
        trend = data['trend']
        rsi = data['rsi']
        print(f"    {name}: {trend}, RSI={rsi}")
    
    if market['signals']:
        print(f"\n  信号:")
        for s in market['signals']:
            print(f"    - {s}")
    
    # 测试个股评分
    print("\n【个股综合评分测试】")
    scorer = EnhancedScorer()
    
    test_stocks = [
        {'code': '601899', 'name': '紫金矿业', 'pe': 18, 'roe': 22, 'industry': '有色金属'},
        {'code': '300750', 'name': '宁德时代', 'pe': 30, 'roe': 20, 'industry': '新能源'},
        {'code': '600519', 'name': '贵州茅台', 'pe': 28, 'roe': 32, 'industry': '白酒'},
    ]
    
    for stock in test_stocks:
        result = scorer.score_stock(stock['code'], stock)
        
        print(f"\n  {stock['name']}({stock['code']}):")
        print(f"    综合得分: {result['total_score']}/100")
        print(f"    建议: {result['recommendation']}")
        print(f"    大盘环境: {result['market_status']}")
        
        print(f"    因子得分:")
        for factor, score in result['component_scores'].items():
            weight = result['weights'][factor]
            print(f"      {factor}: {score} (权重{weight*100:.0f}%)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_enhanced_system()
