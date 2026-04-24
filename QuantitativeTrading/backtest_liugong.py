"""
快速回测脚本 - 柳工(000528)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import akshare as ak
import pandas as pd
from backtest.backtest_engine import BacktestEngine
from strategies.ma_cross_strategy import MAStrategy, MACDStrategy, RSIStrategy
from utils.tools import calculate_sharpe_ratio, calculate_max_drawdown

# 配置
STOCK_CODE = "000528"
STOCK_NAME = "柳工"
START_DATE = "20230101"
END_DATE = "20240331"

print(f"\n{'='*60}")
print(f"📊 {STOCK_NAME}({STOCK_CODE}) 量化回测分析")
print(f"{'='*60}\n")

# 1. 获取数据
print("📥 正在获取数据...")
try:
    df = ak.stock_zh_a_hist(
        symbol=STOCK_CODE,
        period="daily",
        start_date=START_DATE,
        end_date=END_DATE,
        adjust="qfq"
    )
    
    # 清洗数据
    df.columns = [col.strip() for col in df.columns]
    df = df.rename(columns={
        '日期': 'date', '股票代码': 'code', '开盘': 'open',
        '收盘': 'close', '最高': 'high', '最低': 'low',
        '成交量': 'volume', '成交额': 'amount',
        '涨跌幅': 'pct_change', '涨跌额': 'change', 
        '换手率': 'turnover', '振幅': 'amplitude'
    })
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"✅ 获取数据成功！共 {len(df)} 个交易日")
    print(f"   时间范围: {df['date'].min().date()} ~ {df['date'].max().date()}")
    
except Exception as e:
    print(f"❌ 获取数据失败: {e}")
    sys.exit(1)

# 2. 计算技术指标
print("\n📈 计算技术指标...")

# 均线
df['ma5'] = df['close'].rolling(window=5).mean()
df['ma10'] = df['close'].rolling(window=10).mean()
df['ma20'] = df['close'].rolling(window=20).mean()
df['ma60'] = df['close'].rolling(window=60).mean()

# RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

# MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
df['histogram'] = df['macd'] - df['signal_line']

print("✅ 指标计算完成")

# 3. 运行回测 - 三均线策略
print("\n" + "="*60)
print("🚀 策略一：三均线策略 (MA5 > MA20 > MA60)")
print("="*60)

# 初始化回测引擎
engine = BacktestEngine()
engine.initial_capital = 100000
engine.cash = 100000
engine.positions = {}
engine.trades = []
engine.equity_curve = []

# 三均线参数
df['position'] = 0
df.loc[(df['ma5'] > df['ma20']) & (df['ma20'] > df['ma60']), 'position'] = 1

# 模拟交易
for i, row in df.iterrows():
    if pd.isna(row['position']):
        continue
    
    signal = 0
    if i > 0 and df.loc[i-1, 'position'] == 0 and row['position'] == 1:
        signal = 1  # 买入
    elif i > 0 and df.loc[i-1, 'position'] == 1 and row['position'] == 0:
        signal = -1  # 卖出
    
    price = row['close']
    
    if signal == 1:
        # 买入 30% 仓位
        buy_ratio = 0.3
        available_cash = engine.cash * buy_ratio
        quantity = int(available_cash / price / 100) * 100
        if quantity > 0:
            cost = price * quantity * 1.0003
            engine.cash -= cost
            engine.positions[STOCK_CODE] = {'quantity': quantity, 'avg_price': price}
            engine.trades.append({
                'date': row['date'], 'action': 'buy', 
                'price': price, 'quantity': quantity, 'type': '三均线'
            })
    
    elif signal == -1 and STOCK_CODE in engine.positions:
        pos = engine.positions[STOCK_CODE]
        revenue = price * pos['quantity'] * 0.9987
        engine.cash += revenue
        engine.trades.append({
            'date': row['date'], 'action': 'sell',
            'price': price, 'quantity': pos['quantity'], 
            'pnl': revenue - pos['quantity'] * pos['avg_price'], 'type': '三均线'
        })
        del engine.positions[STOCK_CODE]
    
    # 记录权益
    pos_value = engine.positions.get(STOCK_CODE, {}).get('quantity', 0) * price
    engine.equity_curve.append({
        'date': row['date'],
        'value': engine.cash + pos_value
    })

# 计算结果
equity_df = pd.DataFrame(engine.equity_curve)
final_value = equity_df['value'].iloc[-1]
total_return = (final_value - 100000) / 100000 * 100
max_dd = calculate_max_drawdown(equity_df['value']) * 100

returns = equity_df['value'].pct_change().fillna(0)
sharpe = calculate_sharpe_ratio(returns)

print(f"\n📊 回测结果:")
print(f"   初始资金:     ¥100,000")
print(f"   最终市值:     ¥{final_value:,.2f}")
print(f"   总收益率:     {total_return:+.2f}%")
print(f"   最大回撤:     {max_dd:.2f}%")
print(f"   夏普比率:     {sharpe:.2f}")
print(f"   交易次数:     {len([t for t in engine.trades if t['action'] == 'buy'])}")

# 4. 运行回测 - MACD策略
print("\n" + "="*60)
print("🚀 策略二：MACD 金叉死叉策略")
print("="*60)

engine2 = BacktestEngine()
engine2.initial_capital = 100000
engine2.cash = 100000
engine2.positions = {}
engine2.trades = []
engine2.equity_curve = []

df['macd_position'] = 0
df.loc[df['histogram'] > 0, 'macd_position'] = 1

for i, row in df.iterrows():
    if pd.isna(row['macd_position']):
        continue
    
    signal = 0
    if i > 0 and df.loc[i-1, 'macd_position'] == 0 and row['macd_position'] == 1:
        signal = 1
    elif i > 0 and df.loc[i-1, 'macd_position'] == 1 and row['macd_position'] == 0:
        signal = -1
    
    price = row['close']
    
    if signal == 1:
        buy_ratio = 0.3
        available_cash = engine2.cash * buy_ratio
        quantity = int(available_cash / price / 100) * 100
        if quantity > 0:
            cost = price * quantity * 1.0003
            engine2.cash -= cost
            engine2.positions[STOCK_CODE] = {'quantity': quantity, 'avg_price': price}
            engine2.trades.append({
                'date': row['date'], 'action': 'buy',
                'price': price, 'quantity': quantity, 'type': 'MACD'
            })
    
    elif signal == -1 and STOCK_CODE in engine2.positions:
        pos = engine2.positions[STOCK_CODE]
        revenue = price * pos['quantity'] * 0.9987
        engine2.cash += revenue
        engine2.trades.append({
            'date': row['date'], 'action': 'sell',
            'price': price, 'quantity': pos['quantity'],
            'pnl': revenue - pos['quantity'] * pos['avg_price'], 'type': 'MACD'
        })
        del engine2.positions[STOCK_CODE]
    
    pos_value = engine2.positions.get(STOCK_CODE, {}).get('quantity', 0) * price
    engine2.equity_curve.append({
        'date': row['date'],
        'value': engine2.cash + pos_value
    })

equity_df2 = pd.DataFrame(engine2.equity_curve)
final_value2 = equity_df2['value'].iloc[-1]
total_return2 = (final_value2 - 100000) / 100000 * 100
max_dd2 = calculate_max_drawdown(equity_df2['value']) * 100
returns2 = equity_df2['value'].pct_change().fillna(0)
sharpe2 = calculate_sharpe_ratio(returns2)

print(f"\n📊 回测结果:")
print(f"   初始资金:     ¥100,000")
print(f"   最终市值:     ¥{final_value2:,.2f}")
print(f"   总收益率:     {total_return2:+.2f}%")
print(f"   最大回撤:     {max_dd2:.2f}%")
print(f"   夏普比率:     {sharpe2:.2f}")
print(f"   交易次数:     {len([t for t in engine2.trades if t['action'] == 'buy'])}")

# 5. 对比结果
print("\n" + "="*60)
print("📊 策略对比总结")
print("="*60)
print(f"\n{'策略':<15} {'收益率':<12} {'最大回撤':<12} {'夏普比率':<10} {'交易次数':<10}")
print("-" * 60)
print(f"{'三均线策略':<15} {total_return:>+8.2f}%    {max_dd:>8.2f}%    {sharpe:>8.2f}    {len([t for t in engine.trades if t['action'] == 'buy']):<10}")
print(f"{'MACD策略':<15} {total_return2:>+8.2f}%    {max_dd2:>8.2f}%    {sharpe2:>8.2f}    {len([t for t in engine2.trades if t['action'] == 'buy']):<10}")

# 基准收益（买入持有）
buy_hold_return = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
print(f"{'买入持有':<15} {buy_hold_return:>+8.2f}%    {'--':>8}    {'--':>8}    {'1次':<10}")

# 保存数据
output_file = Path("data") / f"{STOCK_CODE}_backtest_result.csv"
output_file.parent.mkdir(exist_ok=True)
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n💾 数据已保存: {output_file}")

# 最近交易记录
print("\n" + "="*60)
print("📋 最近交易记录 (三均线策略)")
print("="*60)
for trade in engine.trades[-6:]:
    if trade['action'] == 'buy':
        print(f"  📈 买入 {trade['date'].strftime('%Y-%m-%d')}  @ ¥{trade['price']:.2f} × {trade['quantity']}股")
    else:
        pnl = trade.get('pnl', 0)
        print(f"  📉 卖出 {trade['date'].strftime('%Y-%m-%d')}  @ ¥{trade['price']:.2f} × {trade['quantity']}股  盈亏: {pnl:+.2f}")

print("\n" + "="*60)
print("⚠️ 风险提示：以上回测结果仅供参考，不构成投资建议！")
print("="*60)
