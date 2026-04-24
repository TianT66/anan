# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

print("=" * 70)
print("  A股短线策略有效性验证")
print("=" * 70)

try:
    from backtest.validator import StrategyValidator
    print("\n[*] 正在初始化策略验证器...")
    validator = StrategyValidator()
    print("[*] 开始运行验证（10只股票，2020-2024年回测）...")
    print("[*] 这可能需要几分钟，请耐心等待...\n")
    validator.validate_strategy()
except Exception as e:
    print(f"[ERROR] 验证失败: {e}")
    import traceback
    traceback.print_exc()
