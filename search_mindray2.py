# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import os
import time

PORT = os.environ.get('AUTH_GATEWAY_PORT', '19000')
from_time = int(time.time()) - 2592000  # 最近30天

keyword = '迈瑞医疗 300760 2026年业绩'

url = f'http://localhost:{PORT}/proxy/prosearch/search'
data = json.dumps({'keyword': keyword, 'from_time': from_time}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({'success': False, 'message': str(e)}, ensure_ascii=False))
