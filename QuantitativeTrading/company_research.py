# -*- coding: utf-8 -*-
"""
深度调研 - 这三家公司到底是做什么的？
"""
import akshare as ak
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

companies = [
    {"code": "002489", "name": "浙江永强"},
    {"code": "603049", "name": "中策橡胶"},
    {"code": "601628", "name": "中国人寿"},
]

for c in companies:
    code = c["code"]
    name = c["name"]
    print("=" * 70)
    print(f"【{name}({code})】")
    print("=" * 70)

    try:
        # 基本信息
        print("\n[1] 公司主营业务")
        info = ak.stock_individual_info_em(symbol=code)
        if info is not None and not info.empty:
            for _, row in info.iterrows():
                if row['item'] in ['所属行业', '主营业务', '经营范围', '公司名称']:
                    print(f"  {row['item']}: {row['value']}")

        time.sleep(0.5)

        # 财务概况
        print("\n[2] 近4期财务数据")
        fin = ak.stock_financial_analysis_indicator(symbol=code, start_year="2022")
        if fin is not None and not fin.empty:
            fin = fin.head(4)
            cols = ['净资产收益率(%)', '销售毛利率(%)', '销售净利率(%)', '资产负债率(%)']
            print(f"  {'指标':<20} {'Q4':<10} {'Q3':<10} {'Q2':<10} {'Q1':<10}")
            print(f"  {'-'*60}")
            for col in cols:
                if col in fin.columns:
                    vals = []
                    for v in fin[col].tolist()[:4]:
                        if v is not None and str(v) != 'nan':
                            vals.append(f"{v:.2f}")
                        else:
                            vals.append("-")
                    print(f"  {col:<20} {vals[0]:<10} {vals[1]:<10} {vals[2]:<10} {vals[3]:<10}")

        time.sleep(0.5)

        # 盈利能力趋势
        print("\n[3] 盈利能力趋势分析")
        if fin is not None and not fin.empty:
            roe_col = '净资产收益率(%)'
            if roe_col in fin.columns:
                roe_vals = fin[roe_col].dropna().tolist()
                if len(roe_vals) >= 4:
                    print(f"  ROE近4期: {', '.join([f'{v:.2f}%' for v in roe_vals])}")
                    roe_trend = roe_vals[0] - roe_vals[-1]
                    if roe_trend > 2:
                        print(f"  趋势判断: ROE在上升 ↑ (上升{roe_trend:.1f}个百分点)")
                    elif roe_trend < -2:
                        print(f"  趋势判断: ROE在下降 ↓ (下降{-roe_trend:.1f}个百分点)")
                    else:
                        print(f"  趋势判断: ROE基本稳定 →")

        time.sleep(0.5)

        # 估值分析
        print("\n[4] 当前估值分析")
        spot = ak.stock_zh_a_spot_em()
        if spot is not None and not spot.empty:
            row = spot[spot['代码'] == code]
            if not row.empty:
                row = row.iloc[0]
                pe = row['市盈率-动态']
                pb = row['市净率']
                price = row['最新价']
                print(f"  当前价: ¥{price:.2f}")
                print(f"  PE: {pe:.1f} (历史分位?)")
                print(f"  PB: {pb:.2f}")

    except Exception as e:
        print(f"  分析失败: {e}")

    print()

print("=" * 70)
