# -*- coding: utf-8 -*-
"""
全市场深度筛选 v2 - 左侧布局专版
重点：从高点回撤幅度 + 行业属性 + 基本面
日期：2026-03-28（周六，数据为3月27日收盘）
"""
import urllib.request
import json
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def get_realtime_price(stocks):
    """从腾讯API获取实时价格"""
    if not stocks:
        return {}

    results = {}
    batch_size = 50

    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        full_codes = []
        for s in batch:
            prefix = "sh" if s["market"] == "SH" else "sz"
            full_codes.append(prefix + s["code"])

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
                                full_code = fields[2]
                                code = full_code[2:] if full_code.startswith(('sz', 'sh')) else full_code
                                price = float(fields[3]) if fields[3] and fields[3] != '0' else 0
                                prev_close = float(fields[4]) if fields[4] else 0
                                high = float(fields[33]) if fields[33] else 0
                                low = float(fields[34]) if fields[34] else 0
                                volume = float(fields[6]) if fields[6] else 0

                                if price > 0:
                                    change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                                    results[code] = {
                                        "code": code,
                                        "name": fields[1],
                                        "price": price,
                                        "prev_close": prev_close,
                                        "change_pct": change_pct,
                                        "high": high,
                                        "low": low,
                                        "volume": volume,
                                    }
                        except:
                            continue
        except:
            pass

        time.sleep(0.1)

    return results


def get_stock_list():
    """获取股票列表"""
    try:
        import akshare as ak
        stocks = []

        df_sh = ak.stock_info_a_code_name()
        if df_sh is not None and not df_sh.empty:
            for _, row in df_sh.iterrows():
                code = str(row.get('code', ''))
                if code.startswith('6'):
                    stocks.append({"code": code, "name": str(row.get('name', '')), "market": "SH"})

        df_sz = ak.stock_info_a_code_name()
        if df_sz is not None and not df_sz.empty:
            for _, row in df_sz.iterrows():
                code = str(row.get('code', ''))
                if code.startswith('0') or code.startswith('3'):
                    stocks.append({"code": code, "name": str(row.get('name', '')), "market": "SZ"})

        return stocks
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return []


def analyze_stock(stock, price_data):
    """深度分析"""
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
    prev_close = data["prev_close"]
    volume = data.get("volume", 0)

    # ========================
    # 1. 从高点回撤分析 (40%)
    # ========================
    drop_score = 50
    drop_reasons = []

    if high > 0 and price > 0:
        drop_pct = (high - price) / high * 100

        if drop_pct > 50:
            drop_score = 95
            drop_reasons.append(f"从高点暴跌{drop_pct:.0f}%")
        elif drop_pct > 40:
            drop_score = 85
            drop_reasons.append(f"从高点重挫{drop_pct:.0f}%")
        elif drop_pct > 30:
            drop_score = 75
            drop_reasons.append(f"从高点大跌{drop_pct:.0f}%")
        elif drop_pct > 20:
            drop_score = 65
            drop_reasons.append(f"从高点回调{drop_pct:.0f}%")
        elif drop_pct > 15:
            drop_score = 60
            drop_reasons.append(f"从高点回撤{drop_pct:.0f}%")
        elif drop_pct > 10:
            drop_score = 55
            drop_reasons.append(f"从高点小幅回调{drop_pct:.0f}%")
        elif drop_pct > 5:
            drop_score = 52

    # ========================
    # 2. 行业属性分析 (30%)
    # ========================
    sector_score = 50
    sector_reasons = []

    # 低估值防御板块
    if any(k in name for k in ["银行", "保险", "证券"]):
        sector_score = 80
        sector_reasons.append("金融低估值")

    # 医药防御
    elif any(k in name for k in ["药", "医", "康", "健"]):
        sector_score = 75
        sector_reasons.append("医药防御")

    # 消费稳定
    elif any(k in name for k in ["食品", "饮料", "白酒", "乳"]):
        sector_score = 70
        sector_reasons.append("消费稳定")

    # 黄金避险（但要考虑美伊战争影响）
    elif any(k in name for k in ["金", "银"]):
        sector_score = 60  # 下调，因为黄金已跌15%
        sector_reasons.append("贵金属（注意战争影响）")

    # 能源（受益战争）
    elif any(k in name for k in ["油", "能", "气"]):
        sector_score = 70
        sector_reasons.append("能源受益")

    # 军工（受益战争，但已涨）
    elif any(k in name for k in ["军", "航", "防"]):
        sector_score = 65
        sector_reasons.append("军工（注意停火风险）")

    # 科技成长
    elif any(k in name for k in ["科技", "电子", "芯", "AI", "软件"]):
        sector_score = 60
        sector_reasons.append("科技成长")

    # 机器人/自动化
    elif any(k in name for k in ["机器人", "自动", "智能"]):
        sector_score = 65
        sector_reasons.append("机器人产业")

    # 战争受损
    elif any(k in name for k in ["航空", "旅游", "酒店"]):
        sector_score = 35
        sector_reasons.append("战争受损")

    # ========================
    # 3. 今日表现分析 (15%)
    # ========================
    today_score = 50
    today_reasons = []

    if change_pct < -7:
        today_score = 70
        today_reasons.append(f"今日大跌{change_pct:.1f}%")
    elif change_pct < -5:
        today_score = 65
        today_reasons.append(f"今日下跌{change_pct:.1f}%")
    elif change_pct < -3:
        today_score = 60
        today_reasons.append(f"今日小跌{change_pct:.1f}%")
    elif -1 < change_pct < 2:
        today_score = 55
        today_reasons.append("今日震荡")
    elif change_pct > 7:
        today_score = 40
        today_reasons.append("注意追高风险")

    # ========================
    # 4. 成交量分析 (15%)
    # ========================
    vol_score = 50
    vol_reasons = []

    if volume > 0:
        vol_ratio = volume / 10000  # 万手
        if vol_ratio > 50:
            vol_score = 60
            vol_reasons.append("成交量放大")
        elif vol_ratio > 20:
            vol_score = 55
            vol_reasons.append("量能温和")

    # ========================
    # 综合评分
    # ========================
    total_score = drop_score * 0.40 + sector_score * 0.30 + today_score * 0.15 + vol_score * 0.15

    all_reasons = drop_reasons + sector_reasons + today_reasons + vol_reasons
    all_reasons = list(dict.fromkeys(all_reasons))[:5]

    return {
        "code": code,
        "name": name,
        "market": market,
        "price": price,
        "change_pct": change_pct,
        "high": high,
        "drop_pct": (high - price) / high * 100 if high > 0 and price > 0 else 0,
        "score": round(total_score, 1),
        "reasons": all_reasons
    }


def scan_market():
    """全市场扫描"""
    print("=" * 70)
    print("🔍 全市场深度筛选 v2 - 左侧布局专版")
    print("=" * 70)
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("📅 数据: 2026-03-27(周五) 收盘数据")
    print()

    # 获取股票列表
    print("📊 获取股票列表...")
    stocks = get_stock_list()
    print(f"   总计: {len(stocks)} 只")
    print()

    # 获取实时价格
    print("📊 获取实时行情（分批）...")
    batch_size = 500
    all_price_data = {}

    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        print(f"   正在获取 {i+1}-{min(i+batch_size, len(stocks))}...")
        price_data = get_realtime_price(batch)
        all_price_data.update(price_data)
        time.sleep(0.5)

    print(f"   成功获取: {len(all_price_data)} 只")
    print()

    # 分析
    print("📊 深度分析...")
    results = []

    for stock in stocks:
        if stock["code"] in all_price_data:
            analysis = analyze_stock(stock, all_price_data)
            if analysis and analysis["score"] >= 65:
                results.append(analysis)

    results.sort(key=lambda x: x["score"], reverse=True)

    # ========================
    # 输出结果
    # ========================
    print()
    print("=" * 70)
    print("📈 筛选结果")
    print("=" * 70)

    # 得分分布
    print(f"\n📊 得分分布 (样本{len(results)}只，得分≥65):")
    ranges = {"80+": 0, "70-79": 0, "65-69": 0}
    for r in results:
        if r["score"] >= 80:
            ranges["80+"] += 1
        elif r["score"] >= 70:
            ranges["70-79"] += 1
        else:
            ranges["65-69"] += 1

    for k, v in ranges.items():
        print(f"   {k}: {v} 只")

    # TOP 20
    print(f"\n🏆 TOP 20 推荐:")
    print("-" * 70)
    for i, r in enumerate(results[:20], 1):
        drop_pct = r["drop_pct"]
        print(f"\n{i:2d}. {r['name']:10s}({r['market']}{r['code']})")
        print(f"    价格: ¥{r['price']:.2f} | 今日: {r['change_pct']:+.2f}% | 从高点回撤: {drop_pct:.1f}%")
        print(f"    得分: {r['score']} | 理由: {', '.join(r['reasons'][:3])}")

    # 按行业分类
    print("\n" + "=" * 70)
    print("📋 按行业分类推荐")
    print("=" * 70)

    categories = {
        "银行/金融": [],
        "医药/医疗": [],
        "消费/食品": [],
        "能源/化工": [],
        "军工/航天": [],
        "科技/AI": [],
        "其他优质": []
    }

    for r in results[:50]:
        name = r["name"]
        if any(k in name for k in ["银行", "保险", "证券"]):
            categories["银行/金融"].append(r)
        elif any(k in name for k in ["药", "医", "康"]):
            categories["医药/医疗"].append(r)
        elif any(k in name for k in ["食品", "饮料", "白酒"]):
            categories["消费/食品"].append(r)
        elif any(k in name for k in ["油", "能", "气", "化"]):
            categories["能源/化工"].append(r)
        elif any(k in name for k in ["军", "航", "防"]):
            categories["军工/航天"].append(r)
        elif any(k in name for k in ["科技", "电子", "AI", "芯"]):
            categories["科技/AI"].append(r)
        else:
            categories["其他优质"].append(r)

    for cat, stocks_list in categories.items():
        if stocks_list:
            print(f"\n【{cat}】")
            for r in stocks_list[:3]:
                print(f"  • {r['name']}({r['code']}) {r['score']}分 ¥{r['price']:.2f} 从高点{r['drop_pct']:.0f}%")

    print()
    print("=" * 70)


if __name__ == "__main__":
    scan_market()
