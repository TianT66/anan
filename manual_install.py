# -*- coding: utf-8 -*-
"""手动下载和安装pandas wheel"""
import urllib.request
import zipfile
import sys
import os
import io

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
site_packages = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\Lib\site-packages"

# PyPI API 获取pandas
print("Fetching pandas from PyPI...")
pypi_url = "https://pypi.org/pypi/pandas/json"

try:
    import json
    with urllib.request.urlopen(pypi_url, timeout=30) as response:
        data = json.loads(response.read())
        
    # 找到适合Python 3.12的wheel文件
    version = data['info']['version']
    print(f"Latest pandas version: {version}")
    
    # 查找合适的wheel
    wheels = data['releases'][version]
    wheel_url = None
    wheel_filename = None
    
    for w in wheels:
        if w['filename'].endswith('-cp312-cp312-win_amd64.whl'):
            wheel_url = w['url']
            wheel_filename = w['filename']
            break
    
    if wheel_url:
        print(f"Downloading {wheel_filename}...")
        wheel_path = os.path.join(site_packages, wheel_filename)
        
        with urllib.request.urlopen(wheel_url, timeout=60) as response:
            wheel_data = response.read()
        
        # 保存wheel文件
        with open(wheel_path, 'wb') as f:
            f.write(wheel_data)
        print(f"Saved to {wheel_path}")
        print(f"Size: {len(wheel_data) / 1024 / 1024:.1f} MB")
        
        # 解压wheel (wheel就是zip文件)
        print("Extracting...")
        with zipfile.ZipFile(io.BytesIO(wheel_data)) as zf:
            zf.extractall(site_packages)
        
        print("Done! pandas installed.")
    else:
        print("No suitable wheel found for Python 3.12 on Windows")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
