# -*- coding: utf-8 -*-
"""
搜索实际数据验证
"""
import urllib.request
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

port = os.environ.get('AUTH_GATEWAY_PORT', '19000')

def search_data(keyword):
    """搜索数据"""
    data = {
        "keyword": keyword,
        "from_time": int(time.time()) - 2592000  # 最近30天
    }

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

print("=" * 70)
print("🔍 搜索实际数据验证")
print("=" * 70)
print()

# 搜索1：黄金价格走势
print("【搜索1：黄金价格走势】")
print("-" * 70)
result = search_data("黄金价格 2026年3月 美伊战争 下跌")
print(result[:1000])  # 只显示前1000字
print()
time.sleep(1)

# 搜索2：美元指数
print("【搜索2：美元指数走势】")
print("-" * 70)
result = search_data("美元指数 2026年3月 升值")
print(result[:1000])
print()
time.sleep(1)

# 搜索3：石油价格
print("【搜索3：石油价格走势】")
print("-" * 70)
result = search_data("布伦特原油 2026年3月 价格 美伊战争")
print(result[:1000])
print()
time.sleep(1)

# 搜索4：全球股市
print("【搜索4：全球股市走势】")
print("-" * 70)
result = search_data("标普500 纳斯达克 2026年3月 下跌")
print(result[:1000])
print()
time.sleep(1)

# 搜索5：美债收益率
print("【搜索5：美债收益率】")
print("-" * 70)
result = search_data("美债收益率 10年期 2026年3月")
print(result[:1000])
print()

print("=" * 70)
