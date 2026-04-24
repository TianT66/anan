"""
快速回测脚本 - 柳工(000528) 独立版（无外部依赖）
"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import akshare as ak
import pandas as pd
import numpy as np

# 配置
STOCK_CODE = "000528"
STOCK_NAME = "柳工"
START_DATE = "20230101"
END_DATE = "20241231"
INITIAL_CAPITAL = 100000

print("=" * 60)
print(f"  {STOCK_NAME}({STOCK_CODE}) 量化回测分析")
print(f"  时间范围: {START_DATE} ~ {END_DATE}")
print(f"  初始资金: {INITIAL_CAPITAL:,} 元")
print("=" * 60)

# 1. 获取数据
print("\n[1/4] 正在获取行情数据...")
try:
    df = ak.stock_zh_a_hist(
        symbol=STOCK_CODE,
        period="daily",
        start_date=START_DATE,
        end_date=END_DATE,
        adjust="qfq"
    )
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        '日期': 'date', '开盘': 'open', '收盘': 'close',
        '最高': 'high', '最低': 'low', '成交量': 'volume',
        '涨跌幅': 'pct_change'
    })
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    print(f"    获取成功！共 {len(df)} 个交易日")
    print(f"    价格区间: {df['close'].min():.2f} ~ {df['close'].max():.2f} 元")
except Exception as e:
    print(f"    获取失败: {e}")
    sys.exit(1)

# 2. 计算技术指标
print("\n[2/4] 计算技术指标...")
df['ma5']  = df['close'].rolling(5).mean()
df['ma10'] = df['close'].rolling(10).mean()
df['ma20'] = df['close'].rolling(20).mean()
df['ma60'] = df['close'].rolling(60).mean()

delta = df['close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
df['rsi'] = 100 - (100 / (1 + gain / loss))

exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
df['macd_hist'] = df['macd'] - df['macd_signal']
print("    完成！(MA5/10/20/60, RSI14, MACD)")

# 3. 回测函数
def run_backtest(df, strategy_name, signal_col):
    cash = INITIAL_CAPITAL
    position = 0
    avg_price = 0
    trades = []
    equity = []

    for i, row in df.iterrows():
        price = row['close']
        sig = row.get(signal_col, 0)

        if pd.isna(sig):
            equity.append({'date': row['date'], 'value': cash + position * price})
            continue

        prev_sig = df.loc[i-1, signal_col] if i > 0 else 0

        # 买入信号
        if sig == 1 and prev_sig != 1 and position == 0:
            qty = int(cash * 0.9 / price / 100) * 100
            if qty > 0:
                cost = qty * price * 1.0003
                cash -= cost
                position = qty
                avg_price = price
                trades.append({'date': row['date'], 'action': 'buy', 'price': price, 'qty': qty})

        # 卖出信号
        elif sig == -1 and prev_sig != -1 and position > 0:
            revenue = position * price * 0.9987
            pnl = revenue - position * avg_price
            cash += revenue
            trades.append({'date': row['date'], 'action': 'sell', 'price': price, 'qty': position, 'pnl': pnl})
            position = 0

        # 止损 5%
        elif position > 0 and price < avg_price * 0.95:
            revenue = position * price * 0.9987
            pnl = revenue - position * avg_price
            cash += revenue
            trades.append({'date': row['date'], 'action': 'stop', 'price': price, 'qty': position, 'pnl': pnl})
            position = 0

        equity.append({'date': row['date'], 'value': cash + position * price})

    eq = pd.DataFrame(equity)
    final = eq['value'].iloc[-1]
    total_ret = (final - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    max_dd = ((eq['value'].cummax() - eq['value']) / eq['value'].cummax()).max() * 100
    rets = eq['value'].pct_change().fillna(0)
    sharpe = (rets.mean() * 252 - 0.03) / (rets.std() * np.sqrt(252)) if rets.std() > 0 else 0
    buy_trades = [t for t in trades if t['action'] == 'buy']
    win_trades = [t for t in trades if t.get('pnl', 0) > 0]
    win_rate = len(win_trades) / len([t for t in trades if 'pnl' in t]) * 100 if [t for t in trades if 'pnl' in t] else 0

    return {
        'name': strategy_name,
        'final': final,
        'total_ret': total_ret,
        'max_dd': max_dd,
        'sharpe': sharpe,
        'trades': len(buy_trades),
        'win_rate': win_rate,
        'trade_list': trades
    }

# 生成信号
df['sig_ma'] = 0
df.loc[(df['ma5'] > df['ma20']) & (df['ma20'] > df['ma60']), 'sig_ma'] = 1
df.loc[(df['ma5'] < df['ma20']), 'sig_ma'] = -1

df['sig_macd'] = 0
df.loc[df['macd_hist'] > 0, 'sig_macd'] = 1
df.loc[df['macd_hist'] <= 0, 'sig_macd'] = -1

df['sig_rsi'] = 0
df.loc[df['rsi'] < 35, 'sig_rsi'] = 1
df.loc[df['rsi'] > 65, 'sig_rsi'] = -1

# 4. 运行三个策略
print("\n[3/4] 运行回测策略...")
results = []
results.append(run_backtest(df, "三均线策略", "sig_ma"))
results.append(run_backtest(df, "MACD策略  ", "sig_macd"))
results.append(run_backtest(df, "RSI策略   ", "sig_rsi"))

# 买入持有基准
bh_ret = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100

# 5. 输出结果
print("\n[4/4] 回测结果")
print("\n" + "=" * 60)
print(f"  柳工({STOCK_CODE}) 策略回测对比")
print(f"  回测区间: {df['date'].iloc[0].strftime('%Y-%m-%d')} ~ {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
print("=" * 60)
print(f"{'策略':<12} {'总收益':>8} {'最大回撤':>9} {'夏普比率':>9} {'交易次数':>9} {'胜率':>8}")
print("-" * 60)
for r in results:
    print(f"{r['name']:<12} {r['total_ret']:>+7.2f}%  {r['max_dd']:>7.2f}%  {r['sharpe']:>9.2f}  {r['trades']:>9}  {r['win_rate']:>6.1f}%")
print("-" * 60)
print(f"{'买入持有':<12} {bh_ret:>+7.2f}%  {'--':>7}  {'--':>9}  {'1':>9}  {'--':>6}")
print("=" * 60)

# 最佳策略
best = max(results, key=lambda x: x['total_ret'])
print(f"\n  最佳策略: {best['name'].strip()} (收益 {best['total_ret']:+.2f}%)")

# 最近交易记录
print(f"\n  最近交易记录 ({best['name'].strip()}):")
print(f"  {'日期':<12} {'操作':<6} {'价格':>8} {'数量':>8} {'盈亏':>10}")
print("  " + "-" * 50)
for t in best['trade_list'][-8:]:
    action_map = {'buy': '买入', 'sell': '卖出', 'stop': '止损'}
    action = action_map.get(t['action'], t['action'])
    pnl_str = f"{t.get('pnl', 0):+.2f}" if 'pnl' in t else "--"
    print(f"  {t['date'].strftime('%Y-%m-%d'):<12} {action:<6} {t['price']:>8.2f} {t['qty']:>8} {pnl_str:>10}")

print("\n" + "=" * 60)
print("  风险提示：回测结果仅供参考，不构成投资建议！")
print("=" * 60)
