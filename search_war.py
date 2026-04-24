import urllib.request
import json
import time
import os

port = os.environ.get('AUTH_GATEWAY_PORT', '19000')
from_time = int(time.time()) - 86400

data = {
    "keyword": "美伊战争 最新进展 3月27日",
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
