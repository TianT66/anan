# -*- coding: utf-8 -*-
"""
多因子综合策略模块
"""
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class MultiFactorStrategy:
    """多因子综合策略"""
    
    def __init__(self):
        """初始化策略"""
        pass
    
    def analyze(self, stock_code, data_fetcher):
        """
        执行完整的股票分析
        
        Args:
            stock_code: 股票代码
            data_fetcher: 数据采集器
            
        Returns:
            dict: 包含评分结果和信号结果
        """
        try:
            logger.info(f"开始分析股票: {stock_code}")
            
            # 1. 获取数据
            df = data_fetcher.get_stock_daily(stock_code)
            fund_flow = data_fetcher.get_fund_flow(stock_code)
            news_df = data_fetcher.get_stock_news(stock_code)
            financial_data = data_fetcher.get_financial_data(stock_code)
            
            # 2. 技术面分析
            from factors.technical import TechnicalAnalyzer
            tech_analyzer = TechnicalAnalyzer(df)
            tech_result = tech_analyzer.analyze()
            
            # 3. 情绪面分析
            from factors.sentiment import SentimentAnalyzer
            sent_analyzer = SentimentAnalyzer(fund_flow, news_df)
            sent_result = sent_analyzer.analyze()
            
            # 4. 基本面分析
            from factors.fundamental import FundamentalAnalyzer
            fund_analyzer = FundamentalAnalyzer(financial_data)
            fund_result = fund_analyzer.analyze()
            
            # 5. 多因子评分
            from engine.scorer import MultiFactorScorer
            scorer = MultiFactorScorer()
            scoring_result = scorer.score(tech_result, sent_result, fund_result)
            
            # 6. 生成信号
            from engine.signal import SignalGenerator
            signal_generator = SignalGenerator()
            signal_result = signal_generator.generate(scoring_result)
            
            # 7. 生成报告
            from report.reporter import ReportGenerator
            report_gen = ReportGenerator()
            report = report_gen.generate(stock_code, scoring_result, signal_result)
            
            result = {
                'stock_code': stock_code,
                'scoring_result': scoring_result,
                'signal_result': signal_result,
                'report': report,
            }
            
            logger.info(f"股票 {stock_code} 分析完成，综合得分: {scoring_result.get('composite_score')}")
            
            return result
            
        except Exception as e:
            logger.error(f"股票 {stock_code} 分析出错: {e}")
            return {
                'stock_code': stock_code,
                'error': str(e),
                'scoring_result': {'composite_score': 50},
                'signal_result': {'signal_name': '持有观望', 'confidence': '低'},
                'report': f"分析出错: {e}",
            }
    
    def batch_analyze(self, stock_codes, data_fetcher):
        """
        批量分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            data_fetcher: 数据采集器
            
        Returns:
            list: 分析结果列表，按综合得分排序
        """
        results = []
        
        for code in stock_codes:
            result = self.analyze(code, data_fetcher)
            results.append(result)
        
        # 按得分排序
        results.sort(key=lambda x: x['scoring_result'].get('composite_score', 0), reverse=True)
        
        return results


# 测试
if __name__ == "__main__":
    from data.data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    strategy = MultiFactorStrategy()
    
    result = strategy.analyze("000528", fetcher)
    
    print(f"\n股票: {result['stock_code']}")
    print(f"综合得分: {result['scoring_result']['composite_score']}")
    print(f"信号: {result['signal_result']['signal_name']}")
    print("\n" + result['report'])
