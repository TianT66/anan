# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('=' * 70)
print('迈瑞医疗 300760 2025年年报深度解读')
print('=' * 70)

try:
    # 财务摘要 - 按年度
    df = ak.stock_financial_abstract_ths(symbol='300760', indicator='按年度')
    if df is not None:
        print('\n【年度营收利润】')
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            period = str(row['报告期'])
            revenue = row.get('营业总收入', 'N/A')
            profit = row.get('净利润', 'N/A')
            rev_growth = row.get('营业总收入同比增长率', 'N/A')
            profit_growth = row.get('净利润同比增长率', 'N/A')
            roe = row.get('净资产收益率', 'N/A')
            gross = row.get('销售毛利率', 'N/A')
            
            print('\n' + period)
            print('  营收: ' + str(revenue) + ' (' + str(rev_growth) + ')')
            print('  利润: ' + str(profit) + ' (' + str(profit_growth) + ')')
            print('  ROE: ' + str(roe) + ' 毛利率: ' + str(gross))
except Exception as e:
    print('Error: ' + str(e))

print('\n' + '=' * 70)
print('【ROE趋势对比】')
print('=' * 70)

try:
    df = ak.stock_financial_analysis_indicator(symbol='300760', start_year='2022')
    if df is not None:
        print('\n年份    Q1     Q2     Q3     Q4     全年')
        print('-' * 50)
        years = {}
        for i in range(len(df)):
            row = df.iloc[i]
            date = str(row['日期'])
            roe = row.get('净资产收益率(%)', 0)
            year = date[:4]
            quarter = date[5:7]
            
            if year not in years:
                years[year] = {}
            years[year][quarter] = roe
        
        for year in sorted(years.keys(), reverse=True):
            q = years[year]
            q1 = q.get('03', 0)
            q2 = q.get('06', 0)
            q3 = q.get('09', 0)
            q4 = q.get('12', 0)
            total = q1 + q2 + q3 + q4
            print(year + '   ' + str(round(q1,1)) + '%  ' + str(round(q2,1)) + '%  ' + str(round(q3,1)) + '%  ' + str(round(q4,1)) + '%  ' + str(round(total,1)) + '%')
except Exception as e:
    print('ROE error: ' + str(e))
