# -*- coding: utf-8 -*-
import akshare as ak
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import sys
sys.stdout.reconfigure(encoding='utf-8')

print('=' * 70)
print('全市场扫描 - 10维度框架选股')
print('=' * 70)

# 获取全市场数据
print('\n[1/4] 获取全市场数据...')
df = ak.stock_zh_a_spot_em()
print('  获取 ' + str(len(df)) + ' 只股票')

# 数据清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')
df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')

# 排除ST
df = df[df['名称'].str.contains('ST', na=False) == False]
print('  排除ST后: ' + str(len(df)) + ' 只')

# 排除问题行业
print('\n[2/4] 行业筛选...')
exclude = ['银行', '证券', '保险', '信托', '期货', '地产', '万科', '煤炭', '钢铁', '石油', '航空', '航运', '旅游', '酒店', '电子', '芯片', '半导', '光伏', '锂电', '新能源', '猪', '牧原', '军工', '国防']

def is_ok(name):
    for kw in exclude:
        if kw in name:
            return False
    return True

df = df[df['名称'].apply(is_ok)]
print('  排除问题行业后: ' + str(len(df)) + ' 只')

# 估值筛选
print('\n[3/4] 估值筛选...')
df = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 20)]
df = df[df['市净率'] < 2]
df = df[df['流通市值'] > 50]
print('  PE<20 PB<2 市值>50亿: ' + str(len(df)) + ' 只')

# 超跌筛选
print('\n[4/4] 超跌筛选...')
df = df[df['年初至今涨跌幅'] < 0]
df = df.sort_values('年初至今涨跌幅')
print('  年初至今下跌: ' + str(len(df)) + ' 只')

# 行业分类
print('\n' + '=' * 70)
print('【按行业分类初选结果】')
print('=' * 70)

# 医药
med = df[df['名称'].apply(lambda x: any(k in x for k in ['药', '医', '生物', '康', '济', '仁']))]
print('\n【医药生物】(' + str(len(med)) + '只)')
for _, r in med.head(10).iterrows():
    print('  ' + r['名称'] + '(' + r['代码'] + ') PE=' + str(round(r['市盈率-动态'],1)) + ' PB=' + str(round(r['市净率'],2)) + ' 年初' + str(round(r['年初至今涨跌幅'],1)) + '%')

# 消费
con = df[df['名称'].apply(lambda x: any(k in x for k in ['酒', '食', '饮', '乳', '肉', '家', '电', '服', '纺', '鞋']))]
print('\n【消费】(' + str(len(con)) + '只)')
for _, r in con.head(10).iterrows():
    print('  ' + r['名称'] + '(' + r['代码'] + ') PE=' + str(round(r['市盈率-动态'],1)) + ' PB=' + str(round(r['市净率'],2)) + ' 年初' + str(round(r['年初至今涨跌幅'],1)) + '%')

# 公用事业
util = df[df['名称'].apply(lambda x: any(k in x for k in ['电', '水', '气', '能', '环保', '高速', '公路', '铁路']))]
print('\n【公用事业】(' + str(len(util)) + '只)')
for _, r in util.head(10).iterrows():
    print('  ' + r['名称'] + '(' + r['代码'] + ') PE=' + str(round(r['市盈率-动态'],1)) + ' PB=' + str(round(r['市净率'],2)) + ' 年初' + str(round(r['年初至今涨跌幅'],1)) + '%')

# 制造业
manu = df[df['名称'].apply(lambda x: any(k in x for k in ['机', '械', '设', '备', '造', '工', '材', '建', '化', '药', '汽', '车']))]
# 排除医药
manu_codes = set(manu['代码']) - set(med['代码'])
manu = manu[manu['代码'].isin(manu_codes)]
print('\n【制造业】(' + str(len(manu)) + '只)')
for _, r in manu.head(10).iterrows():
    print('  ' + r['名称'] + '(' + r['代码'] + ') PE=' + str(round(r['市盈率-动态'],1)) + ' PB=' + str(round(r['市净率'],2)) + ' 年初' + str(round(r['年初至今涨跌幅'],1)) + '%')

# 保存初选结果
result = pd.concat([med, con, util, manu])
result = result.drop_duplicates(subset=['代码'])
result = result.sort_values('年初至今涨跌幅')

print('\n' + '=' * 70)
print('【TOP 20 被错杀标的】')
print('=' * 70)
for i, (_, r) in enumerate(result.head(20).iterrows(), 1):
    print(str(i) + '. ' + r['名称'] + '(' + r['代码'] + ') PE=' + str(round(r['市盈率-动态'],1)) + ' PB=' + str(round(r['市净率'],2)) + ' 年初' + str(round(r['年初至今涨跌幅'],1)) + '%')

# 保存
result.head(30).to_csv('screening_result.csv', index=False, encoding='utf-8-sig')
print('\n结果已保存到 screening_result.csv')
