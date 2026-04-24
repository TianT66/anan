# -*- coding: utf-8 -*-
import akshare as ak
import sys
import warnings
import time
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')

tests = [
    ('stock_info_a_code_name', lambda: ak.stock_info_a_code_name()),
    ('stock_zh_a_spot_em', lambda: ak.stock_zh_a_spot_em()),
    ('stock_zh_index_spot_em', lambda: ak.stock_zh_index_spot_em()),
    ('stock_financial_analysis_indicator', lambda: ak.stock_financial_analysis_indicator(symbol='000001', start_year='2024')),
]

for name, fn in tests:
    try:
        start = time.time()
        result = fn()
        elapsed = time.time() - start
        if result is not None and not result.empty:
            print(f'OK: {name} ({len(result)} rows, {elapsed:.1f}s)')
            print(f'   Columns: {list(result.columns)[:8]}')
        else:
            print(f'EMPTY: {name}')
    except Exception as e:
        print(f'FAIL: {name}: {str(e)[:80]}')
