# -*- coding: utf-8 -*-
"""
量化交易自主进化引擎
功能：记录交易 → 分析胜率 → 识别模式 → 优化参数 → 迭代策略
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

class EvolutionEngine:
    """自主进化引擎"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "evolution_data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 数据文件
        self.trades_file = self.data_dir / "trades.json"
        self.stats_file = self.data_dir / "stats.json"
        self.patterns_file = self.data_dir / "patterns.json"
        self.params_file = self.data_dir / "params.json"

        # 加载数据
        self.trades = self._load_json(self.trades_file, [])
        self.stats = self._load_json(self.stats_file, {})
        self.patterns = self._load_json(self.patterns_file, [])
        self.params = self._load_json(self.params_file, self._default_params())

    def _load_json(self, path: Path, default):
        """加载JSON文件"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default

    def _save_json(self, path: Path, data):
        """保存JSON文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _default_params(self):
        """默认策略参数"""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "stop_loss_pct": -0.08,  # 止损线 -8%
            "take_profit_pct": 0.15,  # 止盈线 +15%
            "position_weights": {
                "bull": 0.80,  # 牛市仓位
                "bear": 0.30,  # 熊市仓位
                "neutral": 0.50  # 震荡仓位
            },
            "factor_weights": {
                "technical": 0.25,
                "fundamental": 0.30,
                "sentiment": 0.15,
                "intelligence": 0.30  # 情报面权重
            },
            "score_threshold": {
                "buy": 70,  # 买入门槛
                "sell": 40  # 卖出门槛
            }
        }

    def record_trade(self, trade: dict):
        """
        记录一笔交易

        trade = {
            "symbol": "300760",
            "name": "迈瑞医疗",
            "action": "buy",  # buy/sell
            "price": 169.60,
            "shares": 100,
            "reason": {
                "technical": "超跌反弹",
                "fundamental": "龙头估值低",
                "sentiment": "中性",
                "intelligence": "美伊战争防御"
            },
            "market_state": "bear",  # bull/bear/neutral
            "timestamp": "2026-03-27T15:00:00"
        }
        """
        trade["id"] = len(self.trades) + 1
        trade["recorded_at"] = datetime.now().isoformat()
        self.trades.append(trade)
        self._save_json(self.trades_file, self.trades)
        print(f"✅ 交易已记录: {trade['action']} {trade['name']} @{trade['price']}")
        return trade["id"]

    def close_trade(self, trade_id: int, close_price: float, close_reason: str):
        """
        平仓记录

        计算盈亏并更新统计
        """
        trade = next((t for t in self.trades if t.get("id") == trade_id), None)
        if not trade:
            print(f"❌ 未找到交易ID: {trade_id}")
            return None

        # 计算盈亏
        if trade["action"] == "buy":
            profit_pct = (close_price - trade["price"]) / trade["price"]
        else:
            profit_pct = (trade["price"] - close_price) / trade["price"]

        # 更新交易记录
        trade["close_price"] = close_price
        trade["close_reason"] = close_reason
        trade["profit_pct"] = profit_pct
        trade["closed_at"] = datetime.now().isoformat()
        trade["holding_days"] = (
            datetime.fromisoformat(trade["closed_at"]) -
            datetime.fromisoformat(trade["timestamp"])
        ).days

        self._save_json(self.trades_file, self.trades)

        # 更新统计
        self._update_stats(trade)

        print(f"✅ 交易平仓: {trade['name']} 盈亏: {profit_pct:.2%}")
        return trade

    def _update_stats(self, closed_trade: dict):
        """更新统计数据"""
        reason_type = closed_trade.get("close_reason", "unknown")
        market_state = closed_trade.get("market_state", "unknown")

        # 初始化统计结构
        if "total_trades" not in self.stats:
            self.stats = {
                "total_trades": 0,
                "win_count": 0,
                "loss_count": 0,
                "total_profit": 0,
                "win_rate": 0,
                "avg_profit": 0,
                "avg_loss": 0,
                "by_reason": {},
                "by_market": {},
                "by_holding_days": {}
            }

        self.stats["total_trades"] += 1
        self.stats["total_profit"] += closed_trade["profit_pct"]

        if closed_trade["profit_pct"] > 0:
            self.stats["win_count"] += 1
        else:
            self.stats["loss_count"] += 1

        # 胜率
        self.stats["win_rate"] = self.stats["win_count"] / self.stats["total_trades"]

        # 按原因统计
        if reason_type not in self.stats["by_reason"]:
            self.stats["by_reason"][reason_type] = {"count": 0, "profit": 0, "win": 0}
        self.stats["by_reason"][reason_type]["count"] += 1
        self.stats["by_reason"][reason_type]["profit"] += closed_trade["profit_pct"]
        if closed_trade["profit_pct"] > 0:
            self.stats["by_reason"][reason_type]["win"] += 1

        # 按市场状态统计
        if market_state not in self.stats["by_market"]:
            self.stats["by_market"][market_state] = {"count": 0, "profit": 0, "win": 0}
        self.stats["by_market"][market_state]["count"] += 1
        self.stats["by_market"][market_state]["profit"] += closed_trade["profit_pct"]
        if closed_trade["profit_pct"] > 0:
            self.stats["by_market"][market_state]["win"] += 1

        self._save_json(self.stats_file, self.stats)

    def analyze_patterns(self):
        """分析模式，发现规律"""
        closed_trades = [t for t in self.trades if "close_price" in t]
        if len(closed_trades) < 5:
            print("⚠️ 交易样本不足，需要至少5笔已平仓交易")
            return None

        patterns = {
            "best_reasons": [],  # 最赚钱的买入原因
            "worst_reasons": [],  # 最亏钱的买入原因
            "best_market": "",    # 最佳市场环境
            "optimal_holding": 0, # 最佳持仓天数
            "recommendations": []  # 优化建议
        }

        # 分析买入原因
        reason_stats = self.stats.get("by_reason", {})
        sorted_reasons = sorted(
            reason_stats.items(),
            key=lambda x: x[1]["profit"] / max(x[1]["count"], 1),
            reverse=True
        )
        if sorted_reasons:
            patterns["best_reasons"] = [r[0] for r in sorted_reasons[:3]]
            patterns["worst_reasons"] = [r[0] for r in sorted_reasons[-3:]]

        # 分析市场环境
        market_stats = self.stats.get("by_market", {})
        sorted_market = sorted(
            market_stats.items(),
            key=lambda x: x[1]["profit"] / max(x[1]["count"], 1),
            reverse=True
        )
        if sorted_market:
            patterns["best_market"] = sorted_market[0][0]

        # 分析持仓天数
        holding_profits = {}
        for t in closed_trades:
            days = t.get("holding_days", 0)
            bucket = f"{(days // 5) * 5}-{(days // 5) * 5 + 5}"
            if bucket not in holding_profits:
                holding_profits[bucket] = []
            holding_profits[bucket].append(t["profit_pct"])

        best_bucket = max(holding_profits.items(),
                         key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0)
        patterns["optimal_holding"] = best_bucket[0]

        # 生成优化建议
        win_rate = self.stats.get("win_rate", 0)
        if win_rate < 0.4:
            patterns["recommendations"].append("🔴 胜率低于40%，建议提高筛选门槛")
        elif win_rate > 0.6:
            patterns["recommendations"].append("🟢 胜率高于60%，可考虑增加仓位")

        avg_profit = self.stats.get("total_profit", 0) / max(self.stats.get("total_trades", 1), 1)
        if avg_profit < 0:
            patterns["recommendations"].append("🔴 平均亏损，检查止损执行")
        elif avg_profit > 0.05:
            patterns["recommendations"].append("🟢 平均盈利>5%，策略有效")

        self.patterns = patterns
        self._save_json(self.patterns_file, self.patterns)

        print("\n📊 模式分析结果:")
        print(f"  最佳买入原因: {patterns['best_reasons']}")
        print(f"  最佳市场环境: {patterns['best_market']}")
        print(f"  最佳持仓区间: {patterns['optimal_holding']}天")
        for rec in patterns["recommendations"]:
            print(f"  {rec}")

        return patterns

    def optimize_params(self):
        """根据历史数据优化参数"""
        if self.stats.get("total_trades", 0) < 10:
            print("⚠️ 交易样本不足，需要至少10笔交易才能优化参数")
            return self.params

        new_params = self.params.copy()
        recommendations = []

        # 优化止损线
        loss_trades = [t for t in self.trades if t.get("profit_pct", 0) < -0.05]
        if loss_trades:
            avg_max_loss = sum(t["profit_pct"] for t in loss_trades) / len(loss_trades)
            if avg_max_loss < -0.10:
                new_params["stop_loss_pct"] = -0.06  # 更严格止损
                recommendations.append("止损线调整: -8% → -6%（历史平均亏损过大）")
            elif avg_max_loss > -0.06:
                new_params["stop_loss_pct"] = -0.10  # 可放宽
                recommendations.append("止损线调整: -8% → -10%（历史亏损可控）")

        # 优化仓位权重
        market_stats = self.stats.get("by_market", {})
        if "bear" in market_stats and market_stats["bear"]["profit"] < 0:
            new_params["position_weights"]["bear"] = 0.20  # 减少熊市仓位
            recommendations.append("熊市仓位调整: 30% → 20%")

        # 更新版本
        version_parts = new_params["version"].split(".")
        new_params["version"] = f"{version_parts[0]}.{int(version_parts[1])+1}.{version_parts[2]}"
        new_params["last_updated"] = datetime.now().isoformat()

        # 保存
        self.params = new_params
        self._save_json(self.params_file, self.params)

        print(f"\n🔧 参数优化完成 (v{self.params['version']}):")
        for rec in recommendations:
            print(f"  {rec}")

        return new_params

    def get_status(self):
        """获取当前状态"""
        return {
            "total_trades": len(self.trades),
            "closed_trades": len([t for t in self.trades if "close_price" in t]),
            "win_rate": self.stats.get("win_rate", 0),
            "total_profit": self.stats.get("total_profit", 0),
            "params_version": self.params.get("version", "1.0.0")
        }

    def print_report(self):
        """打印完整报告"""
        print("\n" + "="*50)
        print("📊 量化交易进化引擎报告")
        print("="*50)

        status = self.get_status()
        print(f"\n📌 基本信息:")
        print(f"  总交易数: {status['total_trades']}")
        print(f"  已平仓: {status['closed_trades']}")
        print(f"  胜率: {status['win_rate']:.1%}")
        print(f"  累计盈亏: {status['total_profit']:.2%}")
        print(f"  策略版本: v{status['params_version']}")

        if self.stats.get("by_reason"):
            print(f"\n📈 按卖出原因统计:")
            for reason, data in self.stats["by_reason"].items():
                win_rate = data["win"] / max(data["count"], 1)
                avg_profit = data["profit"] / max(data["count"], 1)
                print(f"  {reason}: {data['count']}笔, 胜率{win_rate:.0%}, 平均{avg_profit:.2%}")

        if self.stats.get("by_market"):
            print(f"\n🌍 按市场环境统计:")
            for market, data in self.stats["by_market"].items():
                win_rate = data["win"] / max(data["count"], 1)
                avg_profit = data["profit"] / max(data["count"], 1)
                print(f"  {market}: {data['count']}笔, 胜率{win_rate:.0%}, 平均{avg_profit:.2%}")

        print("\n" + "="*50)


# 测试代码
if __name__ == "__main__":
    engine = EvolutionEngine()
    engine.print_report()
