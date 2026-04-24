# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('=' * 60)
print('2026-03-30 市场扫描')
print('=' * 60)

# 获取持仓相关
targets = [
    ('601528', '瑞丰银行'),
    ('600015', '华夏银行'),
    ('600016', '民生银行'),
    ('601607', '上海医药'),
    ('600566', '济川药业'),
    ('600027', '华电国际'),
    ('000690', '宝新能源'),
    ('000651', '格力电器'),
    ('603368', '柳药集团'),
    ('000623', '吉林敖东'),
]

df = ak.stock_zh_a_spot_em()
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')

print('\n【昨日关注标的今日表现】')
print('-' * 50)
for code, name in targets:
    row = df[df['代码'] == code]
    if len(row) > 0:
        price = row['最新价'].values[0]
        change = row['涨跌幅'].values[0]
        print(str(code) + ' ' + name + ' 价格:' + str(round(price,2)) + ' 涨跌:' + str(round(change,2)) + '%')

# 涨幅榜
print('\n' + '=' * 60)
print('【今日涨幅榜 TOP 10】')
print('=' * 60)
df_up = df.sort_values('涨跌幅', ascending=False)
for i, (_, r) in enumerate(df_up.head(10).iterrows(), 1):
    print(str(i) + '. ' + r['名称'] + '(' + r['代码'] + ') ' + str(round(r['涨跌幅'],2)) + '%')

# 跌幅榜
print('\n' + '=' * 60)
print('【今日跌幅榜 TOP 10】')
print('=' * 60)
df_down = df.sort_values('涨跌幅')
for i, (_, r) in enumerate(df_down.head(10).iterrows(), 1):
    print(str(i) + '. ' + r['名称'] + '(' + r['代码'] + ') ' + str(round(r['涨跌幅'],2)) + '%')
