import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\12408\.qclaw\media\inbound\股票持仓---ce9b8f9e-5a54-469c-860b-5226f37e8d0d.xlsx'

try:
    df = pd.read_excel(file_path)
    print("持仓数据:")
    print(df.to_string())
except Exception as e:
    print(f"Error: {e}")
