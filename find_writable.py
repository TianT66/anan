# -*- coding: utf-8 -*-
"""寻找可写的目录"""
import os
import tempfile
import sys

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312"
base_dir = r"C:\Users\12408\AppData\Local\Programs"

print("Checking writable locations...")

# 检查各种可能的位置
locations = [
    python_exe,
    os.path.join(python_exe, "Lib"),
    os.path.join(python_exe, "Lib", "site-packages"),
    os.path.join(base_dir),
    r"C:\Users\12408\AppData\Local",
    r"C:\Users\12408\AppData\Local\Temp",
    r"C:\Users\12408\.qclaw",
    r"C:\Users\12408",
]

for loc in locations:
    exists = os.path.exists(loc)
    writable = os.access(loc, os.W_OK) if exists else False
    print(f"  {loc}")
    print(f"    exists: {exists}, writable: {writable}")

# 尝试创建一个测试文件
test_locations = [
    r"C:\Users\12408\AppData\Local\Programs\Python\Python312\Lib\site-packages",
    r"C:\Users\12408\.qclaw\workspace",
]

for loc in test_locations:
    test_file = os.path.join(loc, "test_write_temp.txt")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"  Successfully wrote to: {loc}")
    except Exception as e:
        print(f"  Failed to write to {loc}: {e}")
