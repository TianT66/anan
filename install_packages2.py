# -*- coding: utf-8 -*-
"""创建临时目录并安装依赖"""
import os
import shutil
import tempfile
import subprocess
import sys

# 尝试创建临时目录
temp_base = r"C:\Users\12408\AppData\Roaming"
temp_dir = os.path.join(temp_base, "Temp")

try:
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    print(f"Using temp dir: {temp_dir}")
except Exception as e:
    print(f"Cannot create temp dir: {e}")
    # 使用项目目录作为临时目录
    temp_dir = r"C:\Users\12408\.qclaw\workspace"
    os.environ['TMP'] = temp_dir
    os.environ['TEMP'] = temp_dir
    tempfile.tempdir = temp_dir
    print(f"Fallback to: {temp_dir}")

python_path = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
pip_cmd = [python_path, "-m", "pip", "install", "--user", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]

packages = ["pandas", "numpy", "akshare"]

for pkg in packages:
    print(f"\nInstalling {pkg}...")
    print("-" * 40)
    result = subprocess.run(pip_cmd + [pkg], capture_output=True, text=True, env={**os.environ, 'TMP': temp_dir, 'TEMP': temp_dir})
    if result.returncode == 0:
        print(f"  ✓ {pkg} installed successfully")
    else:
        print(f"  ✗ {pkg} failed")
        print(f"  Error: {result.stderr[-800:]}")
        if result.stdout:
            print(f"  Output: {result.stdout[-800:]}")

print("\n" + "=" * 40)
print("Installation complete!")
