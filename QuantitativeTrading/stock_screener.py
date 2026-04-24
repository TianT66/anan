# -*- coding: utf-8 -*-
"""
A股智能选股器 - 基于行业自适应量化系统 v4.0
自动扫描市场，筛选最优股票
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

import time
import random

try:
    import akshare as ak
    NETWORK_AVAILABLE = True
except:
    NETWORK_AVAILABLE = False

from strategies.adaptive_strategy import AdaptiveStrategy
from strategies.value_strategy import ValueStrategy
from strategies.cycle_strategy import CycleStrategy
from strategies.defensive_strategy import DefensiveStrategy


def get_stock_data(code):
    """获取股票实时数据"""
    try:
        # 判断市场
        if code.startswith('6'):
            market = 'sh' + code
        else:
            market = 'sz' + code
        
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock = df[df['代码'] == code]
        
        if stock.empty:
            return None
        
        row = stock.iloc[0]
        
        # 获取基本信息
        info = ak.stock_individual_info_em(symbol=code)
        info_dict = {item['item']: item['value'] for item in info.to_dict('records')}
        
        return {
            'code': code,
            'name': row['名称'],
            'price': float(row['最新价']),
            'change_pct': float(row['涨跌幅']),
            'volume_ratio': float(row['量比']) if row['量比'] != '-' else 1.0,
            'turnover': float(row['换手率']) if row['换手率'] != '-' else 0,
            'pe': float(row['市盈率-动态']) if row['市盈率-动态'] != '-' else 15,
            'pb': float(row['市净率']) if row['市净率'] != '-' else 1.5,
            'market_cap': float(row['总市值']) if row['总市值'] != '-' else 0,
            'industry': info_dict.get('行业', '未知'),
            'high_52w': float(row['52周最高']) if row['52周最高'] != '-' else 0,
            'low_52w': float(row['52周最低']) if row['52周最低'] != '-' else 0,
        }
    except Exception as e:
        print(f"  [WARN] 获取{code}数据失败: {e}")
        return None


def get_stock_history(code, days=60):
    """获取历史数据"""
    try:
        if code.startswith('6'):
            market = 'sh' + code
        else:
            market = 'sz' + code
        
        df = ak.stock_zh_a_hist(symbol=code, period='daily', 
                                  start_date='20250101', end_date='20250325', adjust='qfq')
        
        if df is None or df.empty:
            return None
        
        df.columns = [c.strip() for c in df.columns]
        
        # 计算技术指标
        close = df['收盘'].astype(float)
        
        return {
            'close': close.iloc[-1],
            'ma5': close.rolling(5).mean().iloc[-1],
            'ma20': close.rolling(20).mean().iloc[-1],
            'ma60': close.rolling(60).mean().iloc[-1],
            'volume_ratio': float(df['成交量'].iloc[-1]) / float(df['成交量'].rolling(5).mean().iloc[-1]) if len(df) > 5 else 1.0,
            'rsi6': calculate_rsi(close, 6),
            'rsi14': calculate_rsi(close, 14),
            'macd': calculate_macd(close)[0],
            'price_3d_change': (close.iloc[-1] / close.iloc[-4] - 1) * 100 if len(close) > 4 else 0,
            'price_5d_change': (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(close) > 5 else 0,
            'price_20d_change': (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(close) > 20 else 0,
            'volume': df['成交量'].astype(float).iloc[-5:].mean(),
        }
    except Exception as e:
        print(f"  [WARN] 获取{code}历史数据失败: {e}")
        return None


def calculate_rsi(series, period=14):
    """计算RSI"""
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]


def calculate_macd(series, fast=12, slow=26, signal=9):
    """计算MACD"""
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1]


def get_stock_fundamentals(code):
    """获取基本面数据"""
    try:
        fa = ak.stock_financial_analysis_indicator(symbol=code, start_year='2024')
        
        if fa is None or fa.empty:
            # 返回默认值
            return {
                'pe': 15, 'pb': 1.5, 'roe': 10, 'dividend_yield': 2,
                'revenue_growth': 10, 'profit_growth': 8, 'rd_ratio': 3,
                'gross_margin': 30, 'debt_ratio': 50
            }
        
        latest = fa.iloc[-1]
        
        return {
            'pe': float(latest.get('市盈率(动态)', 15)) if str(latest.get('市盈率(动态)', 'N/A')) != 'N/A' else 15,
            'pb': float(latest.get('市净率', 1.5)) if str(latest.get('市净率', 'N/A')) != 'N/A' else 1.5,
            'roe': float(latest.get('净资产收益率(%)', 10)) if str(latest.get('净资产收益率(%)', 'N/A')) != 'N/A' else 10,
            'dividend_yield': float(latest.get('股息率(%)', 2)) if str(latest.get('股息率(%)', 'N/A')) != 'N/A' else 2,
            'revenue_growth': float(latest.get('营业收入增长率(%)', 10)) if str(latest.get('营业收入增长率(%)', 'N/A')) != 'N/A' else 10,
            'profit_growth': float(latest.get('净利润增长率(%)', 8)) if str(latest.get('净利润增长率(%)', 'N/A')) != 'N/A' else 8,
            'rd_ratio': 3,  # 默认值
            'gross_margin': 30,
            'debt_ratio': 50,
        }
    except Exception as e:
        return {
            'pe': 15, 'pb': 1.5, 'roe': 10, 'dividend_yield': 2,
            'revenue_growth': 10, 'profit_growth': 8, 'rd_ratio': 3,
            'gross_margin': 30, 'debt_ratio': 50
        }


def analyze_stock(code):
    """分析单只股票"""
    print(f"\n[*] 分析 {code}...")
    
    # 获取数据
    spot_data = get_stock_data(code)
    if spot_data is None:
        return None
    
    history_data = get_stock_history(code)
    fundamentals = get_stock_fundamentals(code)
    
    # 合并数据
    if history_data:
        stock_data = history_data
    else:
        stock_data = {
            'close': spot_data['price'],
            'ma5': spot_data['price'] * 0.99,
            'ma20': spot_data['price'] * 1.01,
            'ma60': spot_data['price'] * 1.02,
            'rsi6': 50,
            'rsi14': 50,
            'macd': 0,
            'volume_ratio': 1.0,
            'price_3d_change': spot_data['change_pct'],
            'price_5d_change': spot_data['change_pct'],
            'price_20d_change': spot_data['change_pct'],
        }
    
    # 添加行业
    fundamentals['industry'] = spot_data.get('industry', '未知')
    
    # 使用自适应策略分析
    adaptive = AdaptiveStrategy()
    result = adaptive.analyze(stock_data, fundamentals)
    
    # 添加额外信息
    result['code'] = code
    result['name'] = spot_data['name']
    result['price'] = spot_data['price']
    result['change_pct'] = spot_data['change_pct']
    result['pe'] = spot_data['pe']
    result['pb'] = spot_data['pb']
    result['industry'] = spot_data['industry']
    
    return result


def main():
    print("=" * 80)
    print("  A股智能选股器 - 行业自适应量化系统 v4.0")
    print("=" * 80)
    
    if not NETWORK_AVAILABLE:
        print("\n[WARN] akshare未安装，使用模拟数据")
        use_mock_data()
        return
    
    print("\n[*] 开始扫描A股市场...")
    print("[*] 筛选多行业优质股票...\n")
    
    # 候选股票池（各行业龙头）
    candidates = [
        # 价值型
        '601318',  # 中国平安
        '600036',  # 招商银行
        '600028',  # 中国石化
        # 消费型
        '600519',  # 贵州茅台
        '000858',  # 五粮液
        '000333',  # 美的集团
        # 成长型
        '300750',  # 宁德时代
        '002475',  # 立讯精密
        '300059',  # 东方财富
        # 周期型
        '000528',  # 柳工
        '601899',  # 紫金矿业
        '600019',  # 宝钢股份
        # 防御型
        '000538',  # 云南白药
        '600276',  # 恒瑞医药
        # 新能源
        '002594',  # 比亚迪
        '601012',  # 隆基绿能
        # 科技
        '000725',  # 京东方A
        '002230',  # 科大讯飞
        # 券商
        '600030',  # 中信证券
        '000776',  # 广发证券
    ]
    
    results = []
    
    for code in candidates:
        try:
            result = analyze_stock(code)
            if result:
                results.append(result)
                print(f"  [OK] {result['name']}({code}) - {result['stock_type']} - 得分:{result['score']}")
        except Exception as e:
            print(f"  [FAIL] {code} 分析失败: {e}")
        time.sleep(0.5)  # 避免请求过快
    
    if not results:
        print("\n[WARN] 未能获取数据，使用模拟演示")
        use_mock_data()
        return
    
    # 按得分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 筛选最优5支
    top5 = results[:5]
    
    # 输出推荐
    print("\n" + "=" * 80)
    print("  量化模型精选5支股票推荐")
    print("  生成时间: 2026-03-25")
    print("=" * 80)
    
    total_position = 0
    
    for i, stock in enumerate(top5, 1):
        print(f"\n{'='*80}")
        print(f"  #{i} {stock['name']}({stock['code']})")
        print(f"{'='*80}")
        print(f"  股票类型: {stock['stock_type']}")
        print(f"  当前价格: {stock['price']:.2f} 元 ({stock['change_pct']:+.2f}%)")
        print(f"  市盈率PE: {stock['pe']:.2f}")
        print(f"  市净率PB: {stock['pb']:.2f}")
        print(f"  所属行业: {stock['industry']}")
        print(f"  综合得分: {stock['score']} 分")
        print(f"  交易信号: {stock['signal']}")
        print(f"  建议仓位: {stock['position']*100:.0f}%")
        print(f"  止损位:   {stock['price']*(1+stock['stop_loss']):.2f} 元 ({stock['stop_loss']*100:.0f}%)")
        print(f"  止盈位:   {stock['price']*(1+stock['take_profit']):.2f} 元 ({stock['take_profit']*100:.0f}%)")
        print(f"  持有周期: {stock['hold_period']} 天")
        
        # 生成买卖时机建议
        if stock['signal'] in ['BUY', 'STRONG_BUY']:
            entry_price = stock['price'] * 1.01  # 略高开仓
            print(f"\n  [买入时机]")
            print(f"    建议买入价: {entry_price:.2f} 元")
            print(f"    买入理由: {', '.join(stock['reasons'][:3])}")
        elif stock['signal'] == 'HOLD':
            print(f"\n  [建议观望]")
            print(f"    当前信号为持有，等待更好买点")
            print(f"    关注要点: {', '.join(stock['reasons'][:2])}")
        else:
            print(f"\n  [卖出建议]")
            print(f"    当前信号为卖出，建议减仓或清仓")
        
        total_position += stock['position']
    
    # 仓位分配总结
    print(f"\n{'='*80}")
    print("  仓位分配建议")
    print(f"{'='*80}")
    print(f"  总仓位: {total_position*100:.0f}%")
    print(f"\n  建议买入标的:")
    buy_stocks = [s for s in top5 if s['signal'] in ['BUY', 'STRONG_BUY'] and s['position'] > 0]
    for s in buy_stocks:
        print(f"    - {s['name']}({s['code']}): 仓位 {s['position']*100:.0f}%")
    
    print(f"\n  需观望标的:")
    hold_stocks = [s for s in top5 if s['signal'] == 'HOLD']
    for s in hold_stocks:
        print(f"    - {s['name']}({s['code']}): 等待买点")
    
    # 预期收益计算
    print(f"\n{'='*80}")
    print("  预期收益分析")
    print(f"{'='*80}")
    
    expected_return = 0
    for s in top5:
        if s['position'] > 0:
            # 根据策略类型调整预期
            if s['stock_type'] == 'VALUE':
                expected = s['position'] * 0.12  # 价值股年化12%
            elif s['stock_type'] == 'CYCLICAL':
                expected = s['position'] * 0.25  # 周期股高弹性
            elif s['stock_type'] == 'GROWTH':
                expected = s['position'] * 0.20  # 成长股年化20%
            elif s['stock_type'] == 'NEW_ENERGY':
                expected = s['position'] * 0.18  # 新能源年化18%
            else:
                expected = s['position'] * 0.15
            
            expected_return += expected
            print(f"    {s['name']}: 仓位{s['position']*100:.0f}% * 预期{expected/s['position']*100:.0f}% = {expected*100:.1f}%")
    
    print(f"\n  组合预期年化收益: {expected_return*100:.1f}%")
    print(f"  组合预期月收益: {expected_return/12*100:.2f}%")
    
    print(f"\n{'='*80}")
    print("  风险提示")
    print(f"{'='*80}")
    print("  1. 以上分析基于历史数据和量化模型，不构成投资建议")
    print("  2. A股市场波动较大，建议控制单只股票仓位不超过30%")
    print("  3. 周期股波动较大，需严格止损")
    print("  4. 建议分批建仓，避免一次性全仓")
    print(f"{'='*80}")


def use_mock_data():
    """使用模拟数据演示"""
    print("\n[使用模拟数据进行演示]\n")
    
    # 模拟5支股票
    mock_stocks = [
        {
            'name': '招商银行', 'code': '600036', 'type': 'VALUE',
            'price': 38.50, 'change_pct': 1.25, 'pe': 7.2, 'pb': 1.15,
            'industry': '银行', 'score': 72, 'signal': 'BUY',
            'position': 0.35, 'stop_loss': -0.08, 'take_profit': 0.18,
            'hold_period': 180, 'reasons': ['PE仅7.2，低估值', '股息率4.5%', 'ROE16%高盈利']
        },
        {
            'name': '宁德时代', 'code': '300750', 'type': 'GROWTH',
            'price': 268.50, 'change_pct': -0.85, 'pe': 28.5, 'pb': 5.2,
            'industry': '新能源', 'score': 68, 'signal': 'BUY',
            'position': 0.25, 'stop_loss': -0.05, 'take_profit': 0.15,
            'hold_period': 60, 'reasons': ['新能源龙头', '营收增速85%', '技术面企稳']
        },
        {
            'name': '云南白药', 'code': '000538', 'type': 'DEFENSIVE',
            'price': 58.20, 'change_pct': 0.35, 'pe': 28.5, 'pb': 3.5,
            'industry': '中药', 'score': 65, 'signal': 'HOLD',
            'position': 0.20, 'stop_loss': -0.10, 'take_profit': 0.20,
            'hold_period': 120, 'reasons': ['防御性好', '品牌价值高', '估值合理']
        },
        {
            'name': '紫金矿业', 'code': '601899', 'type': 'CYCLICAL',
            'price': 15.80, 'change_pct': 2.15, 'pe': 18.5, 'pb': 2.8,
            'industry': '有色金属', 'score': 62, 'signal': 'BUY',
            'position': 0.30, 'stop_loss': -0.12, 'take_profit': 0.25,
            'hold_period': 90, 'reasons': ['铜价上涨受益', 'PB2.8适中', '业绩增长']
        },
        {
            'name': '中国平安', 'code': '601318', 'type': 'VALUE',
            'price': 45.60, 'change_pct': 0.82, 'pe': 8.5, 'pb': 1.2,
            'industry': '保险', 'score': 58, 'signal': 'HOLD',
            'position': 0.15, 'stop_loss': -0.08, 'take_profit': 0.15,
            'hold_period': 150, 'reasons': ['PE8.5严重低估', '股息率5.2%', '等待趋势确认']
        },
    ]
    
    for i, stock in enumerate(mock_stocks, 1):
        print(f"\n{'='*70}")
        print(f"  #{i} {stock['name']}({stock['code']}) - {stock['type']}型")
        print(f"{'='*70}")
        print(f"  当前价格: {stock['price']:.2f} 元 ({stock['change_pct']:+.2f}%)")
        print(f"  PE: {stock['pe']:.1f}  PB: {stock['pb']:.1f}  行业: {stock['industry']}")
        print(f"  综合得分: {stock['score']} 分  信号: {stock['signal']}")
        print(f"  建议仓位: {stock['position']*100:.0f}%")
        print(f"  买入价: {stock['price']*1.01:.2f} 元")
        print(f"  止损位: {stock['price']*(1+stock['stop_loss']):.2f} 元 ({stock['stop_loss']*100:.0f}%)")
        print(f"  止盈位: {stock['price']*(1+stock['take_profit']):.2f} 元 ({stock['take_profit']*100:.0f}%)")
        print(f"  持有周期: {stock['hold_period']} 天")
        print(f"  买入理由: {', '.join(stock['reasons'][:2])}")
    
    print(f"\n{'='*70}")
    print("  仓位分配总结")
    print(f"{'='*70}")
    print("  总仓位: 85%")
    print("\n  建议立即买入:")
    print("    - 招商银行(600036): 35% - 低估值价值股")
    print("    - 宁德时代(300750): 25% - 新能源成长股")
    print("    - 紫金矿业(601899): 30% - 周期资源股")
    print("\n  观望等待:")
    print("    - 云南白药(000538): 等待回调")
    print("    - 中国平安(601318): 等待趋势确认")
    
    print(f"\n{'='*70}")
    print("  预期收益分析")
    print(f"{'='*70}")
    print("    招行 35%仓位 * 预期18%收益 = 6.3%")
    print("    宁德 25%仓位 * 预期20%收益 = 5.0%")
    print("    紫金 30%仓位 * 预期25%收益 = 7.5%")
    print("\n    组合预期年化收益: ~18.8%")
    print("    组合预期月收益: ~1.6%")
    
    print(f"\n{'='*70}")
    print("  风险提示")
    print(f"{'='*70}")
    print("    1. 以上为模拟演示，实际操作需验证数据")
    print("    2. 周期股波动大，紫金矿业需严格止损")
    print("    3. 建议分批建仓，总仓位不超过80%")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
