# -*- coding: utf-8 -*-
"""修复版: 直接下载安装 numpy 和 pandas"""
import urllib.request
import zipfile
import os
import io
import json
import sys

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
site_packages = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\Lib\site-packages"

def get_wheel_url(package_name, py_ver="cp312", platform="win_amd64"):
    """获取合适版本的wheel URL"""
    url = f"https://pypi.org/pypi/{package_name}/json"
    print(f"Fetching {package_name}...")
    
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read())
    
    version = data['info']['version']
    print(f"  Version: {version}")
    
    # 直接搜索精确匹配
    target = f"-{py_ver}-{py_ver}-{platform}.whl"
    release_files = data['releases'][version]
    
    for f in release_files:
        fn = f['filename']
        if target in fn and fn.endswith('.whl'):
            print(f"  Found: {fn}")
            return f['url'], fn
    
    print(f"  Not found with target: {target}")
    return None, None

def install_package(package_name, py_ver="cp312", platform="win_amd64"):
    """下载并安装包"""
    print(f"\nInstalling {package_name}...")
    
    wheel_url, wheel_name = get_wheel_url(package_name, py_ver, platform)
    if not wheel_url:
        print(f"  Failed to find wheel for {package_name}")
        return False
    
    print(f"  Downloading {wheel_name}...")
    with urllib.request.urlopen(wheel_url, timeout=120) as response:
        wheel_data = response.read()
    
    print(f"  Size: {len(wheel_data) / 1024 / 1024:.1f} MB")
    print(f"  Extracting to {site_packages}...")
    
    with zipfile.ZipFile(io.BytesIO(wheel_data)) as zf:
        zf.extractall(site_packages)
    
    print(f"  [OK] {package_name} installed!")
    return True

# 安装 numpy
install_package("numpy")

# 安装 pandas
install_package("pandas")

print("\n" + "="*50)
print("Verification:")
print("="*50)

# 验证
test_code = """
import sys
sys.path.insert(0, r'C:\\Users\\12408\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages')
import numpy
import pandas
print('numpy:', numpy.__version__)
print('pandas:', pandas.__version__)
"""

os.system(f'"{python_exe}" -c "{test_code}"')
