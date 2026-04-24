# -*- coding: utf-8 -*-
"""
导入历史交易记录到进化引擎
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 数据目录
data_dir = Path(__file__).parent / "QuantitativeTrading" / "evolution_data"
data_dir.mkdir(parents=True, exist_ok=True)
trades_file = data_dir / "trades.json"

# 历史交易数据（根据memory记录整理）
historical_trades = [
    {
        "id": 1,
        "symbol": "512400",
        "name": "有色金属ETF",
        "action": "buy",
        "price": 3.38,  # 估算成本（亏损42.31%反推）
        "shares": 1000,
        "reason": {
            "technical": "周期股行情",
            "fundamental": "有色金属涨价预期",
            "sentiment": "乐观",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-02-15T10:00:00",
        "close_price": 1.95,
        "close_reason": "止损",
        "profit_pct": -0.4231,
        "holding_days": 30,
        "closed_at": "2026-03-17T14:30:00"
    },
    {
        "id": 2,
        "symbol": "588000",
        "name": "科创50ETF",
        "action": "buy",
        "price": 1.50,  # 估算成本
        "shares": 1000,
        "reason": {
            "technical": "科技反弹预期",
            "fundamental": "科创板估值低",
            "sentiment": "中性",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-02-20T10:00:00",
        "close_price": 1.39,
        "close_reason": "止损",
        "profit_pct": -0.0733,
        "holding_days": 25,
        "closed_at": "2026-03-17T14:30:00"
    },
    {
        "id": 3,
        "symbol": "516010",
        "name": "游戏ETF",
        "action": "buy",
        "price": 1.47,  # 估算成本
        "shares": 1000,
        "reason": {
            "technical": "游戏版号放开",
            "fundamental": "AI+游戏概念",
            "sentiment": "乐观",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-02-10T10:00:00",
        "close_price": 0.99,
        "close_reason": "止损",
        "profit_pct": -0.3265,
        "holding_days": 35,
        "closed_at": "2026-03-17T14:30:00"
    },
    {
        "id": 4,
        "symbol": "159998",
        "name": "计算机ETF",
        "action": "buy",
        "price": 1.07,  # 估算成本
        "shares": 1000,
        "reason": {
            "technical": "科技反弹",
            "fundamental": "计算机行业复苏",
            "sentiment": "中性",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-02-25T10:00:00",
        "close_price": 0.99,
        "close_reason": "止损",
        "profit_pct": -0.0748,
        "holding_days": 20,
        "closed_at": "2026-03-17T14:30:00"
    },
    {
        "id": 5,
        "symbol": "515980",
        "name": "AI ETF",
        "action": "buy",
        "price": 1.0098,
        "shares": 1000,
        "reason": {
            "technical": "AI概念热",
            "fundamental": "AI产业趋势",
            "sentiment": "乐观",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-03-01T10:00:00",
        "close_price": 0.914,
        "close_reason": "止损",
        "profit_pct": -0.0949,
        "holding_days": 26,
        "closed_at": "2026-03-27T09:38:00"
    },
    {
        "id": 6,
        "symbol": "600309",
        "name": "万华化学",
        "action": "buy",
        "price": 79.1818,
        "shares": 100,
        "reason": {
            "technical": "龙头超跌",
            "fundamental": "MDI龙头估值低",
            "sentiment": "中性",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-03-10T10:00:00",
        "close_price": 79.23,
        "close_reason": "减仓止盈",
        "profit_pct": 0.0006,
        "holding_days": 17,
        "closed_at": "2026-03-27T09:38:00"
    },
]

# 还持有的仓位（未平仓）
open_positions = [
    {
        "id": 7,
        "symbol": "300760",
        "name": "迈瑞医疗",
        "action": "buy",
        "price": 178.48,
        "shares": 100,
        "reason": {
            "technical": "龙头超跌",
            "fundamental": "医疗器械龙头",
            "sentiment": "中性",
            "intelligence": "美伊战争防御"
        },
        "market_state": "bear",
        "timestamp": "2026-03-15T10:00:00",
        "status": "open"
    },
    {
        "id": 8,
        "symbol": "601899",
        "name": "紫金矿业",
        "action": "buy",
        "price": 33.0,  # 估算
        "shares": 300,
        "reason": {
            "technical": "黄金涨",
            "fundamental": "金铜龙头",
            "sentiment": "乐观",
            "intelligence": "美伊战争避险"
        },
        "market_state": "bear",
        "timestamp": "2026-03-10T10:00:00",
        "status": "open"
    },
    {
        "id": 9,
        "symbol": "562500",
        "name": "机器人ETF",
        "action": "buy",
        "price": 1.0,  # 估算
        "shares": 1000,
        "reason": {
            "technical": "人形机器人概念",
            "fundamental": "产业政策支持",
            "sentiment": "乐观",
            "intelligence": "未考虑"
        },
        "market_state": "bear",
        "timestamp": "2026-03-05T10:00:00",
        "status": "open"
    },
]

# 合并所有交易
all_trades = historical_trades + open_positions

# 保存
with open(trades_file, 'w', encoding='utf-8') as f:
    json.dump(all_trades, f, ensure_ascii=False, indent=2)

print(f"✅ 已导入 {len(all_trades)} 条交易记录")
print(f"   - 已平仓: {len(historical_trades)} 条")
print(f"   - 持仓中: {len(open_positions)} 条")
print(f"\n📁 保存位置: {trades_file}")

# 显示摘要
print("\n" + "="*50)
print("📊 历史交易摘要")
print("="*50)

total_profit = sum(t["profit_pct"] for t in historical_trades)
win_count = sum(1 for t in historical_trades if t["profit_pct"] > 0)
loss_count = len(historical_trades) - win_count

print(f"\n📌 已平仓交易:")
print(f"  总交易数: {len(historical_trades)}")
print(f"  盈利: {win_count} 笔")
print(f"  亏损: {loss_count} 笔")
print(f"  胜率: {win_count/len(historical_trades):.1%}")
print(f"  累计盈亏: {total_profit:.2%}")

print(f"\n📌 各交易盈亏:")
for t in historical_trades:
    status = "✅" if t["profit_pct"] > 0 else "❌"
    print(f"  {status} {t['name']}: {t['profit_pct']:+.2%}")

print(f"\n📌 当前持仓:")
for t in open_positions:
    print(f"  ⏳ {t['name']}: 成本 {t['price']} 元")
