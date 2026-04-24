# -*- coding: utf-8 -*-
import urllib.request
import json
import time
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

port = os.environ.get('AUTH_GATEWAY_PORT', '19000')
from_time = int(time.time()) - 172800  # 最近48小时

data = {
    "keyword": "美伊战争 霍尔木兹海峡 最新进展 3月28日",
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
        print(result.get('message', 'No results'))
except Exception as e:
    print(f"Error: {e}")
