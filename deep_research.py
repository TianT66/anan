# -*- coding: utf-8 -*-
"""
深度调研三家公司的详细信息
"""
import urllib.request
import json
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

port = os.environ.get('AUTH_GATEWAY_PORT', '19000')

def search(keyword):
    data = {"keyword": keyword, "from_time": int(time.time()) - 2592000}
    req = urllib.request.Request(
        f"http://localhost:{port}/proxy/prosearch/search",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('message', '')
    except Exception as e:
        return f"搜索失败: {e}"

companies = [
    ("002489", "浙江永强"),
    ("603049", "中策橡胶"),
    ("601628", "中国人寿"),
]

for code, name in companies:
    print("=" * 70)
    print(f"【{name}({code})】深度调研")
    print("=" * 70)

    # 搜索公司概况
    print("\n[1] 公司主营业务搜索...")
    result = search(f"{name} {code} 主营业务 做什么")
    print(result[:2000])

    time.sleep(1)

    # 搜索最新财务
    print("\n[2] 最新财务状况搜索...")
    result = search(f"{name} {code} 2025年报 业绩 财务")
    print(result[:2000])

    time.sleep(1)

    # 搜索近期走势
    print("\n[3] 近期走势分析搜索...")
    result = search(f"{name} {code} 股价 走势 下跌 原因")
    print(result[:2000])

    print()

print("=" * 70)
print("调研完成")
print("=" * 70)
