# -*- coding: utf-8 -*-
"""测试分析函数"""

def analyze_stock(stock, price_data):
    code = stock["code"]
    name = stock["name"]
    market = stock["market"]

    if code not in price_data:
        return None

    data = price_data[code]
    price = data["price"]
    change_pct = data["change_pct"]
    high = data["high"]
    low = data["low"]

    print(f"\n分析 {code} {name}:")
    print(f"  price={price}, change={change_pct:.2f}%")

    # 技术面
    tech_score = 50
    tech_reasons = []

    if change_pct < -5:
        tech_score += 15
        tech_reasons.append("今日大跌超5%")
    elif change_pct < -3:
        tech_score += 10
        tech_reasons.append("今日下跌超3%")
    elif change_pct < 0:
        tech_score += 5
        tech_reasons.append("今日小幅下跌")
    elif change_pct > 7:
        tech_score -= 10
        tech_reasons.append("今日涨幅过大")

    print(f"  tech_score after change: {tech_score}")
    print(f"  reasons: {tech_reasons}")

    # 基本面
    fund_score = 50
    fund_reasons = []

    if any(k in name for k in ["银行"]):
        fund_score += 15
        fund_reasons.append("银行低估值")
    if any(k in name for k in ["药", "医"]):
        fund_score += 10
        fund_reasons.append("医药防御")

    print(f"  fund_score: {fund_score}")

    # 情报面
    intel_score = 50
    intel_reasons = []

    if any(k in name for k in ["金", "银", "矿"]):
        intel_score += 15
        intel_reasons.append("贵金属避险")

    print(f"  intel_score: {intel_score}")

    # 资金面
    flow_score = 50
    if change_pct > 0:
        flow_score += 10
    elif change_pct < -5:
        flow_score += 5

    print(f"  flow_score: {flow_score}")

    # 综合
    total = tech_score * 0.3 + fund_score * 0.3 + intel_score * 0.2 + flow_score * 0.2

    print(f"  TOTAL SCORE: {total:.1f}")

    return {
        "code": code,
        "name": name,
        "price": price,
        "change_pct": change_pct,
        "score": round(total, 1),
        "reasons": tech_reasons + fund_reasons
    }


# 测试数据
stocks = [
    {"code": "000001", "name": "平安银行", "market": "SZ"},
    {"code": "600519", "name": "贵州茅台", "market": "SH"},
    {"code": "300760", "name": "迈瑞医疗", "market": "SZ"},
    {"code": "002371", "name": "北方华创", "market": "SZ"},
]

price_data = {
    "000001": {"code": "000001", "name": "平安银行", "price": 11.02, "change_pct": 0.73, "high": 11.05, "low": 10.83},
    "600519": {"code": "600519", "name": "贵州茅台", "price": 1416.02, "change_pct": 1.06, "high": 1420, "low": 1400},
    "300760": {"code": "300760", "name": "迈瑞医疗", "price": 169.6, "change_pct": 3.23, "high": 170, "low": 162},
    "002371": {"code": "002371", "name": "北方华创", "price": 452.98, "change_pct": 1.54, "high": 458, "low": 434},
}

results = []
for stock in stocks:
    result = analyze_stock(stock, price_data)
    if result:
        results.append(result)

results.sort(key=lambda x: x["score"], reverse=True)

print("\n\n=== 最终排名 ===")
for r in results:
    print(f"{r['name']}: {r['score']}分 ({r['change_pct']:+.2f}%)")
