# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import os
import sys

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')

port = os.environ.get('AUTH_GATEWAY_PORT', '19000')
from_time = int(time.time()) - 86400

data = {
    "keyword": "迈瑞医疗 300760 今日股价 成交量",
    "from_time": from_time
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
        print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")
