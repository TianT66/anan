import os
import shutil

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
src = r"C:\Users\12408\.qclaw\workspace\QuantitativeTrading"
dst = os.path.join(desktop, "量化交易系统")

print(f"Desktop: {desktop}")
print(f"Desktop exists: {os.path.exists(desktop)}")
print(f"Desktop writable: {os.access(desktop, os.W_OK)}")

if os.path.exists(desktop) and os.access(desktop, os.W_OK):
    if os.path.exists(dst):
        print(f"Folder already exists: {dst}")
    else:
        shutil.copytree(src, dst)
        print(f"Created: {dst}")
else:
    print("Cannot write to desktop")
    # 列出可能的桌面路径
    possible = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        r"C:\Users\Public\Desktop",
        r"C:\Users\12408\OneDrive\Desktop",
    ]
    for p in possible:
        print(f"  {p}: exists={os.path.exists(p)}, writable={os.access(p, os.W_OK)}")
