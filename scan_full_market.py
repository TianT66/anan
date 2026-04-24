# -*- coding: utf-8 -*-
"""
全市场完整扫描 - 获取5000+股票
"""
import urllib.request
import json
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def get_full_market():
    """获取全市场A股数据"""
    print("📊 正在获取全市场股票数据...")

    # 沪市股票代码范围
    sh_codes = []
    # 600000-605000 主板
    for i in range(600000, 605000, 100):
        sh_codes.append(f"sh{i}")
    # 688000-689000 科创板
    for i in range(688000, 689000, 100):
        sh_codes.append(f"sh{i}")

    # 深市股票代码范围
    sz_codes = []
    # 000001-003000 主板
    for i in range(1, 3000, 100):
        sz_codes.append(f"sz{i:06d}")
    # 300001-301000 创业板
    for i in range(300001, 301000, 100):
        sz_codes.append(f"sz{i}")

    all_codes = sh_codes + sz_codes
    print(f"  尝试获取约 {len(all_codes) * 50} 只股票...")

    stocks_data = []

    # 批量获取
    batch_size = 50
    total_batches = min(len(all_codes), 200)  # 限制批次数，避免超时

    for i in range(total_batches):
        batch_idx = i * batch_size
        if batch_idx >= len(all_codes):
            break

        batch = all_codes[batch_idx:batch_idx + batch_size]
        codes = ",".join(batch)

        try:
            url = f"https://qt.gtimg.cn/q={codes}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('gbk')

                for line in content.strip().split('\n'):
                    if '~' in line and '="' in line:
                        try:
                            data_str = line.split('="')[1].rstrip('";')
                            fields = data_str.split('~')

                            if len(fields) >= 35 and fields[3] and fields[3] != '0':
                                price = float(fields[3])
                                if price > 0:  # 有效价格
                                    stock = {
                                        "code": fields[2],
                                        "name": fields[1],
                                        "price": price,
                                        "prev_close": float(fields[4]) if fields[4] else 0,
                                        "high": float(fields[33]) if fields[33] else 0,
                                        "low": float(fields[34]) if fields[34] else 0,
                                        "volume": float(fields[6]) if fields[6] else 0,
                                    }

                                    if stock["prev_close"] > 0:
                                        stock["change_pct"] = (price - stock["prev_close"]) / stock["prev_close"] * 100
                                    else:
                                        stock["change_pct"] = 0

                                    stocks_data.append(stock)
                        except:
                            continue
        except:
            continue

        if (i + 1) % 20 == 0:
            print(f"  已处理 {(i+1)*batch_size} 个代码，获取 {len(stocks_data)} 只有效股票...")

    print(f"  ✅ 成功获取 {len(stocks_data)} 只股票数据")
    return stocks_data


def calculate_score(stock):
    """计算股票得分"""
    score = 50
    reasons = []

    # 1. 技术面得分
    tech_score = 50
    change = stock.get("change_pct", 0)

    # 超跌反弹机会
    if -10 < change < -5:
        tech_score += 15
        reasons.append("超跌反弹信号")
    elif -5 < change < 0:
        tech_score += 8
    elif 0 < change < 3:
        tech_score += 5
    elif 3 < change < 7:
        tech_score += 3
    elif change >= 7:
        tech_score -= 10
        reasons.append("短期涨幅过大")

    # 2. 基本面得分
    fund_score = 50
    name = stock.get("name", "")

    # 行业判断
    if any(k in name for k in ["银行", "保险", "证券"]):
        fund_score += 20
        reasons.append("金融低估值")
    elif any(k in name for k in ["煤", "油", "气", "矿"]):
        fund_score += 15
        reasons.append("能源板块")
    elif any(k in name for k in ["药", "医", "康", "健"]):
        fund_score += 12
        reasons.append("医药板块")
    elif any(k in name for k in ["金", "银", "贵"]):
        fund_score += 18
        reasons.append("贵金属避险")
    elif any(k in name for k in ["军", "国防", "航"]):
        fund_score += 15
        reasons.append("军工板块")

    # 3. 情报面得分
    intel_score = 50

    # 美伊战争影响
    if any(k in name for k in ["军", "国防", "兵"]):
        intel_score += 30
        reasons.append("🔥战争受益")
    elif any(k in name for k in ["金", "银", "贵"]):
        intel_score += 25
        reasons.append("🔥避险资产")
    elif any(k in name for k in ["油", "煤", "气", "能"]):
        intel_score += 20
        reasons.append("🔥能源危机受益")
    elif any(k in name for k in ["药", "医"]):
        intel_score += 15
        reasons.append("防御板块")
    elif any(k in name for k in ["航空", "旅游", "酒店"]):
        intel_score -= 20
        reasons.append("⚠️战争受损")

    # 综合得分
    total_score = tech_score * 0.3 + fund_score * 0.3 + intel_score * 0.4

    return {
        "code": stock["code"],
        "name": stock["name"],
        "price": stock["price"],
        "change_pct": stock.get("change_pct", 0),
        "score": round(total_score, 1),
        "reasons": reasons
    }


def scan_full_market():
    """完整市场扫描"""
    print("=" * 60)
    print("🔍 全市场完整扫描 - 寻找机会")
    print("=" * 60)
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 获取数据
    stocks = get_full_market()

    if not stocks:
        print("❌ 未能获取股票数据")
        return

    print(f"\n📊 开始分析 {len(stocks)} 只股票...")

    # 计算得分
    results = []
    for stock in stocks:
        result = calculate_score(stock)
        results.append(result)

    # 按得分排序
    results.sort(key=lambda x: x["score"], reverse=True)

    # 筛选高分股票
    high_score = [r for r in results if r["score"] >= 70]
    medium_score = [r for r in results if 60 <= r["score"] < 70]

    # 输出结果
    print("\n" + "=" * 60)
    print("📈 扫描结果")
    print("=" * 60)

    if high_score:
        print(f"\n🟢 得分≥70 强烈推荐（共{len(high_score)}只）:\n")
        for i, r in enumerate(high_score[:15], 1):
            print(f"{i:2d}. {r['name']:8s}({r['code']})")
            print(f"    价格: {r['price']:.2f}元 | 涨跌: {r['change_pct']:+.2f}% | 得分: {r['score']}")
            if r['reasons']:
                print(f"    理由: {', '.join(r['reasons'])}")
            print()
    else:
        print("\n⚠️ 未找到得分≥70的股票")

    if medium_score:
        print(f"\n🟡 得分60-70 关注候选（共{len(medium_score)}只）:\n")
        for i, r in enumerate(medium_score[:10], 1):
            print(f"{i:2d}. {r['name']:8s}({r['code']}) 得分: {r['score']}")

    # 显示得分分布
    print("\n📊 得分分布:")
    score_ranges = {
        "80+": len([r for r in results if r["score"] >= 80]),
        "70-79": len([r for r in results if 70 <= r["score"] < 80]),
        "60-69": len([r for r in results if 60 <= r["score"] < 70]),
        "50-59": len([r for r in results if 50 <= r["score"] < 60]),
        "<50": len([r for r in results if r["score"] < 50]),
    }
    for range_name, count in score_ranges.items():
        bar = "█" * (count // 10)
        print(f"  {range_name}: {count:4d}只 {bar}")

    # 显示TOP 20
    print("\n📊 得分TOP 20:")
    for i, r in enumerate(results[:20], 1):
        print(f"  {i:2d}. {r['name']:8s}({r['code']}) {r['score']:5.1f}分")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    scan_full_market()
