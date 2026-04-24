import os
import shutil

# 用英文文件夹名
desktop = r"C:\Users\12408\Desktop"
src = r"C:\Users\12408\.qclaw\workspace\QuantitativeTrading"
dst = os.path.join(desktop, "QuantitativeTrading")

print(f"Copying to: {dst}")

try:
    if os.path.exists(dst):
        print("Folder already exists, removing...")
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"SUCCESS: Created {dst}")
except Exception as e:
    print(f"Error: {e}")
    # 尝试逐个文件复制
    try:
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
                print(f"  Copied: {item}")
        print("Partial copy done")
    except Exception as e2:
        print(f"Also failed: {e2}")
