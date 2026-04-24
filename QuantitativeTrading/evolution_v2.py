# -*- coding: utf-8 -*-
"""
预测型进化系统 v2.0
核心能力：从市场学习 → 建立模型 → 预测推荐 → 持续进化
"""
import json
import os
import sys
import urllib.request
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


class MarketLearner:
    """市场规律学习引擎"""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "learning_data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.data_dir / "market_patterns.json"
        self.patterns = self._load_json(self.patterns_file, self._default_patterns())

    def _load_json(self, path: Path, default):
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default

    def _save_json(self, path: Path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _default_patterns(self):
        """默认市场规律（基于常识，后续通过数据学习更新）"""
        return {
            "version": "1.0.0",
            "last_learned": None,

            # 行业轮动规律（月份→热门板块）
            "sector_rotation": {
                "1": ["消费", "零售"],      # 春节前
                "2": ["农业", "基建"],      # 两会前
                "3": ["两会概念", "政策受益"],
                "4": ["年报业绩", "高送转"],
                "5": ["旅游", "消费"],
                "6": ["半年报", "业绩预增"],
                "7": ["军工", "科技"],
                "8": ["消费电子", "新能源"],
                "9": ["旅游", "消费"],
                "10": ["三季报", "业绩"],
                "11": ["电商", "消费"],
                "12": ["年底行情", "基金重仓"]
            },

            # 技术指标有效性（后续通过回测更新）
            "indicator_effectiveness": {
                "MACD金叉": {"win_rate": 0.52, "avg_return": 0.03},
                "RSI超卖": {"win_rate": 0.58, "avg_return": 0.05},
                "放量突破": {"win_rate": 0.55, "avg_return": 0.04},
                "均线多头": {"win_rate": 0.53, "avg_return": 0.03},
                "缩量回调": {"win_rate": 0.50, "avg_return": 0.02}
            },

            # 情报-股价关联规律
            "intelligence_impact": {
                "战争爆发": {"sector": "军工,能源,黄金", "impact": "涨", "duration": "5-10天"},
                "战争停火": {"sector": "消费,旅游,航空", "impact": "涨", "duration": "3-5天"},
                "降息": {"sector": "券商,地产,基建", "impact": "涨", "duration": "5-15天"},
                "加息": {"sector": "银行,保险", "impact": "涨", "duration": "3-7天"},
                "行业利好政策": {"sector": "该行业", "impact": "涨", "duration": "3-10天"},
                "业绩超预期": {"sector": "该个股", "impact": "涨", "duration": "1-3天"}
            },

            # 龙头股特征（从历史牛股学习）
            "leader_features": {
                "市值": "100-500亿最佳",
                "行业地位": "细分龙头前3",
                "业绩增速": ">30%",
                "机构持仓": ">20%",
                "研发投入": ">5%",
                "催化剂": "政策/技术/订单突破"
            },

            # 风险信号
            "risk_signals": [
                "连续3天主力净流出",
                "RSI超过80超买",
                "放量滞涨",
                "跌破20日均线",
                "重大利空消息"
            ],

            # 机会信号
            "opportunity_signals": [
                "RSI低于30超卖",
                "主力连续净流入3天",
                "突破关键压力位",
                "重大利好政策",
                "业绩超预期"
            ]
        }

    def learn_from_market(self, stock_data: list):
        """
        从市场数据中学习规律

        stock_data: 5000只股票的历史数据
        """
        print("📊 开始学习市场规律...")

        # 1. 学习技术指标有效性
        indicator_stats = self._learn_indicators(stock_data)
        self.patterns["indicator_effectiveness"] = indicator_stats

        # 2. 学习资金流向模式
        flow_patterns = self._learn_capital_flow(stock_data)
        self.patterns["capital_flow_patterns"] = flow_patterns

        # 3. 更新学习时间
        self.patterns["last_learned"] = datetime.now().isoformat()

        # 保存
        self._save_json(self.patterns_file, self.patterns)
        print("✅ 市场规律学习完成")

        return self.patterns

    def _learn_indicators(self, stock_data: list):
        """学习技术指标有效性"""
        # 简化版：实际需要回测引擎
        return self.patterns.get("indicator_effectiveness", {})

    def _learn_capital_flow(self, stock_data: list):
        """学习资金流向模式"""
        return {}

    def get_patterns(self):
        """获取当前学习到的规律"""
        return self.patterns


class StockPredictor:
    """个股预测引擎"""

    def __init__(self, learner: MarketLearner):
        self.learner = learner
        self.patterns = learner.get_patterns()

    def predict(self, stock_info: dict) -> dict:
        """
        预测个股走势

        stock_info = {
            "symbol": "300760",
            "name": "迈瑞医疗",
            "price": 169.60,
            "technical": {...},   # 技术面数据
            "fundamental": {...}, # 基本面数据
            "sentiment": {...},   # 情绪面数据
            "intelligence": {...} # 情报面数据
        }

        返回:
        {
            "score": 75,           # 综合得分 0-100
            "direction": "up",     # 方向预测
            "probability": 0.65,   # 上涨概率
            "expected_return": 0.05, # 预期收益
            "risk_level": "中",    # 风险等级
            "action": "观望",      # 操作建议
            "reasons": [...]       # 理由
        }
        """
        # 计算各维度得分
        tech_score = self._calc_technical_score(stock_info.get("technical", {}))
        fund_score = self._calc_fundamental_score(stock_info.get("fundamental", {}))
        sent_score = self._calc_sentiment_score(stock_info.get("sentiment", {}))
        intel_score = self._calc_intelligence_score(stock_info.get("intelligence", {}))

        # 加权综合得分
        weights = self.patterns.get("factor_weights", {
            "technical": 0.25,
            "fundamental": 0.30,
            "sentiment": 0.15,
            "intelligence": 0.30
        })

        total_score = (
            tech_score * weights["technical"] +
            fund_score * weights["fundamental"] +
            sent_score * weights["sentiment"] +
            intel_score * weights["intelligence"]
        )

        # 预测方向和概率
        if total_score >= 70:
            direction = "up"
            probability = 0.65 + (total_score - 70) * 0.01
            action = "买入"
        elif total_score >= 50:
            direction = "neutral"
            probability = 0.50
            action = "观望"
        else:
            direction = "down"
            probability = 0.35 - (50 - total_score) * 0.005
            action = "卖出/不买"

        # 预期收益
        expected_return = (total_score - 50) / 100

        # 风险等级
        if total_score >= 70:
            risk_level = "低"
        elif total_score >= 50:
            risk_level = "中"
        else:
            risk_level = "高"

        # 生成理由
        reasons = []
        if tech_score >= 70:
            reasons.append("✅ 技术面强势")
        elif tech_score < 40:
            reasons.append("❌ 技术面走弱")

        if fund_score >= 70:
            reasons.append("✅ 基本面优秀")
        elif fund_score < 40:
            reasons.append("❌ 基本面堪忧")

        if intel_score >= 70:
            reasons.append("✅ 情报面利好")
        elif intel_score < 40:
            reasons.append("❌ 情报面利空")

        return {
            "symbol": stock_info.get("symbol"),
            "name": stock_info.get("name"),
            "score": round(total_score, 1),
            "scores": {
                "technical": tech_score,
                "fundamental": fund_score,
                "sentiment": sent_score,
                "intelligence": intel_score
            },
            "direction": direction,
            "probability": min(max(probability, 0), 1),
            "expected_return": expected_return,
            "risk_level": risk_level,
            "action": action,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat()
        }

    def _calc_technical_score(self, tech: dict) -> float:
        """计算技术面得分"""
        score = 50  # 基础分

        # 趋势
        if tech.get("trend") == "up":
            score += 15
        elif tech.get("trend") == "down":
            score -= 15

        # RSI
        rsi = tech.get("rsi", 50)
        if rsi < 30:
            score += 10  # 超卖，可能反弹
        elif rsi > 70:
            score -= 10  # 超买，可能回调

        # 成交量
        if tech.get("volume_trend") == "increasing":
            score += 10
        elif tech.get("volume_trend") == "decreasing":
            score -= 5

        # 均线
        if tech.get("above_ma20"):
            score += 10
        if tech.get("above_ma60"):
            score += 5

        return max(0, min(100, score))

    def _calc_fundamental_score(self, fund: dict) -> float:
        """计算基本面得分"""
        score = 50

        # PE
        pe = fund.get("pe", 0)
        if 0 < pe < 20:
            score += 15
        elif 20 <= pe < 30:
            score += 5
        elif pe >= 50:
            score -= 10

        # 业绩增长
        growth = fund.get("revenue_growth", 0)
        if growth > 30:
            score += 15
        elif growth > 10:
            score += 10
        elif growth < 0:
            score -= 10

        # 行业地位
        if fund.get("is_leader"):
            score += 10

        return max(0, min(100, score))

    def _calc_sentiment_score(self, sent: dict) -> float:
        """计算情绪面得分"""
        score = 50

        # 主力资金
        if sent.get("main_inflow"):
            score += 15
        if sent.get("retail_inflow"):
            score += 5

        # 舆情
        if sent.get("sentiment") == "positive":
            score += 10
        elif sent.get("sentiment") == "negative":
            score -= 10

        return max(0, min(100, score))

    def _calc_intelligence_score(self, intel: dict) -> float:
        """计算情报面得分"""
        score = 50

        # 政策利好
        if intel.get("policy_positive"):
            score += 20

        # 行业利好
        if intel.get("sector_positive"):
            score += 15

        # 重大事件
        event = intel.get("major_event")
        if event == "war_ongoing":
            # 战争期间，防御板块加分
            score += 10
        elif event == "war_ended":
            # 战争结束，风险资产加分
            score += 15
        elif event == "rate_cut":
            score += 20
        elif event == "rate_hike":
            score -= 10

        # 风险事件
        if intel.get("risk_event"):
            score -= 15

        return max(0, min(100, score))


class ProactiveAdvisor:
    """主动推荐引擎"""

    def __init__(self, predictor: StockPredictor):
        self.predictor = predictor
        self.recommendations = []

    def scan_opportunities(self, stock_list: list) -> list:
        """
        扫描全市场机会

        返回TOP N买入候选
        """
        results = []

        for stock in stock_list:
            prediction = self.predictor.predict(stock)
            if prediction["score"] >= 70:
                results.append(prediction)

        # 按得分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:10]  # 返回TOP 10

    def scan_risks(self, holdings: list) -> list:
        """
        扫描持仓风险

        返回需要减仓/止损的股票
        """
        risks = []

        for stock in holdings:
            prediction = self.predictor.predict(stock)
            if prediction["score"] < 40 or prediction["direction"] == "down":
                risks.append(prediction)

        return risks

    def generate_daily_report(self, holdings: list, opportunities: list) -> str:
        """生成每日报告"""
        report = []
        report.append("=" * 50)
        report.append("📊 每日投资建议报告")
        report.append("=" * 50)
        report.append(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")

        # 持仓风险
        risks = self.scan_risks(holdings)
        if risks:
            report.append("🔴 卖出/减仓预警:")
            for r in risks:
                report.append(f"  • {r['name']}({r['symbol']}): 得分{r['score']}, {r['action']}")
                report.append(f"    理由: {', '.join(r['reasons'])}")
        else:
            report.append("✅ 持仓安全，暂无卖出信号")
        report.append("")

        # 买入机会
        if opportunities:
            report.append("🟢 买入候选:")
            for i, opp in enumerate(opportunities[:5], 1):
                report.append(f"  {i}. {opp['name']}({opp['symbol']}): 得分{opp['score']}")
                report.append(f"     预测: {opp['direction']} (概率{opp['probability']:.0%})")
                report.append(f"     理由: {', '.join(opp['reasons'])}")
        report.append("")

        report.append("=" * 50)
        return "\n".join(report)


# 主系统
class EvolutionSystemV2:
    """预测型进化系统 v2.0"""

    def __init__(self, data_dir: str = None):
        self.learner = MarketLearner(data_dir)
        self.predictor = StockPredictor(self.learner)
        self.advisor = ProactiveAdvisor(self.predictor)

        print("✅ 预测型进化系统 v2.0 已初始化")

    def learn(self, stock_data: list):
        """从市场数据学习"""
        return self.learner.learn_from_market(stock_data)

    def predict(self, stock_info: dict) -> dict:
        """预测单只股票"""
        return self.predictor.predict(stock_info)

    def scan(self, stock_list: list) -> list:
        """扫描全市场机会"""
        return self.advisor.scan_opportunities(stock_list)

    def check_risks(self, holdings: list) -> list:
        """检查持仓风险"""
        return self.advisor.scan_risks(holdings)

    def daily_report(self, holdings: list, opportunities: list) -> str:
        """生成每日报告"""
        return self.advisor.generate_daily_report(holdings, opportunities)


# 测试
if __name__ == "__main__":
    system = EvolutionSystemV2()

    # 测试预测迈瑞医疗
    mindray = {
        "symbol": "300760",
        "name": "迈瑞医疗",
        "price": 169.60,
        "technical": {
            "trend": "down",
            "rsi": 45,
            "volume_trend": "decreasing",
            "above_ma20": False,
            "above_ma60": False
        },
        "fundamental": {
            "pe": 23,
            "revenue_growth": 8,
            "is_leader": True
        },
        "sentiment": {
            "main_inflow": False,
            "retail_inflow": True,
            "sentiment": "neutral"
        },
        "intelligence": {
            "policy_positive": False,
            "sector_positive": False,
            "major_event": "war_ongoing"
        }
    }

    result = system.predict(mindray)
    print("\n📊 迈瑞医疗预测结果:")
    print(f"  综合得分: {result['score']}")
    print(f"  预测方向: {result['direction']}")
    print(f"  上涨概率: {result['probability']:.0%}")
    print(f"  风险等级: {result['risk_level']}")
    print(f"  操作建议: {result['action']}")
    print(f"  理由: {', '.join(result['reasons'])}")
