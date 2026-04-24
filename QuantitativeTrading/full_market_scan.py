# -*- coding: utf-8 -*-
"""
全市场深度筛选 - 寻找左侧布局机会
分析框架：技术面(30%) + 基本面(30%) + 情报面(20%) + 资金面(20%)
"""
import urllib.request
import json
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# ========================
# 数据获取
# ========================

def get_realtime_price(stocks):
    """从腾讯API获取实时价格"""
    if not stocks:
        return {}

    results = {}
    batch_size = 50

    # 准备带前缀的代码
    codes_with_prefix = []
    for s in stocks:
        code = s["code"]
        market = s["market"]
        if market == "SH":
            prefix = "sh"
        else:
            prefix = "sz"
        codes_with_prefix.append({
            "code": code,
            "name": s["name"],
            "market": market,
            "full_code": prefix + code
        })

    for i in range(0, len(codes_with_prefix), batch_size):
        batch = codes_with_prefix[i:i+batch_size]
        full_codes = [c["full_code"] for c in batch]
        codes_str = ",".join(full_codes)

        try:
            url = f"https://qt.gtimg.cn/q={codes_str}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('gbk')

                for line in content.strip().split('\n'):
                    if '~' in line and '="' in line:
                        try:
                            data_str = line.split('="')[1].rstrip('";')
                            fields = data_str.split('~')

                            if len(fields) >= 35:
                                full_code = fields[2]  # 如 sz000001
                                # 提取纯数字代码
                                code = full_code[2:] if full_code.startswith(('sz', 'sh')) else full_code
                                price = float(fields[3]) if fields[3] and fields[3] != '0' else 0
                                prev_close = float(fields[4]) if fields[4] else 0

                                if price > 0 and prev_close > 0:
                                    change_pct = (price - prev_close) / prev_close * 100
                                else:
                                    change_pct = 0

                                results[code] = {
                                    "code": code,
                                    "name": fields[1],
                                    "price": price,
                                    "prev_close": prev_close,
                                    "change_pct": change_pct,
                                    "high": float(fields[33]) if fields[33] else 0,
                                    "low": float(fields[34]) if fields[34] else 0,
                                    "open": float(fields[5]) if fields[5] else 0,
                                    "volume": float(fields[6]) if fields[6] else 0,
                                }
                        except:
                            continue
        except Exception as e:
            print(f"  批次 {i//batch_size + 1} 获取失败")

        time.sleep(0.1)

    return results


def get_stock_list():
    """获取股票列表"""
    try:
        import akshare as ak
        stocks = []

        # 沪市
        print("📊 获取沪市股票列表...")
        df_sh = ak.stock_info_a_code_name()
        if df_sh is not None and not df_sh.empty:
            for _, row in df_sh.iterrows():
                code = str(row.get('code', ''))
                if code.startswith('6'):
                    stocks.append({
                        "code": code,
                        "name": str(row.get('name', '')),
                        "market": "SH"
                    })

        # 深市
        print("📊 获取深市股票列表...")
        df_sz = ak.stock_info_a_code_name()
        if df_sz is not None and not df_sz.empty:
            for _, row in df_sz.iterrows():
                code = str(row.get('code', ''))
                if code.startswith('0') or code.startswith('3'):
                    stocks.append({
                        "code": code,
                        "name": str(row.get('name', '')),
                        "market": "SZ"
                    })

        print(f"✅ 共获取 {len(stocks)} 只股票")
        return stocks

    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []


# ========================
# 分析引擎
# ========================

def analyze_stock(stock, price_data, market_data):
    """
    分析单只股票
    返回: {score, direction, reasons}
    """
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

    # ========================
    # 1. 技术面分析 (30%)
    # ========================
    tech_score = 50
    tech_reasons = []

    # 涨跌幅
    if change_pct < -5:
        tech_score += 15
        tech_reasons.append("✅ 今日大跌超5%")
    elif change_pct < -3:
        tech_score += 10
        tech_reasons.append("✅ 今日下跌超3%")
    elif change_pct < 0:
        tech_score += 5
        tech_reasons.append("🟡 今日小幅下跌")
    elif change_pct > 7:
        tech_score -= 10
        tech_reasons.append("⚠️ 今日涨幅过大")

    # 计算从高点的回撤（估算）
    if high > 0 and price > 0:
        drop_pct = (high - price) / high * 100
        if drop_pct > 30:
            tech_score += 15
            tech_reasons.append(f"✅ 从高点回撤{drop_pct:.0f}%")
        elif drop_pct > 20:
            tech_score += 10
            tech_reasons.append(f"🟡 从高点回撤{drop_pct:.0f}%")
        elif drop_pct > 10:
            tech_score += 5

    # 振幅
    if high > 0 and low > 0 and data["prev_close"] > 0:
        amplitude = (high - low) / data["prev_close"] * 100
        if amplitude > 5:
            tech_score += 5
            tech_reasons.append("✅ 振幅充足，可操作")

    tech_weight = 0.30

    # ========================
    # 2. 基本面分析 (30%)
    # ========================
    fund_score = 50
    fund_reasons = []

    # 行业特征
    # 银行 - 低估值
    if any(k in name for k in ["银行"]):
        fund_score += 15
        fund_reasons.append("✅ 银行低估值")

    # 医药 - 防御性
    if any(k in name for k in ["药", "医", "康", "健"]):
        fund_score += 10
        fund_reasons.append("🟡 医药防御板块")

    # 消费 - 稳定
    if any(k in name for k in ["食品", "饮料", "白酒", "乳"]):
        fund_score += 10
        fund_reasons.append("🟡 消费稳定")

    # 黄金/贵金属 - 避险
    if any(k in name for k in ["金", "银", "矿"]):
        fund_score += 15
        fund_reasons.append("🟡 贵金属避险")

    # 军工 - 战争受益
    if any(k in name for k in ["军", "航", "防"]):
        fund_score += 10
        fund_reasons.append("🟡 军工板块")

    # 科技 - 高波动
    if any(k in name for k in ["科技", "电子", "芯", "软"]):
        fund_score += 5

    fund_weight = 0.30

    # ========================
    # 3. 情报面分析 (20%)
    # ========================
    intel_score = 50
    intel_reasons = []

    # 美伊战争影响
    if any(k in name for k in ["金", "银", "贵"]):
        intel_score += 10
        intel_reasons.append("🟡 避险资产")

    if any(k in name for k in ["油", "能", "气"]):
        intel_score += 5
        intel_reasons.append("🟡 能源受益")

    if any(k in name for k in ["药", "医"]):
        intel_score += 10
        intel_reasons.append("🟡 防御板块")

    if any(k in name for k in ["航空", "旅游"]):
        intel_score -= 15
        intel_reasons.append("⚠️ 战争受损")

    # 当前市场背景（3月底）
    # 三月年报季，业绩超预期个股有机会
    # 美伊战争持续，防御板块相对安全

    intel_weight = 0.20

    # ========================
    # 4. 资金面分析 (20%)
    # ========================
    flow_score = 50
    flow_reasons = []

    # 今日资金流向（根据涨跌判断）
    if change_pct > 0:
        flow_score += 10
        flow_reasons.append("🟢 今日资金流入")
    elif change_pct < -5:
        flow_score += 5
        flow_reasons.append("🟡 可能被错杀")
    else:
        flow_score += 0

    flow_weight = 0.20

    # ========================
    # 综合评分
    # ========================
    total_score = (
        tech_score * tech_weight +
        fund_score * fund_weight +
        intel_score * intel_weight +
        flow_score * flow_weight
    )

    # 整合所有理由
    all_reasons = tech_reasons + fund_reasons + intel_reasons + flow_reasons
    all_reasons = list(dict.fromkeys(all_reasons))[:5]  # 去重，保留前5条

    return {
        "code": code,
        "name": name,
        "market": market,
        "price": price,
        "change_pct": change_pct,
        "score": round(total_score, 1),
        "scores": {
            "tech": round(tech_score, 1),
            "fund": round(fund_score, 1),
            "intel": round(intel_score, 1),
            "flow": round(flow_score, 1)
        },
        "reasons": all_reasons
    }


def scan_market():
    """全市场扫描"""
    print("=" * 70)
    print("🔍 全市场深度筛选 - 寻找左侧布局机会")
    print("=" * 70)
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 1. 获取股票列表
    print("📊 第1步：获取股票列表...")
    stocks = get_stock_list()
    if not stocks:
        print("❌ 股票列表获取失败")
        return
    print(f"   股票总数: {len(stocks)}")
    print()

    # 2. 获取实时价格
    print("📊 第2步：获取实时行情...")
    print(f"   正在获取 {len(stocks)} 只股票价格...")

    # 分批获取，先获取前500只测试
    test_stocks = stocks[:500]
    price_data = get_realtime_price(test_stocks)
    print(f"   成功获取 {len(price_data)} 只股票价格")
    print()

    # 3. 大盘环境
    print("📊 第3步：市场环境分析...")
    print("   当前背景:")
    print("   - 市场状态: 熊市（A50空头71%）")
    print("   - 关键事件: 美伊战争第30天")
    print("   - 黄金: 下跌15%（美元升值+实际利率上升）")
    print("   - 策略: 左侧布局，超跌优质标的")
    print()

    # 4. 分析每只股票
    print("📊 第4步：深度分析...")
    results = []

    for stock in stocks[:500]:  # 先分析前500只
        analysis = analyze_stock(stock, price_data, {})
        if analysis and analysis["score"] >= 65:
            results.append(analysis)

    # 按得分排序
    results.sort(key=lambda x: x["score"], reverse=True)

    # 5. 输出结果
    print()
    print("=" * 70)
    print("📈 筛选结果")
    print("=" * 70)

    # 高分候选
    high_score = [r for r in results if r["score"] >= 70]
    if high_score:
        print(f"\n🟢 强烈推荐（得分≥70，共{len(high_score)}只）:\n")
        for i, r in enumerate(high_score[:10], 1):
            print(f"{i}. {r['name']:8s}({r['market']}{r['code']})")
            print(f"   价格: ¥{r['price']:.2f} | 涨跌: {r['change_pct']:+.2f}% | 得分: {r['score']}")
            print(f"   理由: {', '.join(r['reasons'][:3])}")
            print()
    else:
        print("\n⚠️ 未找到得分≥70的股票")

    # 中等候选
    medium_score = [r for r in results if 60 <= r["score"] < 70]
    if medium_score:
        print(f"\n🟡 关注候选（得分60-70，共{len(medium_score)}只）:\n")
        for i, r in enumerate(medium_score[:10], 1):
            print(f"{i}. {r['name']:8s}({r['market']}{r['code']}) 得分: {r['score']}")

    # 得分分布
    print("\n📊 得分分布（分析样本500只）:")
    print(f"   70+: {len([r for r in results if r['score'] >= 70])} 只")
    print(f"   60-70: {len([r for r in results if 60 <= r['score'] < 70])} 只")
    print(f"   50-60: {len([r for r in results if 50 <= r['score'] < 60])} 只")
    print(f"   <50: {len([r for r in results if r['score'] < 50])} 只")

    print()
    print("=" * 70)


if __name__ == "__main__":
    scan_market()
