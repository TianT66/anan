# -*- coding: utf-8 -*-
"""直接安装包到site-packages"""
import subprocess
import os

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
site_packages = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\Lib\site-packages"

# 直接安装到site-packages
result = subprocess.run(
    [python_exe, "-m", "pip", "install",
     "--target", site_packages,
     "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
     "pandas", "numpy"],
    capture_output=True,
    text=True,
    timeout=300
)

print("Return code:", result.returncode)
if result.stdout:
    print("Output:", result.stdout[-2000:])
if result.stderr:
    print("Errors:", result.stderr[-2000:])
