# -*- coding: utf-8 -*-
"""使用内置urllib直接下载和安装pandas"""
import urllib.request
import zipfile
import os
import sys

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
print("Testing direct urllib usage...")

# 简单的网络测试
try:
    response = urllib.request.urlopen("https://pypi.org/simple/pandas/", timeout=10)
    print("Network OK! Can access PyPI")
except Exception as e:
    print(f"Network error: {e}")

print("\nPython version:", sys.version)
print("Executable:", sys.executable)

# 检查可写目录
user_dir = os.path.expanduser("~")
print("User home:", user_dir)
print("User home writable:", os.access(user_dir, os.W_OK))

# 尝试在用户目录创建文件
test_file = os.path.join(user_dir, "test_write.txt")
try:
    with open(test_file, "w") as f:
        f.write("test")
    print("Can write to user home!")
    os.remove(test_file)
except Exception as e:
    print(f"Cannot write to user home: {e}")

# 检查site-packages
import site
print("\nSite packages locations:")
for sp in site.getsitepackages():
    print(f"  {sp}")
    print(f"    Writable: {os.access(sp, os.W_OK)}")

print("\nUser site packages:", site.getusersitepackages())
print("User site writable:", os.access(site.getusersitepackages(), os.W_OK))
