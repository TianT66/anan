# -*- coding: utf-8 -*-
"""
测试脚本 - 直接测试柳工(000528)
"""
import sys
import os

# 设置UTF-8输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except:
    pass

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    stock_code = "000528"
    
    print("\n" + "=" * 50)
    print(f"  测试股票: {stock_code} (柳工)")
    print("=" * 50)
    
    try:
        from data.data_fetcher import DataFetcher
        from strategies.multi_factor import MultiFactorStrategy
        
        print(f"\n[>>] 正在分析股票 {stock_code}...")
        
        # 获取数据
        fetcher = DataFetcher()
        
        # 执行分析
        strategy = MultiFactorStrategy()
        result = strategy.analyze(stock_code, fetcher)
        
        # 打印报告
        print("\n" + result['report'])
        
        # 打印最终结论
        print("\n" + "=" * 50)
        print("[分析结论]")
        print("=" * 50)
        print(f"股票代码: {stock_code}")
        print(f"综合得分: {result['scoring_result']['composite_score']:.1f} 分")
        print(f"投资建议: {result['signal_result']['signal_name']}")
        print(f"置信度: {result['signal_result']['confidence']}")
        
        if result['signal_result'].get('reasons'):
            print(f"主要理由: {', '.join(result['signal_result']['reasons'])}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"[!] 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
