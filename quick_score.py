# -*- coding: utf-8 -*-
"""快速检查得分分布"""
import urllib.request
import json
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def get_realtime_price(stocks):
    results = {}
    batch_size = 50
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        full_codes = ["sh" + s["code"] if s["market"] == "SH" else "sz" + s["code"] for s in batch]
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
                                change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                                if price > 0:
                                    results[code] = {
                                        "code": code, "name": fields[1], "price": price,
                                        "prev_close": prev_close, "change_pct": change_pct, "high": high
                                    }
                        except: continue
        except: pass
        time.sleep(0.1)
    return results

def analyze(name, price, change_pct, high):
    drop_pct = (high - price) / high * 100 if high > 0 and price > 0 else 0
    drop_score = 50
    if drop_pct > 50: drop_score = 95
    elif drop_pct > 40: drop_score = 85
    elif drop_pct > 30: drop_score = 75
    elif drop_pct > 20: drop_score = 65
    elif drop_pct > 15: drop_score = 60
    elif drop_pct > 10: drop_score = 55

    sector_score = 50
    if any(k in name for k in ["银行", "保险", "证券"]): sector_score = 80
    elif any(k in name for k in ["药", "医", "康"]): sector_score = 75
    elif any(k in name for k in ["食品", "饮料", "白酒"]): sector_score = 70
    elif any(k in name for k in ["金", "银"]): sector_score = 60
    elif any(k in name for k in ["油", "能"]): sector_score = 70
    elif any(k in name for k in ["军", "航"]): sector_score = 65
    elif any(k in name for k in ["航空", "旅游"]): sector_score = 35

    total = drop_score * 0.40 + sector_score * 0.30 + 50 * 0.30
    return total, drop_pct

# 测试样本
test_stocks = [
    {"code": "000001", "name": "平安银行", "market": "SZ"},
    {"code": "600519", "name": "贵州茅台", "market": "SH"},
    {"code": "300760", "name": "迈瑞医疗", "market": "SZ"},
    {"code": "002371", "name": "北方华创", "market": "SZ"},
    {"code": "601899", "name": "紫金矿业", "market": "SH"},
    {"code": "600309", "name": "万华化学", "market": "SH"},
]

prices = get_realtime_price(test_stocks)
print("\n测试样本得分:")
for code, data in prices.items():
    score, drop = analyze(data["name"], data["price"], data["change_pct"], data["high"])
    print(f"  {data['name']}: price={data['price']:.2f} high={data['high']:.2f} drop={drop:.1f}% score={score:.1f}")

# 统计前500只
import akshare as ak
stocks = []
df_sh = ak.stock_info_a_code_name()
for _, row in df_sh.iterrows():
    code = str(row.get('code', ''))
    if code.startswith('6'):
        stocks.append({"code": code, "name": str(row.get('name', '')), "market": "SH"})
df_sz = ak.stock_info_a_code_name()
for _, row in df_sz.iterrows():
    code = str(row.get('code', ''))
    if code.startswith('0') or code.startswith('3'):
        stocks.append({"code": code, "name": str(row.get('name', '')), "market": "SZ"})

prices = get_realtime_price(stocks[:500])
scores = []
for code, data in prices.items():
    score, drop = analyze(data["name"], data["price"], data["change_pct"], data["high"])
    scores.append({"code": code, "name": data["name"], "price": data["price"], "drop": drop, "score": score})

scores.sort(key=lambda x: x["score"], reverse=True)

print(f"\n\n前500只股票得分分布:")
ranges = {"80+": 0, "70-79": 0, "60-69": 0, "50-59": 0, "<50": 0}
for s in scores:
    if s["score"] >= 80: ranges["80+"] += 1
    elif s["score"] >= 70: ranges["70-79"] += 1
    elif s["score"] >= 60: ranges["60-69"] += 1
    elif s["score"] >= 50: ranges["50-59"] += 1
    else: ranges["<50"] += 1
for k, v in ranges.items():
    print(f"  {k}: {v} 只")

print(f"\nTOP 20:")
for i, s in enumerate(scores[:20], 1):
    print(f"  {i:2d}. {s['name']:10s} {s['score']:5.1f}分 drop={s['drop']:.1f}%")
