# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('迈瑞医疗 2024年年报关键数据')
print('=' * 60)

try:
    # 财务摘要
    df = ak.stock_financial_abstract_ths(symbol='300760', indicator='按报告期')
    if df is not None and len(df) > 0:
        # 取最近几年的数据
        print('\n【营收和利润趋势】')
        for i in range(min(15, len(df))):
            row = df.iloc[i]
            period = str(row['报告期'])
            revenue = row['营业总收入']
            profit = row['净利润']
            growth = row['营业总收入同比增长率']
            
            if pd.notna(revenue) and pd.notna(profit):
                print(period + ' 营收:' + str(round(revenue/100, 1)) + '亿 利润:' + str(round(profit/100, 1)) + '亿 增长:' + str(growth))
except Exception as e:
    print('Error: ' + str(e))

print('\n' + '=' * 60)

# 最新季度
try:
    df = ak.stock_financial_analysis_indicator(symbol='300760', start_year='2024')
    if df is not None and len(df) > 0:
        print('\n【2024年季度ROE】')
        for i in range(len(df)):
            row = df.iloc[i]
            date = str(row['日期'])
            roe = row.get('净资产收益率(%)', 'N/A')
            print(date + ': ROE=' + str(roe) + '%')
except Exception as e:
    print('ROE error: ' + str(e))