# -*- coding: utf-8 -*-
"""
全市场深度筛选 v3 - 寻找被错杀的价值股
目标：PE/PB低 + 业绩稳定 + 被战争恐慌错杀 = 有望翻倍
"""
import akshare as ak
import pandas as pd
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("全市场深度筛选 v3 - 寻找被错杀的价值股")
print("=" * 70)
print()

# ========================
# 第1步：获取全市场数据
# ========================
print("[1/4] 获取全市场数据（包含PE/PB）...")
start = time.time()
try:
    df = ak.stock_zh_a_spot_em()
    elapsed = time.time() - start
    print(f"    成功获取 {len(df)} 只股票，耗时 {elapsed:.1f}秒")
    print(f"    字段: {list(df.columns)}")
except Exception as e:
    print(f"    获取失败: {e}")
    sys.exit(1)

print()

# ========================
# 第2步：数据清洗
# ========================
print("[2/4] 数据清洗...")

# 转换为数值型
df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
df['市盈率-动态'] = pd.to_numeric(df['市盈率-动态'], errors='coerce')
df['市净率'] = pd.to_numeric(df['市净率'], errors='coerce')
df['总市值'] = pd.to_numeric(df['总市值'], errors='coerce')
df['流通市值'] = pd.to_numeric(df['流通市值'], errors='coerce')
df['换手率'] = pd.to_numeric(df['换手率'], errors='coerce')

# 过滤ST、停牌等
df = df[df['名称'].str.contains('ST', na=False) == False]
df = df[df['最新价'] > 0]
df = df[df['最新价'] < 1000]  # 排除高价股

# 有效PE过滤（排除负PE和异常值）
df_valid_pe = df[(df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 100)]

print(f"    清洗后剩余 {len(df_valid_pe)} 只股票")
print()

# ========================
# 第3步：多维度筛选
# ========================
print("[3/4] 多维度筛选...")

# 维度1：低估值
low_pe = df_valid_pe[(df_valid_pe['市盈率-动态'] < 20)].copy()
low_pe['维度1_低PE'] = 1

low_pb = df_valid_pe[(df_valid_pe['市净率'] < 2)].copy()
low_pb['维度1_低PB'] = 1

# 维度2：中小市值（容易被错杀）
mid_cap = df_valid_pe[(df_valid_pe['流通市值'] > 50) & (df_valid_pe['流通市值'] < 500)].copy()
mid_cap['维度2_中小市值'] = 1

# 维度3：今日被错杀（跌幅大）
# 但今天周六，看昨日收盘情况
# 筛选跌幅较大的
dropped = df_valid_pe[(df_valid_pe['涨跌幅'] < -3)].copy()
dropped['维度3_超跌'] = 1

# 维度4：非战争受损板块
# 排除：航空、旅游、酒店
safe_sectors = df_valid_pe[~df_valid_pe['名称'].str.contains('航空|旅游|酒店', na=False, regex=True)].copy()
safe_sectors['维度4_非受损'] = 1

# 维度5：优质行业
# 银行、医药、消费、科技
good_sectors = df_valid_pe[
    (df_valid_pe['名称'].str.contains('银行|医药|医疗|食品|饮料|白酒|科技|电子|软件', na=False, regex=True))
].copy()
good_sectors['维度5_优质行业'] = 1

print(f"    低PE(<20): {len(low_pe)} 只")
print(f"    低PB(<2): {len(low_pb)} 只")
print(f"    中小市值(50-500亿): {len(mid_cap)} 只")
print(f"    超跌(>-3%): {len(dropped)} 只")
print(f"    非受损板块: {len(safe_sectors)} 只")
print(f"    优质行业: {len(good_sectors)} 只")
print()

# ========================
# 第4步：综合评分
# ========================
print("[4/4] 综合评分...")

# 合并筛选结果
df_result = df_valid_pe.copy()
df_result['低PE'] = (df_result['市盈率-动态'] < 20).astype(int)
df_result['低PB'] = (df_result['市净率'] < 2).astype(int)
df_result['中小市值'] = ((df_result['流通市值'] > 50) & (df_result['流通市值'] < 500)).astype(int)
df_result['超跌'] = (df_result['涨跌幅'] < -3).astype(int)
df_result['优质行业'] = df_result['名称'].str.contains('银行|医药|医疗|食品|饮料|白酒|科技|电子|软件', na=False, regex=True).astype(int)
df_result['非受损'] = (~df_result['名称'].str.contains('航空|旅游|酒店', na=False, regex=True)).astype(int)

# 计算综合得分
# 低PE: 30分, 低PB: 20分, 中小市值: 15分, 超跌: 20分, 优质行业: 15分
df_result['得分'] = (
    df_result['低PE'] * 30 +
    df_result['低PB'] * 20 +
    df_result['中小市值'] * 15 +
    df_result['超跌'] * 20 +
    df_result['优质行业'] * 15
)

# 按得分排序
df_result = df_result.sort_values('得分', ascending=False)

# ========================
# 输出结果
# ========================
print()
print("=" * 70)
print("筛选结果")
print("=" * 70)

# TOP 50
top50 = df_result.head(50)

print(f"\n[TOP 50 被错杀价值股]\n")

for i, row in top50.iterrows():
    name = row['名称']
    code = row['代码']
    price = row['最新价']
    pe = row['市盈率-动态']
    pb = row['市净率']
    change = row['涨跌幅']
    mkt_cap = row['流通市值']
    score = row['得分']

    print(f"{name}({code})")
    print(f"  价格: ¥{price:.2f} | 涨跌: {change:+.2f}% | PE: {pe:.1f} | PB: {pb:.2f} | 流通市值: {mkt_cap/10000:.1f}亿 | 得分: {score}")

print()
print("=" * 70)

# 按行业分类
print("\n[按行业分类]\n")

categories = {
    '银行': df_result[df_result['名称'].str.contains('银行', na=False)].head(5),
    '医药': df_result[df_result['名称'].str.contains('医药|医疗', na=False, regex=True)].head(5),
    '消费': df_result[df_result['名称'].str.contains('食品|饮料|白酒|乳', na=False, regex=True)].head(5),
    '科技': df_result[df_result['名称'].str.contains('科技|电子|软件|芯', na=False, regex=True)].head(5),
}

for cat, stocks in categories.items():
    if len(stocks) > 0:
        print(f"【{cat}】")
        for _, row in stocks.iterrows():
            print(f"  {row['名称']}({row['代码']}) PE:{row['市盈率-动态']:.1f} PB:{row['市净率']:.2f} 得分:{row['得分']}")
        print()

# ========================
# 深度分析TOP 10
# ========================
print("=" * 70)
print("[TOP 10 深度分析]")
print("=" * 70)

for rank, (_, row) in enumerate(df_result.head(10).iterrows(), 1):
    name = row['名称']
    code = row['代码']
    price = row['最新价']
    pe = row['市盈率-动态']
    pb = row['市净率']
    change = row['涨跌幅']
    mkt_cap = row['流通市值']
    score = row['得分']

    print(f"\n{rank}. {name}({code})")
    print("-" * 50)

    # 估值分析
    pe_level = "极低" if pe < 10 else "较低" if pe < 20 else "合理"
    pb_level = "极低" if pb < 1 else "较低" if pb < 2 else "合理"

    # 行业特征
    sector = "未知"
    if any(k in name for k in ['银行']):
        sector = "银行"
    elif any(k in name for k in ['医药', '医疗']):
        sector = "医药"
    elif any(k in name for k in ['食品', '饮料', '白酒']):
        sector = "消费"
    elif any(k in name for k in ['科技', '电子', '软件']):
        sector = "科技"
    elif any(k in name for k in ['化工', '材料']):
        sector = "化工"

    # 错杀原因推测
    reason = ""
    if change < -5:
        reason = "战争恐慌被错杀"
    elif pe < 15:
        reason = "估值被杀到历史低位"
    else:
        reason = "市场情绪过度悲观"

    print(f"  股价: ¥{price:.2f}")
    print(f"  估值: PE={pe:.1f}({pe_level}) PB={pb:.2f}({pb_level})")
    print(f"  流通市值: {mkt_cap/10000:.1f}亿")
    print(f"  今日涨跌: {change:+.2f}%")
    print(f"  行业: {sector}")
    print(f"  错杀原因: {reason}")
    print(f"  综合得分: {score}")

    # 翻倍可能性
    if pe < 10 and pb < 1 and sector in ['银行', '医药', '消费']:
        potential = "极高"
        reason2 = "估值极低+防御行业"
    elif pe < 15 and sector in ['医药', '消费']:
        potential = "高"
        reason2 = "估值低+行业优质"
    elif pe < 20 and sector == '科技':
        potential = "较高"
        reason2 = "超跌科技股"
    else:
        potential = "中等"
        reason2 = "需要催化剂"

    print(f"  翻倍潜力: {potential} ({reason2})")

print()
print("=" * 70)
print("说明：以上仅为数据分析结果，不构成投资建议")
print("=" * 70)
