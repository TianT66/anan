# -*- coding: utf-8 -*-
import urllib.request
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

# 获取几只股票测试
stocks = [
    {"code": "000001", "name": "平安银行", "market": "SZ"},
    {"code": "600519", "name": "贵州茅台", "market": "SH"},
    {"code": "300760", "name": "迈瑞医疗", "market": "SZ"},
    {"code": "002371", "name": "北方华创", "market": "SZ"},
]

results = {}
batch_size = 50

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

batch = codes_with_prefix
full_codes = [c["full_code"] for c in batch]
codes_str = ",".join(full_codes)

url = f"https://qt.gtimg.cn/q={codes_str}"
print(f"URL: {url}")

req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')

with urllib.request.urlopen(req, timeout=10) as response:
    content = response.read().decode('gbk')
    print(f"Content length: {len(content)}")

    for line in content.strip().split('\n'):
        print(f"Line: {line[:100]}...")
        if '~' in line and '="' in line:
            try:
                data_str = line.split('="')[1].rstrip('";')
                fields = data_str.split('~')
                print(f"Fields count: {len(fields)}")

                if len(fields) >= 35:
                    full_code = fields[2]
                    code = full_code[2:] if full_code.startswith(('sz', 'sh')) else full_code
                    name = fields[1]
                    price = float(fields[3]) if fields[3] and fields[3] != '0' else 0
                    prev_close = float(fields[4]) if fields[4] else 0

                    if prev_close > 0:
                        change_pct = (price - prev_close) / prev_close * 100
                    else:
                        change_pct = 0

                    results[code] = {
                        "code": code,
                        "name": name,
                        "price": price,
                        "change_pct": change_pct,
                    }
                    print(f"OK: {code} {name} price={price} change={change_pct:.2f}%")
            except Exception as e:
                print(f"Error: {e}")
                continue

print(f"\nTotal results: {len(results)}")
for k, v in results.items():
    print(f"  {v['name']}: {v['price']} ({v['change_pct']:+.2f}%)")
