# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('=' * 70)
print('2026-03-30 11:53 实时扫描')
print('=' * 70)

# 获取指数
idx = ak.stock_zh_index_spot_em()
main = idx[idx['代码'].isin(['000001', '399001', '000300'])]
print('\n【主要指数】')
for _, r in main.iterrows():
    name = r['名称']
    price = r['最新价']
    change = r['涨跌幅']
    print('  ' + name + ': ' + str(price) + ' (' + str(round(change,2)) + '%)')

# 关注标的
targets = [
    ('601607', '上海医药'),
    ('603368', '柳药集团'),
    ('600566', '济川药业'),
    ('000651', '格力电器'),
    ('600027', '华电国际'),
    ('000690', '宝新能源'),
]

df = ak.stock_zh_a_spot_em()
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')

print('\n【关注标的实时价格】')
print('-' * 50)
for code, name in targets:
    row = df[df['代码'] == code]
    if len(row) > 0:
        price = row['最新价'].values[0]
        change = row['涨跌幅'].values[0]
        if change > 0:
            status = 'OK'
        elif change < -2:
            status = 'WARN'
        else:
            status = 'FLAT'
        print(status + ' ' + name + '(' + code + '): ' + str(round(price,2)) + ' ' + str(round(change,2)) + '%')

# 涨跌统计
print('\n【涨跌统计】')
up = len(df[df['涨跌幅'] > 0])
down = len(df[df['涨跌幅'] < 0])
print('  上涨: ' + str(up) + ' 只')
print('  下跌: ' + str(down) + ' 只')
