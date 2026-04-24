# -*- coding: utf-8 -*-
"""
运行进化引擎分析历史数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 导入引擎
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')
from evolution_engine import EvolutionEngine

# 初始化引擎
engine = EvolutionEngine(r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading\evolution_data')

# 更新统计数据
closed_trades = [t for t in engine.trades if "close_price" in t]
for trade in closed_trades:
    engine._update_stats(trade)

# 打印报告
engine.print_report()

# 分析模式
print("\n" + "="*50)
print("🔍 模式分析")
print("="*50)
engine.analyze_patterns()

# 优化参数
print("\n" + "="*50)
print("🔧 参数优化")
print("="*50)
engine.optimize_params()
