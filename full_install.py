# -*- coding: utf-8 -*-
"""完整的包安装脚本 - 全部在Python中执行"""
import urllib.request
import zipfile
import os
import io
import json
import sys
import stat
import shutil

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
site_packages = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\Lib\site-packages"

def download_and_install(package_name, python_version="3.12", win_arch="win_amd64"):
    """从PyPI下载并安装包"""
    print(f"\n{'='*50}")
    print(f"Installing {package_name}...")
    print(f"{'='*50}")
    
    # 获取包信息
    url = f"https://pypi.org/pypi/{package_name}/json"
    print(f"Fetching {url}...")
    
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read())
    
    version = data['info']['version']
    print(f"Latest version: {version}")
    
    # 查找合适的wheel
    release_files = data['releases'][version]
    wheel_url = None
    wheel_filename = None
    
    for f in release_files:
        fn = f['filename']
        if fn.endswith(f'-cp{python_version.replace(".",",")}-cp{python_version.replace(".",",")}-{win_arch}.whl'):
            wheel_url = f['url']
            wheel_filename = fn
            break
    
    if not wheel_url:
        # 尝试其他格式
        for f in release_files:
            fn = f['filename']
            if f'-cp{python_version.replace(".",",")}-' in fn and win_arch in fn and fn.endswith('.whl'):
                wheel_url = f['url']
                wheel_filename = fn
                break
    
    if not wheel_url:
        print(f"No suitable wheel found for Python {python_version} on {win_arch}")
        return False
    
    print(f"Downloading {wheel_filename}...")
    
    # 下载
    with urllib.request.urlopen(wheel_url, timeout=120) as response:
        wheel_data = response.read()
    
    print(f"Downloaded {len(wheel_data) / 1024 / 1024:.1f} MB")
    
    # 解压到site-packages
    print(f"Extracting to {site_packages}...")
    with zipfile.ZipFile(io.BytesIO(wheel_data)) as zf:
        zf.extractall(site_packages)
    
    print(f"✓ {package_name} installed successfully!")
    return True

# 安装依赖
packages_to_install = [
    ("numpy", "pandas"),
    ("pandas", None),
]

# 先安装numpy (pandas的依赖)
print("Installing dependencies...")

# numpy
try:
    download_and_install("numpy")
except Exception as e:
    print(f"Error installing numpy: {e}")

# pandas
try:
    download_and_install("pandas")
except Exception as e:
    print(f"Error installing pandas: {e}")

print("\n" + "="*50)
print("Verification...")
print("="*50)

# 验证
try:
    sys.path.insert(0, site_packages)
    import pandas
    print(f"✓ pandas {pandas.__version__} is working!")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    import numpy
    print(f"✓ numpy {numpy.__version__} is working!")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

print("\nDone!")
