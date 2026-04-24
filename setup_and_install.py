# -*- coding: utf-8 -*-
"""创建可用的临时目录并安装Python包"""
import os
import sys
import tempfile

python_exe = r"C:\Users\12408\AppData\Local\Programs\Python\Python312\python.exe"
user_site = r"C:\Users\12408\AppData\Roaming\Python\Python312\site-packages"

# 创建用户site-packages目录
os.makedirs(user_site, exist_ok=True)
print(f"Created: {user_site}")

# 设置临时目录到用户可写的位置
# 尝试在用户目录创建一个临时目录
tmp_base = r"C:\Users\12408\AppData\Roaming\Temp"
os.makedirs(tmp_base, exist_ok=True)
print(f"Temp dir: {tmp_base}")

# 设置环境变量
os.environ['TMP'] = tmp_base
os.environ['TEMP'] = tmp_base

# 使用subprocess安装包
import subprocess
result = subprocess.run(
    [python_exe, "-m", "pip", "install", 
     "--user",
     "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
     "pandas", "numpy"],
    capture_output=True,
    text=True,
    timeout=300
)

print("STDOUT:", result.stdout[-2000:] if result.stdout else "None")
print("STDERR:", result.stderr[-2000:] if result.stderr else "None")
print("Return code:", result.returncode)

# 验证安装
if result.returncode == 0:
    print("\n--- Verification ---")
    verify = subprocess.run(
        [python_exe, "-c", "import pandas; import numpy; print('pandas:', pandas.__version__); print('numpy:', numpy.__version__)"],
        capture_output=True,
        text=True
    )
    print(verify.stdout)
