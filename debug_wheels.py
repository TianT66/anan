# -*- coding: utf-8 -*-
"""Debug: 查看可用的wheels"""
import urllib.request
import json

def check_wheels(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    print(f"\n=== {package_name} ===")
    
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read())
    
    version = data['info']['version']
    print(f"Latest: {version}")
    
    # 列出所有文件
    release_files = data['releases'][version]
    print(f"Total files: {len(release_files)}")
    
    # 找windows的wheel
    win_wheels = [f for f in release_files if 'win' in f['filename'].lower() and f['filename'].endswith('.whl')]
    print(f"\nWindows wheels ({len(win_wheels)}):")
    for w in win_wheels[:10]:
        print(f"  {w['filename']}")

check_wheels("numpy")
check_wheels("pandas")
