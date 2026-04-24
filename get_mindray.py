# -*- coding: utf-8 -*-
import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 迈瑞医疗实时数据
url = "https://qt.gtimg.cn/q=sz300760"

req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=10) as response:
    content = response.read().decode('gbk')
    print(content)
    
    # 解析数据
    if 'v_sz300760=' in content:
        data_str = content.split('v_sz300760="')[1].split('";')[0]
        fields = data_str.split('~')
        
        print("\n=== 迈瑞医疗 300760 实时数据 ===")
        print(f"名称: {fields[1]}")
        print(f"代码: {fields[2]}")
        print(f"当前价: {fields[3]} 元")
        print(f"昨收: {fields[4]} 元")
        print(f"今开: {fields[5]} 元")
        print(f"成交量: {fields[6]} 手 ({int(fields[6])/10000:.2f}万手)")
        print(f"外盘: {fields[7]} 手")
        print(f"内盘: {fields[8]} 手")
        print(f"涨跌: {fields[30]} 元 ({fields[31]}%)")
        print(f"最高: {fields[32]} 元")
        print(f"最低: {fields[33]} 元")
        print(f"成交额: {float(fields[36])/100000000:.2f} 亿元")
        print(f"换手率: {fields[37]}%")
        print(f"振幅: {fields[43]}%")
        print(f"更新时间: {fields[29]}")
