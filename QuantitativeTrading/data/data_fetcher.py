# -*- coding: utf-8 -*-
"""
数据采集模块
支持akshare数据获取，失败时返回模拟数据
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import random
from datetime import datetime, timedelta

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except:
    AKSHARE_AVAILABLE = False


class DataFetcher:
    """数据采集器"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_daily(self, code, start_date=None, end_date=None):
        """
        获取股票日线数据
        返回格式: DataFrame with columns [date, open, high, low, close, volume]
        """
        try:
            if AKSHARE_AVAILABLE:
                # 转换为akshare格式
                if code.startswith('6'):
                    symbol = f"sh{code}"
                else:
                    symbol = f"sz{code}"
                
                df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, 
                                        end_date=end_date, adjust="qfq")
                if df is not None and len(df) > 0:
                    return df
        except Exception as e:
            pass
        
        # 返回模拟数据
        return self._generate_mock_data(code, start_date, end_date)
    
    def _generate_mock_data(self, code, start_date=None, end_date=None):
        """生成模拟数据"""
        import pandas as pd
        
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        # 根据股票代码生成不同的初始价格
        base_prices = {
            '601318': 50, '600036': 35, '601288': 5, '600028': 5,
            '600519': 1800, '000858': 180, '000596': 250, '000333': 60,
            '300750': 180, '002475': 40, '300059': 25, '688041': 100,
            '000528': 8, '600019': 6, '601899': 15, '000983': 8,
            '000538': 90, '600276': 50, '300760': 350,
            '002594': 250, '601012': 40
        }
        
        base_price = base_prices.get(code, 30)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成模拟价格走势
        data = []
        price = base_price
        for date in dates:
            if random.random() > 0.3:  # 70%交易日有数据
                change = random.uniform(-0.03, 0.035)
                price = price * (1 + change)
                open_price = price * random.uniform(0.98, 1.02)
                high = max(price, open_price) * random.uniform(1.0, 1.03)
                low = min(price, open_price) * random.uniform(0.97, 1.0)
                volume = random.randint(1000000, 50000000)
                
                data.append({
                    '日期': date.strftime('%Y-%m-%d'),
                    '开盘': round(open_price, 2),
                    '收盘': round(price, 2),
                    '最高': round(high, 2),
                    '最低': round(low, 2),
                    '成交量': volume
                })
        
        df = pd.DataFrame(data)
        if '日期' in df.columns:
            df.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close',
                              '最高': 'high', '最低': 'low', '成交量': 'volume'}, inplace=True)
        return df
    
    def get_stock_fundamentals(self, code):
        """
        获取股票基本面数据
        返回: dict with PE, PB, ROE, dividend_yield, revenue_growth, etc.
        """
        fundamentals = {
            'code': code,
            'pe': 15.0,
            'pb': 1.5,
            'roe': 12.0,
            'dividend_yield': 2.5,
            'revenue_growth': 10.0,
            'profit_growth': 8.0,
            'rd_ratio': 3.0,
            'industry': '未知',
            'market_cap': 1000  # 亿
        }
        
        try:
            if AKSHARE_AVAILABLE:
                try:
                    # 获取实时行情
                    df = ak.stock_zh_a_spot_em()
                    stock_row = df[df['代码'] == code]
                    if len(stock_row) > 0:
                        row = stock_row.iloc[0]
                        fundamentals['pe'] = float(row.get('市盈率-动态', 15))
                        fundamentals['pb'] = float(row.get('市净率', 1.5))
                        fundamentals['market_cap'] = float(row.get('总市值', 1000)) / 100000000
                except:
                    pass
        except:
            pass
        
        # 根据股票代码返回预设基本面数据
        fundamental_db = {
            '601318': {'pe': 10.5, 'pb': 1.2, 'roe': 15.0, 'dividend_yield': 4.5, 
                      'revenue_growth': 5.0, 'profit_growth': 3.0, 'rd_ratio': 1.5, 'industry': '保险'},
            '600036': {'pe': 6.5, 'pb': 0.9, 'roe': 14.0, 'dividend_yield': 4.8, 
                      'revenue_growth': 8.0, 'profit_growth': 10.0, 'rd_ratio': 0.5, 'industry': '银行'},
            '601288': {'pe': 5.8, 'pb': 0.7, 'roe': 12.0, 'dividend_yield': 5.2, 
                      'revenue_growth': 6.0, 'profit_growth': 5.0, 'rd_ratio': 0.3, 'industry': '银行'},
            '600028': {'pe': 8.0, 'pb': 0.85, 'roe': 10.0, 'dividend_yield': 6.5, 
                      'revenue_growth': 3.0, 'profit_growth': 2.0, 'rd_ratio': 0.8, 'industry': '石油'},
            '600519': {'pe': 35.0, 'pb': 8.0, 'roe': 28.0, 'dividend_yield': 1.8, 
                      'revenue_growth': 15.0, 'profit_growth': 18.0, 'rd_ratio': 2.5, 'industry': '白酒'},
            '000858': {'pe': 28.0, 'pb': 5.5, 'roe': 22.0, 'dividend_yield': 2.2, 
                      'revenue_growth': 20.0, 'profit_growth': 25.0, 'rd_ratio': 2.0, 'industry': '白酒'},
            '000596': {'pe': 32.0, 'pb': 6.0, 'roe': 24.0, 'dividend_yield': 1.5, 
                      'revenue_growth': 18.0, 'profit_growth': 20.0, 'rd_ratio': 1.8, 'industry': '白酒'},
            '000333': {'pe': 15.0, 'pb': 3.5, 'roe': 25.0, 'dividend_yield': 3.5, 
                      'revenue_growth': 12.0, 'profit_growth': 15.0, 'rd_ratio': 4.0, 'industry': '家电'},
            '300750': {'pe': 45.0, 'pb': 6.0, 'roe': 18.0, 'dividend_yield': 0.5, 
                      'revenue_growth': 80.0, 'profit_growth': 90.0, 'rd_ratio': 8.0, 'industry': '半导体'},
            '002475': {'pe': 35.0, 'pb': 4.5, 'roe': 20.0, 'dividend_yield': 1.0, 
                      'revenue_growth': 35.0, 'profit_growth': 40.0, 'rd_ratio': 6.0, 'industry': '电子'},
            '300059': {'pe': 40.0, 'pb': 4.0, 'roe': 15.0, 'dividend_yield': 0.8, 
                      'revenue_growth': 25.0, 'profit_growth': 30.0, 'rd_ratio': 5.0, 'industry': '互联网'},
            '688041': {'pe': 80.0, 'pb': 8.0, 'roe': 5.0, 'dividend_yield': 0.0, 
                      'revenue_growth': 50.0, 'profit_growth': -10.0, 'rd_ratio': 25.0, 'industry': '半导体'},
            '000528': {'pe': 12.0, 'pb': 0.8, 'roe': 8.0, 'dividend_yield': 3.0, 
                      'revenue_growth': -5.0, 'profit_growth': -15.0, 'rd_ratio': 4.0, 'industry': '工程机械'},
            '600019': {'pe': 8.0, 'pb': 0.7, 'roe': 6.0, 'dividend_yield': 4.0, 
                      'revenue_growth': -10.0, 'profit_growth': -20.0, 'rd_ratio': 2.0, 'industry': '钢铁'},
            '601899': {'pe': 18.0, 'pb': 2.5, 'roe': 18.0, 'dividend_yield': 2.5, 
                      'revenue_growth': 15.0, 'profit_growth': 20.0, 'rd_ratio': 2.5, 'industry': '有色'},
            '000983': {'pe': 6.0, 'pb': 0.7, 'roe': 12.0, 'dividend_yield': 5.0, 
                      'revenue_growth': 10.0, 'profit_growth': 15.0, 'rd_ratio': 2.0, 'industry': '煤炭'},
            '000538': {'pe': 22.0, 'pb': 3.0, 'roe': 18.0, 'dividend_yield': 2.5, 
                      'revenue_growth': 8.0, 'profit_growth': 10.0, 'rd_ratio': 2.0, 'industry': '医药'},
            '600276': {'pe': 60.0, 'pb': 8.0, 'roe': 12.0, 'dividend_yield': 0.8, 
                      'revenue_growth': -5.0, 'profit_growth': -20.0, 'rd_ratio': 18.0, 'industry': '医药'},
            '300760': {'pe': 40.0, 'pb': 7.0, 'roe': 28.0, 'dividend_yield': 1.2, 
                      'revenue_growth': 20.0, 'profit_growth': 22.0, 'rd_ratio': 10.0, 'industry': '医疗器械'},
            '002594': {'pe': 50.0, 'pb': 5.5, 'roe': 16.0, 'dividend_yield': 0.5, 
                      'revenue_growth': 40.0, 'profit_growth': 45.0, 'rd_ratio': 5.0, 'industry': '新能源车'},
            '601012': {'pe': 20.0, 'pb': 2.8, 'roe': 18.0, 'dividend_yield': 2.0, 
                      'revenue_growth': 30.0, 'profit_growth': 35.0, 'rd_ratio': 3.0, 'industry': '光伏'},
        }
        
        if code in fundamental_db:
            fundamentals.update(fundamental_db[code])
        
        return fundamentals
    
    def get_index_daily(self, index_code='sh000300', start_date=None, end_date=None):
        """获取指数数据（沪深300）"""
        try:
            if AKSHARE_AVAILABLE:
                df = ak.stock_zh_index_daily(symbol=index_code)
                if start_date:
                    df = df[df['date'] >= start_date]
                if end_date:
                    df = df[df['date'] <= end_date]
                return df
        except:
            pass
        
        # 返回模拟数据
        import pandas as pd
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        price = 4000
        data = []
        for date in dates:
            if random.random() > 0.3:
                change = random.uniform(-0.015, 0.016)
                price = price * (1 + change)
                data.append({'date': date.strftime('%Y-%m-%d'), 'close': round(price, 2)})
        
        return pd.DataFrame(data)
    
    def get_ppi_data(self):
        """获取PPI数据（工业生产者出厂价格指数）"""
        try:
            if AKSHARE_AVAILABLE:
                df = ak.macro_china_ppi()
                if df is not None and len(df) > 0:
                    return df
        except:
            pass
        
        # 返回模拟PPI数据
        import pandas as pd
        dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='M')
        base_ppi = 100
        data = []
        for date in dates:
            change = random.uniform(-0.02, 0.03)
            base_ppi = base_ppi * (1 + change)
            data.append({'month': date.strftime('%Y-%m'), 'ppi': round(base_ppi, 2)})
        
        return pd.DataFrame(data)


# 单例
data_fetcher = DataFetcher()


def get_stock_daily(code, start_date=None, end_date=None):
    return data_fetcher.get_stock_daily(code, start_date, end_date)


def get_stock_fundamentals(code):
    return data_fetcher.get_stock_fundamentals(code)


def get_index_daily(index_code='sh000300', start_date=None, end_date=None):
    return data_fetcher.get_index_daily(index_code, start_date, end_date)


def get_ppi_data():
    return data_fetcher.get_ppi_data()