import os

# 检查桌面路径
possible_desktops = [
    r"C:\Users\12408\Desktop",
    r"C:\Users\12408\OneDrive\Desktop",
    r"C:\Users\Public\Desktop",
]

for p in possible_desktops:
    exists = os.path.exists(p)
    writable = os.access(p, os.W_OK) if exists else False
    print(f"{p}")
    print(f"  exists={exists}, writable={writable}")
    if exists:
        # 尝试实际写入
        test = os.path.join(p, "_test_write.txt")
        try:
            with open(test, "w") as f:
                f.write("test")
            os.remove(test)
            print(f"  ACTUALLY WRITABLE!")
        except Exception as e:
            print(f"  Write test failed: {e}")
