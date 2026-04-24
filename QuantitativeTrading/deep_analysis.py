# -*- coding: utf-8 -*-
"""
深度基本面分析 - 验证是真低估还是假低估
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("深度基本面分析 - 鉴别真假低估")
print("=" * 70)
print()

# 分析标的
targets = [
    {"code": "601528", "name": "瑞丰银行", "reason": "PE5.3 PB0.53 极度低估"},
    {"code": "600015", "name": "华夏银行", "reason": "PE4.2 PB0.36 全市场最低PE"},
    {"code": "600016", "name": "民生银行", "reason": "PE4.4 PB0.30 极度低估"},
    {"code": "601607", "name": "上海医药", "reason": "PE9.0 PB0.82 医药低估"},
    {"code": "600566", "name": "济川药业", "reason": "PE17.3 今日-3.36%"},
]

for target in targets:
    code = target["code"]
    name = target["name"]
    print(f"\n{'=' * 70}")
    print(f"【{name}({code})】")
    print(f"入选原因: {target['reason']}")
    print("-" * 70)

    try:
        # 1. 获取基本信息
        print("\n[1] 公司基本信息...")
        try:
            info = ak.stock_individual_info_em(symbol=code)
            if info is not None and not info.empty:
                for _, row in info.iterrows():
                    print(f"  {row['item']}: {row['value']}")
        except Exception as e:
            print(f"  获取失败: {e}")

        time.sleep(0.5)

        # 2. 获取财务指标
        print("\n[2] 财务指标分析...")
        try:
            fin = ak.stock_financial_analysis_indicator(symbol=code, start_year="2022")
            if fin is not None and not fin.empty:
                fin = fin.head(4)
                print(f"  {'指标':<25} {'最新':<12} {'上期':<12}")
                print(f"  {'-'*50}")

                for col in ['摊薄每股收益(元)', '加权每股收益(元)', '净资产收益率(%)']:
                    if col in fin.columns:
                        vals = fin[col].tolist()
                        if len(vals) >= 2:
                            latest = vals[0] if pd.notna(vals[0]) else 0
                            prev = vals[1] if pd.notna(vals[1]) else 0
                            change = "^" if latest > prev else "v" if latest < prev else "->"
                            print(f"  {col:<25} {latest:<12.3f} {prev:<12.3f} {change}")
        except Exception as e:
            print(f"  获取失败: {e}")

        time.sleep(0.5)

        # 3. 获取利润表
        print("\n[3] 盈利能力分析...")
        try:
            profit = ak.stock_profit_sheet_by_report_em(symbol=code)
            if profit is not None and not profit.empty:
                # 营业收入
                if '营业总收入' in profit.columns:
                    rev = profit['营业总收入'].dropna().tolist()
                    if len(rev) >= 2:
                        print(f"  营收: {rev[0]/100000000:.2f}亿 (上期: {rev[1]/100000000:.2f}亿)")
                # 净利润
                if '净利润' in profit.columns:
                    profit_vals = profit['净利润'].dropna().tolist()
                    if len(profit_vals) >= 2:
                        print(f"  净利润: {profit_vals[0]/100000000:.2f}亿 (上期: {profit_vals[1]/100000000:.2f}亿)")
        except Exception as e:
            print(f"  获取失败: {e}")

    except Exception as e:
        print(f"\n  总体分析失败: {e}")

    time.sleep(1)

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
