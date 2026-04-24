# -*- coding: utf-8 -*-
"""
全市场股票获取 - 腾讯接口全面测试
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time

def try_tencent_full():
    """腾讯全量接口"""
    stocks = []
    
    # 腾讯行情接口 - 测试不同的市场
    tests = [
        # 沪深主要股票
        ('https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?apptype=&isrc=&count=1&_var=kline_dayqfq&param=sh000001,day,,,,,100,qfq&_=0', '测试'),
    ]
    
    for url, name in tests:
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://finance.qq.com/',
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode('utf-8')
                print(f"  {name}: {data[:200]}")
        except Exception as e:
            print(f"  {name}失败: {e}")
    
    return stocks

def try_jqdata_public():
    """聚宽公开数据接口"""
    stocks = []
    
    # 聚宽数据中心 - 免费数据
    try:
        url = 'https://dataapi.joinquant.com/apis'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode()
            print(f"  聚宽响应: {content[:200]}")
    except Exception as e:
        print(f"  聚宽失败: {e}")
    
    return stocks

def try_tushare_style():
    """Tushare风格接口"""
    stocks = []
    
    # SinoStockAPI
    try:
        url = 'http://api.sosit.com.cn/api/stock?type=hs&market=cn&page=1&limit=5000'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"  SinoStock: {len(data)}条")
    except Exception as e:
        print(f"  SinoStock失败: {e}")
    
    return stocks

def try_eastmoney_new():
    """东方财富新版接口"""
    stocks = []
    
    # 新版东方财富行情接口
    urls_to_test = [
        'https://push2.eastmoney.com/api/qt/ulist/get?pn=1&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23&fields=f2%2Cf3%2Cf4%2Cf5%2Cf6%2Cf7%2Cf8%2Cf9%2Cf10%2Cf12%2Cf13%2Cf14%2Cf15%2Cf16%2Cf17%2Cf18%2Cf20%2Cf21%2Cf23%2Cf24%2Cf25%2Cf22%2Cf11%2Cf62%2Cf128%2Cf136%2Cf115%2Cf152&cb=&_=0',
        'http://push2.eastmoney.com/api/qt/ulist/get?pn=1&pz=500&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23&fields=f2%2Cf3%2Cf4%2Cf5%2Cf6%2Cf7%2Cf8%2Cf9%2Cf10%2Cf12%2Cf13%2Cf14%2Cf15%2Cf16%2Cf17%2Cf18%2Cf20%2Cf21%2Cf23%2Cf24%2Cf25%2Cf22%2Cf11%2Cf62%2Cf128%2Cf136%2Cf115%2Cf152',
    ]
    
    for url in urls_to_test:
        print(f"  测试: {url[:80]}...")
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'http://quote.eastmoney.com/',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('data') and data['data'].get('diff'):
                    print(f"  成功: {len(data['data']['diff'])}只")
                    for s in data['data']['diff'][:3]:
                        print(f"    {s.get('f12')} {s.get('f14')} PE:{s.get('f9')}")
                else:
                    print(f"  无数据: {str(data)[:200]}")
        except Exception as e:
            print(f"  失败: {e}")
    
    return stocks

def try_sina_new_api():
    """新版新浪API"""
    stocks = []
    
    # 新浪财经股票列表 - 不同的接口
    apis = [
        # 方式1: 标准接口
        'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=5000&sort=symbol&asc=1&node=hs_a&_s_r_a=page',
        # 方式2: 批量
        'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=1000&sort=symbol&asc=1&node=hs_a&_s_r_a=page&count=5000',
    ]
    
    for url in apis:
        print(f"  测试: {url[:80]}...")
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn/',
                'Accept': '*/*',
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode('gbk')
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        print(f"  成功: {len(data)}条")
                        # 看看都是哪些市场
                        sh = len([d for d in data if str(d.get('symbol','')).startswith('6')])
                        sz = len([d for d in data if str(d.get('symbol','')).startswith(('0','3'))])
                        bj = len([d for d in data if str(d.get('symbol','')).startswith(('4','8','9'))])
                        print(f"    上交所:{sh} 深交所:{sz} 北交所:{bj}")
                        for d in data[:3]:
                            print(f"    {d.get('symbol')} {d.get('name')} PE:{d.get('peratio','-')}")
                    else:
                        print(f"  返回类型: {type(data)}")
                        print(f"  内容: {str(data)[:200]}")
                except json.JSONDecodeError as je:
                    print(f"  JSON解析失败: {je}")
                    print(f"  内容前200字符: {content[:200]}")
        except Exception as e:
            print(f"  失败: {e}")
        time.sleep(1)
    
    return stocks

print("=" * 80)
print("  全市场股票获取 - 接口测试")
print("  2026-03-27 07:40")
print("=" * 80)

print("\n[1] 测试腾讯接口...")
try_tencent_full()

print("\n[2] 测试聚宽...")
try_jqdata_public()

print("\n[3] 测试东方财富新版...")
try_eastmoney_new()

print("\n[4] 测试新浪新版...")
try_sina_new_api()

print("\n" + "=" * 80)
