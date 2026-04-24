# -*- coding: utf-8 -*-
import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 测试获取几只股票
url = 'https://qt.gtimg.cn/q=sz000001,sh600519,sz300760,sz002371'
req = urllib.request.Request(url)
req.add_header('User-Agent', 'Mozilla/5.0')
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('gbk')

print("Raw data:")
for line in content.strip().split('\n'):
    if '~' in line:
        print(line[:200])
        fields = line.split('~')
        if len(fields) >= 35:
            print(f"Parsed - Code: {fields[2]}, Name: {fields[1]}, Price: {fields[3]}, Change: {fields[31]}%")
        print()
