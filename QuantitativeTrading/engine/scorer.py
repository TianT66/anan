# -*- coding: utf-8 -*-
"""
综合评分引擎 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime


class ComprehensiveScorer:
    """综合评分器"""
    
    def __init__(self):
        # 评分权重配置
        self.weights = {
            'fund_flow': 0.20,      # 资金动向
            'pattern': 0.15,         # K线形态
            'volume_price': 0.15,   # 量价配合
            'momentum': 0.15,        # 短线动能
            'ma_system': 0.15,      # 均线系统
            'macd': 0.10,           # MACD
            'kdj': 0.05,            # KDJ
            'rsi': 0.05,            # RSI
        }
        
    def score(self, df, stock_code=None, market_data=None):
        """
        计算综合评分
        :param df: 包含所有指标的DataFrame
        :param stock_code: 股票代码
        :param market_data: 市场情绪数据
        :return: 综合评分结果
        """
        if len(df) < 20:
            return self._empty_result("数据不足")
        
        # 导入各因子评分器
        from factors.technical import TechnicalIndicators
        from factors.pattern import PatternRecognition
        from factors.sentiment import SentimentFactors
        from factors.limits import LimitUpDownAnalyzer
        
        # 各因子评分
        tech = TechnicalIndicators()
        df = tech.calculate_all(df)
        
        # 1. 资金动向评分
        fund_flow_score = self._score_fund_flow(df)
        
        # 2. K线形态评分
        pattern_rec = PatternRecognition()
        pattern_score = pattern_rec.score_patterns(df)
        
        # 3. 量价配合评分
        vol_price_score = tech.score_volume_price(df)
        
        # 4. 短线动能评分
        momentum_score = tech.score_momentum(df)
        
        # 5. 均线系统评分
        ma_score = tech.score_ma_system(df)
        
        # 6. MACD评分
        macd_score = tech.score_macd(df)
        
        # 7. KDJ评分
        kdj_score = tech.score_kdj(df)
        
        # 8. RSI评分
        rsi_score = tech.score_rsi(df)
        
        # 涨跌停评分（A股特有）
        limit_analyzer = LimitUpDownAnalyzer()
        limit_score = limit_analyzer.score_limits(df)
        
        # 情绪因子评分
        sentiment_analyzer = SentimentFactors()
        sentiment_score = sentiment_analyzer.analyze_sentiment(df, stock_code, market_data)
        
        # 计算加权总分
        raw_score = (
            fund_flow_score['score'] * self.weights['fund_flow'] +
            pattern_score['score'] * self.weights['pattern'] +
            vol_price_score['score'] * self.weights['volume_price'] +
            momentum_score['score'] * self.weights['momentum'] +
            ma_score['score'] * self.weights['ma_system'] +
            macd_score['score'] * self.weights['macd'] +
            kdj_score['score'] * self.weights['kdj'] +
            rsi_score['score'] * self.weights['rsi'] +
            limit_score['score'] * 0.0 +  # 涨停作为独立加成
            sentiment_score['score'] * 0.0  # 情绪作为独立加成
        )
        
        # 涨停加分
        raw_score += limit_score['score']
        
        # 情绪加分
        raw_score += sentiment_score['score']
        
        # 归一化到0-100
        final_score = self._normalize_score(raw_score)
        
        # 收集所有细节
        all_details = []
        for detail_list in [fund_flow_score['details'], pattern_score['details'],
                          vol_price_score['details'], momentum_score['details'],
                          ma_score['details'], macd_score['score']['details'] if isinstance(macd_score['score'], dict) else macd_score['details'],
                          kdj_score['details'], rsi_score['details'],
                          limit_score['details'], sentiment_score['details']]:
            if isinstance(detail_list, list):
                all_details.extend(detail_list)
        
        # 获取最新指标值
        latest_values = tech.get_latest_values(df)
        
        return {
            'total_score': final_score,
            'raw_score': raw_score,
            'fund_flow': fund_flow_score,
            'pattern': pattern_score,
            'volume_price': vol_price_score,
            'momentum': momentum_score,
            'ma_system': ma_score,
            'macd': macd_score,
            'kdj': kdj_score,
            'rsi': rsi_score,
            'limit': limit_score,
            'sentiment': sentiment_score,
            'details': all_details,
            'indicators': latest_values,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _score_fund_flow(self, df):
        """资金动向评分"""
        score = 0
        details = []
        
        if len(df) < 10:
            return {'score': 0, 'details': ['数据不足']}
        
        # 5日主力净流入占比（模拟）
        # 实际应使用akshare的资金流数据
        try:
            vol_ma5 = df['volume'].rolling(5).mean()
            vol_ma10 = df['volume'].rolling(10).mean()
            
            # 量能趋势
            vol_ratio_5d = df['volume'].iloc[-5:].mean() / df['volume'].iloc[-10:-5].mean()
            
            # 5日趋势上升：+15分
            if vol_ratio_5d > 1.03:
                score += 15
                details.append(f"5日量能持续放大(+{(vol_ratio_5d-1)*100:.1f}%) [+15]")
            
            # 超大单迹象（放量且涨幅大）
            vol_ratio = df['vol_ratio'].iloc[-1] if 'vol_ratio' in df.columns else 1
            pct_change = df['pct_change'].iloc[-1]
            
            if vol_ratio > 1.5 and pct_change > 2:
                score += 10
                details.append("超大单净流入迹象 [+10]")
                
        except Exception:
            pass
        
        # 10日趋势上升：+15分
        try:
            vol_10_trend = (df['volume'].iloc[-10:].mean() - df['volume'].iloc[-20:-10].mean()) / \
                           df['volume'].iloc[-20:-10].mean()
            if vol_10_trend > 0.05:
                score += 15
                details.append(f"10日量能趋势上升(+{vol_10_trend*100:.1f}%) [+15]")
        except Exception:
            pass
        
        return {'score': score, 'details': details}
    
    def _normalize_score(self, raw_score):
        """
        将原始分数归一化到0-100范围
        """
        # 根据各因子满分的理论最大值（约100-150分）进行归一化
        # 这里用简单映射
        if raw_score < 0:
            return max(0, 50 + raw_score)  # 允许少量负分，但最低不低于50
        
        # 将分数映射到0-100
        # 假设正常范围在-20到+80之间
        normalized = 50 + raw_score
        return max(0, min(100, normalized))
    
    def get_position_recommendation(self, total_score):
        """
        根据评分获取仓位建议
        """
        if total_score > 75:
            return {
                'position': 0.40,
                'action': '重仓买入',
                'level': 'heavy'
            }
        elif total_score >= 65:
            return {
                'position': 0.25,
                'action': '标准买入',
                'level': 'standard'
            }
        elif total_score >= 55:
            return {
                'position': 0.15,
                'action': '轻仓试探',
                'level': 'light'
            }
        elif total_score >= 45:
            return {
                'position': 0.00,
                'action': '持有不动',
                'level': 'hold'
            }
        else:
            return {
                'position': 0.00,
                'action': '清仓观望',
                'level': 'clear'
            }
    
    def _empty_result(self, reason):
        """返回空结果"""
        return {
            'total_score': 50,
            'raw_score': 0,
            'reason': reason,
            'details': [],
            'indicators': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_report(self, score_result, stock_code, stock_name=None):
        """生成评分报告"""
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"  A股短线量化评分报告 v3.0")
        report_lines.append(f"  股票代码: {stock_code}")
        if stock_name:
            report_lines.append(f"  股票名称: {stock_name}")
        report_lines.append(f"  评分时间: {score_result.get('timestamp', 'N/A')}")
        report_lines.append("=" * 60)
        
        report_lines.append("")
        report_lines.append(f"【综合评分】 {score_result['total_score']:.1f} / 100")
        
        # 仓位建议
        position = self.get_position_recommendation(score_result['total_score'])
        report_lines.append(f"【仓位建议】 {position['action']} ({position['position']*100:.0f}%)")
        
        report_lines.append("")
        report_lines.append("【分项评分】")
        
        # 各因子评分
        factor_names = {
            'fund_flow': '资金动向',
            'pattern': 'K线形态',
            'volume_price': '量价配合',
            'momentum': '短线动能',
            'ma_system': '均线系统',
            'macd': 'MACD',
            'kdj': 'KDJ',
            'rsi': 'RSI',
            'limit': '涨跌停',
            'sentiment': '情绪周期'
        }
        
        for key, name in factor_names.items():
            if key in score_result:
                factor = score_result[key]
                score = factor.get('score', 0) if isinstance(factor, dict) else factor
                details = factor.get('details', []) if isinstance(factor, dict) else []
                report_lines.append(f"  {name}: {score:+.0f}分")
                for detail in details[:3]:  # 最多显示3个细节
                    report_lines.append(f"    - {detail}")
        
        report_lines.append("")
        report_lines.append("【关键指标】")
        
        indicators = score_result.get('indicators', {})
        if indicators:
            report_lines.append(f"  收盘价: {indicators.get('close', 0):.2f}")
            report_lines.append(f"  MA5: {indicators.get('ma5', 0):.2f}")
            report_lines.append(f"  MA10: {indicators.get('ma10', 0):.2f}")
            report_lines.append(f"  MACD: {indicators.get('macd', 0):.3f}")
            report_lines.append(f"  KDJ(K/D/J): {indicators.get('kdj_k', 0):.1f}/{indicators.get('kdj_d', 0):.1f}/{indicators.get('kdj_j', 0):.1f}")
            report_lines.append(f"  RSI(6): {indicators.get('rsi_6', 0):.1f}")
            report_lines.append(f"  量比: {indicators.get('vol_ratio', 0):.2f}")
            report_lines.append(f"  3日涨幅: {indicators.get('pct_3d', 0):.2f}%")
            report_lines.append(f"  5日涨幅: {indicators.get('pct_5d', 0):.2f}%")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


# 全局实例
scorer = ComprehensiveScorer()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    
    df = fetcher.get_daily_data('000528', '20240101', '20241231')
    
    cs = ComprehensiveScorer()
    result = cs.score(df, '000528', {'yzt_ratio': 0.02})
    
    print(f"[OK] Total Score: {result['total_score']:.1f}")
    print(f"[OK] Position: {cs.get_position_recommendation(result['total_score'])}")
    print("")
    print(cs.generate_report(result, '000528', '柳工'))
