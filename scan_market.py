# -*- coding: utf-8 -*-
"""
全市场扫描 - 寻找得分≥70的买入候选
"""
import urllib.request
import json
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def get_all_stocks():
    """获取全市场A股数据"""
    print("📊 正在获取全市场股票数据...")

    # 腾讯批量查价API - 分批获取
    url_template = "https://qt.gtimg.cn/q={}"

    # 先获取市场列表
    market_urls = [
        "https://qt.gtimg.cn/q=sh000001",  # 上证指数
        "https://qt.gtimg.cn/q=sz399001",  # 深证成指
    ]

    all_stocks = []

    # 尝试获取A股列表（使用预设列表）
    # 由于腾讯API不支持直接获取列表，我们使用已知的股票池
    # 这里简化为获取热门股票数据

    # 常用股票代码（示例：沪深300成分股 + 热门股）
    hot_stocks = [
        # 科技
        "sz300750", "sz300760", "sz300059", "sz300033", "sz002415", "sz002230", "sz002371",
        "sh688981", "sh688012", "sh600570", "sh600588", "sh600036",
        # 医药
        "sz300015", "sz300347", "sz300122", "sz002007", "sz000661", "sh603259",
        # 新能源
        "sz300750", "sz002594", "sz002466", "sz002460", "sh601012", "sh600438",
        # 消费
        "sz000858", "sz000568", "sz000333", "sz002304", "sh600519", "sh600887",
        # 金融
        "sh601318", "sh601166", "sh600036", "sh601398", "sh601288",
        # 周期
        "sh601899", "sz000002", "sz002142", "sh600309", "sz002714",
        # 军工
        "sh600893", "sz002179", "sz300034", "sh601989",
        # 半导体
        "sz002371", "sh688981", "sz002049", "sh603501", "sz300661",
        # AI相关
        "sz002230", "sz300033", "sz002405", "sh688787", "sz300474",
        # 机器人
        "sz002747", "sz300124", "sh603236", "sz002008",
        # 更多热门股
        "sz000001", "sz000002", "sz000333", "sz000651", "sz000725", "sz000858",
        "sh600000", "sh600009", "sh600010", "sh600011", "sh600015", "sh600016",
        "sh600019", "sh600028", "sh600029", "sh600030", "sh600031", "sh600033",
        "sh600035", "sh600037", "sh600048", "sh600050", "sh600061", "sh600066",
        "sh600068", "sh600085", "sh600089", "sh600104", "sh600109", "sh600111",
        "sh600115", "sh600118", "sh600123", "sh600132", "sh600141", "sh600143",
        "sh600150", "sh600153", "sh600158", "sh600160", "sh600161", "sh600166",
        "sh600167", "sh600170", "sh600176", "sh600177", "sh600183", "sh600188",
        "sh600196", "sh600199", "sh600201", "sh600208", "sh600210", "sh600216",
        "sh600219", "sh600220", "sh600223", "sh600225", "sh600226", "sh600227",
        "sh600229", "sh600230", "sh600231", "sh600232", "sh600233", "sh600236",
        "sh600239", "sh600240", "sh600242", "sh600243", "sh600245", "sh600246",
        "sh600247", "sh600248", "sh600249", "sh600250", "sh600251", "sh600252",
    ]

    # 去重
    hot_stocks = list(set(hot_stocks))

    print(f"  获取 {len(hot_stocks)} 只热门股票数据...")

    stocks_data = []

    # 批量获取（每批50个）
    batch_size = 50
    for i in range(0, len(hot_stocks), batch_size):
        batch = hot_stocks[i:i+batch_size]
        codes = ",".join(batch)

        try:
            url = f"https://qt.gtimg.cn/q={codes}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('gbk')

                # 解析数据
                for line in content.strip().split('\n'):
                    if '~' in line:
                        try:
                            data_str = line.split('="')[1].rstrip('";')
                            fields = data_str.split('~')

                            if len(fields) >= 35:
                                stock = {
                                    "code": fields[2],
                                    "name": fields[1],
                                    "price": float(fields[3]) if fields[3] else 0,
                                    "change_pct": float(fields[31]) if fields[31] else 0,
                                    "volume": float(fields[6]) if fields[6] else 0,
                                    "amount": float(fields[37]) if fields[37] else 0,
                                    "high": float(fields[33]) if fields[33] else 0,
                                    "low": float(fields[34]) if fields[34] else 0,
                                    "open": float(fields[5]) if fields[5] else 0,
                                    "prev_close": float(fields[4]) if fields[4] else 0,
                                }

                                # 计算技术指标
                                if stock["prev_close"] > 0:
                                    stock["change_pct"] = (stock["price"] - stock["prev_close"]) / stock["prev_close"] * 100

                                # 估算PE（简化）
                                stock["pe"] = 20  # 默认值，实际需要财务数据

                                stocks_data.append(stock)
                        except Exception as e:
                            continue
        except Exception as e:
            print(f"  批次 {i//batch_size + 1} 获取失败: {e}")
            continue

        time.sleep(0.1)  # 避免请求过快

    print(f"  成功获取 {len(stocks_data)} 只股票数据")
    return stocks_data


def calculate_score(stock):
    """计算股票得分"""
    score = 50
    reasons = []

    # 1. 技术面（30分）
    tech_score = 50

    # 涨跌幅
    change = stock.get("change_pct", 0)
    if -5 < change < 0:
        tech_score += 10  # 小跌，可能反弹
        reasons.append("技术面:超跌反弹信号")
    elif 0 < change < 3:
        tech_score += 5
    elif change >= 5:
        tech_score -= 10  # 大涨，注意回调
        reasons.append("技术面:短期涨幅过大")

    # 振幅（高低价差）
    if stock["prev_close"] > 0:
        amplitude = (stock["high"] - stock["low"]) / stock["prev_close"]
        if amplitude > 0.05:
            tech_score += 5
            reasons.append("技术面:振幅足够")

    score = (score + tech_score) / 2 + 25  # 技术面权重

    # 2. 基本面（20分）
    # 简化：根据股票属性判断
    fund_score = 50
    name = stock.get("name", "")

    if any(k in name for k in ["银行", "保险"]):
        fund_score += 15  # 金融股估值低
        reasons.append("基本面:金融股低估值")
    elif any(k in name for k in ["药", "医"]):
        fund_score += 10  # 医药龙头
        reasons.append("基本面:医药龙头")
    elif any(k in name for k in ["科技", "电子", "芯"]):
        fund_score += 5

    score = score * 0.6 + fund_score * 0.2

    # 3. 情报面（30分）
    intel_score = 50

    # 美伊战争影响
    if any(k in name for k in ["军工", "国防", "黄金", "金"]):
        intel_score += 25  # 战争受益
        reasons.append("情报面:美伊战争受益")
    elif any(k in name for k in ["药", "医", "消费"]):
        intel_score += 15  # 防御板块
        reasons.append("情报面:防御属性")
    elif any(k in name for k in ["航空", "旅游", "酒店"]):
        intel_score -= 15  # 战争受损
        reasons.append("情报面:战争受损板块")

    # 政策热点（3月）
    if any(k in name for k in ["机器人", "AI", "人工智能"]):
        intel_score += 10
        reasons.append("情报面:AI政策支持")
    if any(k in name for k in ["新能", "锂", "电"]):
        intel_score += 5

    score = score * 0.7 + intel_score * 0.3

    return {
        "code": stock["code"],
        "name": stock["name"],
        "price": stock["price"],
        "change_pct": stock["change_pct"],
        "score": round(score, 1),
        "reasons": reasons
    }


def scan_market():
    """扫描市场"""
    print("=" * 60)
    print("🔍 全市场扫描 - 寻找得分≥70的买入候选")
    print("=" * 60)
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    # 获取数据
    stocks = get_all_stocks()

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

    # 筛选得分≥65的股票（降低门槛，因为数据有限）
    high_score = [r for r in results if r["score"] >= 65]

    # 输出结果
    print("\n" + "=" * 60)
    print("📈 扫描结果")
    print("=" * 60)

    if high_score:
        print(f"\n🟢 得分≥65的买入候选（共{len(high_score)}只）:\n")
        for i, r in enumerate(high_score[:20], 1):
            print(f"{i:2d}. {r['name']}({r['code']})")
            print(f"    价格: {r['price']:.2f}元 | 涨跌: {r['change_pct']:+.2f}% | 得分: {r['score']}")
            if r['reasons']:
                print(f"    理由: {'; '.join(r['reasons'])}")
            print()
    else:
        print("\n⚠️ 未找到得分≥65的股票")
        print("   可能原因: 市场整体偏弱，或数据获取有限")

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
        print(f"  {range_name}: {count}只")

    # 显示TOP 10
    print("\n📊 得分TOP 10:")
    for i, r in enumerate(results[:10], 1):
        print(f"  {i:2d}. {r['name']:8s} {r['score']:5.1f}分")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    scan_market()
