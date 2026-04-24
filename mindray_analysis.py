# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('迈瑞医疗 2024年年报分析')
print('=' * 60)

# 财务指标
try:
    df = ak.stock_financial_analysis_indicator(symbol='300760', start_year='2022')
    if df is not None and len(df) > 0:
        print('\n【ROE趋势】')
        for i in range(min(8, len(df))):
            row = df.iloc[i]
            date = row['日期']
            roe = row.get('净资产收益率(%)', 'N/A')
            print(date + ': ROE=' + str(roe) + '%')
except Exception as e:
    print('ROE error: ' + str(e))

print('\n' + '=' * 60)

# 营收利润
try:
    df = ak.stock_financial_abstract_ths(symbol='300760', indicator='按报告期')
    if df is not None and len(df) > 0:
        print('\n【营收利润】')
        print(df.head(8).to_string())
except Exception as e:
    print('营收利润 error: ' + str(e))