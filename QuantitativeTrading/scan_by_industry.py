# -*- coding: utf-8 -*-
"""
分行业筛选 - 寻找被错杀的价值股
按行业分组，每个行业找出最被低估的标的
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("分行业筛选 - 寻找被错杀的价值股")
print("=" * 70)

# 第1步：获取全市场数据
print("\n[1/4] 获取全市场数据...")
df = ak.stock_zh_a_spot_em()
print(f"    获取 {len(df)} 只股票")

# 数据清洗
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['年初至今涨跌幅'] = pd.to_numeric(df['年初至今涨跌幅'], errors='coerce')

# 过滤
df = df[df['名称'].str.contains('ST', na=False) == False]
df = df[df['最新价'] > 0]
df_valid = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 30)]
print(f"    清洗后 {len(df_valid)} 只")

# 第2步：行业分类
print("\n[2/4] 行业分类...")

# 行业关键词映射
industry_map = {
    '医药': ['药', '医', '生物', '制药', '康', '华大', '药明', '恒瑞', '片仔癀', '云南白药', '同仁堂', '济川', '敖东'],
    '消费': ['酒', '食品', '饮料', '乳', '奶', '调味', '酱油', '醋', '肉', '养殖', '饲料', '海天', '伊利', '茅台', '五粮液'],
    '家电': ['电器', '家电', '格力', '美的', '海尔', '海信', '空调', '冰箱', '洗衣机'],
    '电力': ['电力', '能源', '发电', '水电', '火电', '风电', '光伏', '新能源', '核电'],
    '基建': ['建筑', '建工', '路桥', '高速', '铁路', '地铁', '隧道', '中建', '中铁', '交建'],
    '化工': ['化工', '化学', '化纤', '塑料', '橡胶', '氮肥', '磷肥', '农药'],
    '机械': ['机械', '设备', '重工', '工程机械', '挖掘', '三一', '中联'],
    '汽车': ['汽车', '车企', '比亚迪', '长城', '长安', '上汽', '广汽', '吉利', '新能源车'],
    '半导体': ['半导体', '芯片', '集成电路', '微电子', '晶圆', '封测', '中芯', '华虹'],
    '通信': ['通信', '电信', '5G', '光纤', '中兴', '烽火'],
    '传媒': ['传媒', '出版', '影视', '游戏', '教育', '广告'],
    '环保': ['环保', '水务', '垃圾', '环卫', '节能', '绿色'],
}

# 排除的行业
exclude_keywords = ['银行', '证券', '保险', '地产', '万科', '航空', '旅游', '酒店', '煤炭', '钢铁', '石油']

# 分类
results = []
for _, row in df_valid.iterrows():
    name = row['名称']
    
    # 排除
    if any(k in name for k in exclude_keywords):
        continue
    
    # 行业分类
    industry = '其他'
    for ind, keywords in industry_map.items():
        if any(k in name for k in keywords):
            industry = ind
            break
    
    results.append({
        'code': row['代码'],
        'name': name,
        'industry': industry,
        'price': row['最新价'],
        'pe': row['市盈率-动态'],
        'pb': row['市净率'],
        'change': row['涨跌幅'],
        'ytd': row['年初至今涨跌幅'] if pd.notna(row['年初至今涨跌幅']) else 0,
        'mkt_cap': row['流通市值'],
    })

df_result = pd.DataFrame(results)
print(f"    排除问题行业后: {len(df_result)} 只")

# 第3步：按行业筛选TOP标的
print("\n[3/4] 按行业筛选TOP标的...")

output = []
for industry in ['医药', '消费', '家电', '电力', '基建', '化工', '机械', '汽车', '半导体', '通信', '传媒', '环保']:
    df_ind = df_result[df_result['industry'] == industry]
    if len(df_ind) == 0:
        continue
    
    # 取PE最低的5只
    top5 = df_ind.nsmallest(5, 'pe')
    
    for _, row in top5.iterrows():
        output.append({
            'industry': industry,
            'code': row['code'],
            'name': row['name'],
            'pe': row['pe'],
            'pb': row['pb'],
            'ytd': row['ytd'],
            'mkt_cap': row['mkt_cap'],
            'price': row['price'],
        })

df_output = pd.DataFrame(output)

# 第4步：获取财务数据（只对筛选后的标的）
print("\n[4/4] 获取财务数据...")

for i, row in df_output.iterrows():
    try:
        fin = ak.stock_financial_analysis_indicator(symbol=row['code'], start_year="2023")
        if fin is not None and len(fin) >= 4:
            if '净资产收益率(%)' in fin.columns:
                roe_vals = fin['净资产收益率(%)'].dropna().tolist()
                if len(roe_vals) >= 4 and all(v > 0 for v in roe_vals[:4]):
                    df_output.loc[i, 'roe'] = roe_vals[0]
                    avg_roe = sum(roe_vals[1:4]) / 3
                    df_output.loc[i, 'roe_change'] = (roe_vals[0] - avg_roe) / avg_roe
                else:
                    df_output.loc[i, 'roe'] = 0
                    df_output.loc[i, 'roe_change'] = 0
            else:
                df_output.loc[i, 'roe'] = 0
                df_output.loc[i, 'roe_change'] = 0
        else:
            df_output.loc[i, 'roe'] = 0
            df_output.loc[i, 'roe_change'] = 0
    except:
        df_output.loc[i, 'roe'] = 0
        df_output.loc[i, 'roe_change'] = 0
    
    time.sleep(0.3)

# 输出
print("\n" + "=" * 70)
print("【分行业筛选结果】")
print("=" * 70)

for industry in ['医药', '消费', '家电', '电力', '基建', '化工', '机械', '汽车', '半导体', '通信', '传媒', '环保']:
    df_ind = df_output[df_output['industry'] == industry]
    if len(df_ind) == 0:
        continue
    
    print(f"\n【{industry}】")
    print("-" * 50)
    
    for i, row in df_ind.iterrows():
        roe_str = f"{row['roe']:.1f}%" if row['roe'] > 0 else "N/A"
        trend = "^" if row['roe_change'] > 0.05 else "->" if row['roe_change'] > -0.1 else "v"
        
        # 评分
        score = 0
        if row['pe'] < 10: score += 30
        elif row['pe'] < 15: score += 20
        elif row['pe'] < 20: score += 10
        
        if row['roe'] > 15: score += 25
        elif row['roe'] > 10: score += 20
        elif row['roe'] > 5: score += 10
        
        if row['roe_change'] > 0: score += 15
        elif row['roe_change'] > -0.1: score += 5
        
        if row['ytd'] < -30: score += 20
        elif row['ytd'] < -20: score += 10
        
        # 目标价
        if row['roe'] > 15: fair_pe = 20
        elif row['roe'] > 10: fair_pe = 15
        elif row['roe'] > 5: fair_pe = 12
        else: fair_pe = 10
        
        target = row['price'] * (fair_pe / row['pe'])
        profit = (target - row['price']) / row['price'] * 100
        
        print(f"  {row['name']}({row['code']}) PE={row['pe']:.1f} ROE={roe_str}({trend}) 年初{row['ytd']:+.0f}% 得分={score} 目标+{profit:.0f}%")

# 汇总
print("\n" + "=" * 70)
print("【全市场TOP 20】（按评分排序）")
print("=" * 70)

# 计算所有标的得分
df_output['score'] = 0
for i, row in df_output.iterrows():
    score = 0
    if row['pe'] < 10: score += 30
    elif row['pe'] < 15: score += 20
    elif row['pe'] < 20: score += 10
    
    if row['roe'] > 15: score += 25
    elif row['roe'] > 10: score += 20
    elif row['roe'] > 5: score += 10
    
    if row['roe_change'] > 0: score += 15
    elif row['roe_change'] > -0.1: score += 5
    
    if row['ytd'] < -30: score += 20
    elif row['ytd'] < -20: score += 10
    
    df_output.loc[i, 'score'] = score

# 排序输出
df_top = df_output.nlargest(20, 'score')
for i, (_, row) in enumerate(df_top.iterrows(), 1):
    roe_str = f"{row['roe']:.1f}%" if row['roe'] > 0 else "N/A"
    trend = "^" if row['roe_change'] > 0.05 else "->" if row['roe_change'] > -0.1 else "v"
    
    if row['roe'] > 15: fair_pe = 20
    elif row['roe'] > 10: fair_pe = 15
    elif row['roe'] > 5: fair_pe = 12
    else: fair_pe = 10
    
    target = row['price'] * (fair_pe / row['pe'])
    profit = (target - row['price']) / row['price'] * 100
    
    print(f"{i:2d}. [{row['industry']}] {row['name']}({row['code']}) PE={row['pe']:.1f} ROE={roe_str}({trend}) 年初{row['ytd']:+.0f}% 得分={row['score']:.0f} 目标+{profit:.0f}%")

print("\n" + "=" * 70)
