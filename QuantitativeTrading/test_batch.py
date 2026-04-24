# -*- coding: utf-8 -*-
"""
测试脚本 - 批量扫描测试
"""
import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except:
    pass

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def main():
    """主函数"""
    # 测试批量扫描
    stock_codes = ["000528", "600036", "000001", "600519", "300750"]
    
    print("\n" + "=" * 50)
    print("  批量扫描测试")
    print("=" * 50)
    
    from data.data_fetcher import DataFetcher
    from strategies.multi_factor import MultiFactorStrategy
    
    fetcher = DataFetcher()
    strategy = MultiFactorStrategy()
    
    results = strategy.batch_analyze(stock_codes, fetcher)
    
    # 打印结果
    print("\n" + "=" * 60)
    print("       批量扫描结果 (按综合得分降序)")
    print("=" * 60)
    print(f"{'排名':<4} {'股票代码':<10} {'综合得分':<10} {'投资建议':<12} {'置信度':<8}")
    print("-" * 60)
    
    for i, result in enumerate(results, 1):
        code = result['stock_code']
        score = result['scoring_result']['composite_score']
        signal = result['signal_result']['signal_name']
        confidence = result['signal_result']['confidence']
        
        print(f"{i:<4} {code:<10} {score:<10.1f} {signal:<12} {confidence:<8}")
    
    print("=" * 60)
    
    if results:
        best = results[0]
        print(f"\n[*] 最佳推荐: {best['stock_code']} (得分: {best['scoring_result']['composite_score']:.1f})")
        print(f"    建议: {best['signal_result']['signal_name']}")


if __name__ == "__main__":
    main()
