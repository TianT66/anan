# -*- coding: utf-8 -*-
"""
基本面因子分析模块
分析PE、PB、ROE等财务指标
"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    """基本面分析器"""
    
    def __init__(self, financial_data=None):
        """
        初始化基本面分析器
        
        Args:
            financial_data: 财务数据dict
        """
        self.financial_data = financial_data or {}
        self.score = 50  # 基础分
        self.details = {}
        
    def analyze(self):
        """
        执行基本面分析
        
        Returns:
            dict: 基本面得分和细节
        """
        try:
            # 如果没有财务数据，返回默认50分
            if not self.financial_data:
                logger.warning("无财务数据，使用默认基本面得分50分")
                return {
                    'score': 50,
                    'details': {'note': '无财务数据，使用默认值'}
                }
            
            self.score = 50  # 重置为基础分50
            
            # 1. PE估值分析
            self._analyze_pe()
            
            # 2. PB估值分析
            self._analyze_pb()
            
            # 3. ROE分析
            self._analyze_roe()
            
            # 归一化到0-100
            self.score = max(0, min(100, self.score))
            
            result = {
                'score': self.score,
                'details': self.details
            }
            
            logger.info(f"基本面分析完成，得分: {self.score}")
            return result
            
        except Exception as e:
            logger.error(f"基本面分析出错: {e}")
            return {'score': 50, 'details': {'error': str(e)}}
    
    def _analyze_pe(self):
        """分析PE估值"""
        try:
            pe = self.financial_data.get('pe', 0)
            
            score = 0
            reasons = []
            
            # PE打分
            if pe <= 0 or pe is None:
                score = 0
                reasons.append("PE无效或亏损")
            elif pe < 15:
                score = 30
                reasons.append(f"PE低估(<15, +30): {pe:.1f}")
            elif pe < 30:
                score = 20
                reasons.append(f"PE合理(15-30, +20): {pe:.1f}")
            elif pe < 50:
                score = 10
                reasons.append(f"PE偏高(30-50, +10): {pe:.1f}")
            else:
                score = 0
                reasons.append(f"PE高估(>50, +0): {pe:.1f}")
            
            self.score += score
            
            self.details['pe'] = {
                'score': score,
                'reasons': reasons,
                'value': round(pe, 2) if pe and pe > 0 else None,
            }
            
        except Exception as e:
            logger.error(f"PE分析出错: {e}")
            self.details['pe'] = {'score': 0, 'reasons': [f'计算错误: {e}']}
    
    def _analyze_pb(self):
        """分析PB估值"""
        try:
            pb = self.financial_data.get('pb', 0)
            
            score = 0
            reasons = []
            
            # PB打分
            if pb <= 0 or pb is None:
                score = 0
                reasons.append("PB无效")
            elif pb < 1:
                score = 20
                reasons.append(f"PB极低(<1, +20): {pb:.2f}")
            elif pb < 3:
                score = 10
                reasons.append(f"PB合理(1-3, +10): {pb:.2f}")
            else:
                score = 0
                reasons.append(f"PB偏高(>3, +0): {pb:.2f}")
            
            self.score += score
            
            self.details['pb'] = {
                'score': score,
                'reasons': reasons,
                'value': round(pb, 2) if pb and pb > 0 else None,
            }
            
        except Exception as e:
            logger.error(f"PB分析出错: {e}")
            self.details['pb'] = {'score': 0, 'reasons': [f'计算错误: {e}']}
    
    def _analyze_roe(self):
        """分析ROE"""
        try:
            roe = self.financial_data.get('roe', 0)
            
            score = 0
            reasons = []
            
            # ROE打分
            if roe <= 0 or roe is None:
                score = 0
                reasons.append("ROE无效或亏损")
            elif roe > 20:
                score = 25
                reasons.append(f"ROE优秀(>20%, +25): {roe:.1f}%")
            elif roe > 10:
                score = 15
                reasons.append(f"ROE良好(10-20%, +15): {roe:.1f}%")
            elif roe > 5:
                score = 5
                reasons.append(f"ROE一般(5-10%, +5): {roe:.1f}%")
            else:
                score = 0
                reasons.append(f"ROE较低(<5%, +0): {roe:.1f}%")
            
            self.score += score
            
            self.details['roe'] = {
                'score': score,
                'reasons': reasons,
                'value': round(roe, 2) if roe and roe > 0 else None,
            }
            
        except Exception as e:
            logger.error(f"ROE分析出错: {e}")
            self.details['roe'] = {'score': 0, 'reasons': [f'计算错误: {e}']}


# 测试
if __name__ == "__main__":
    from data.data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    financial_data = fetcher.get_financial_data("000528")
    
    analyzer = FundamentalAnalyzer(financial_data)
    result = analyzer.analyze()
    
    print(f"\n基本面得分: {result['score']}")
    print(f"基本面详情: {result['details']}")
