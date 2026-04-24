# -*- coding: utf-8 -*-
"""手动安装依赖脚本"""
import subprocess
import sys
import os

# 设置临时目录到用户可写位置
os.environ['TMP'] = r'C:\Users\12408\AppData\Roaming\Temp'
os.environ['TEMP'] = r'C:\Users\12408\AppData\Roaming\Temp'

python_path = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
pip_cmd = [python_path, "-m", "pip", "install", "--user", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]

packages = ["pandas", "numpy", "akshare"]

for pkg in packages:
    print(f"Installing {pkg}...")
    result = subprocess.run(pip_cmd + [pkg], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✓ {pkg} installed")
    else:
        print(f"  ✗ {pkg} failed: {result.stderr[-500:]}")

print("\nDone!")
