# -*- coding: utf-8 -*-
"""安装Python包到用户目录"""
import os
import subprocess
import sys

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"

# 用户目录
user_dir = os.path.expanduser("~")
packages_dir = os.path.join(user_dir, "PythonPackages")
os.makedirs(packages_dir, exist_ok=True)
print(f"Packages dir: {packages_dir}")

# 安装到指定目录
result = subprocess.run(
    [python_exe, "-m", "pip", "install",
     "--target", packages_dir,
     "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
     "pandas", "numpy"],
    capture_output=True,
    text=True,
    timeout=300
)

print("Return code:", result.returncode)
if result.stdout:
    print("Output:", result.stdout[-1000:])
if result.stderr:
    print("Errors:", result.stderr[-1000:])
