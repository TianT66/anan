# -*- coding: utf-8 -*-
"""
A股短线量化系统 v3.0 - 主程序入口
专业级A股短线量化交易系统
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_banner():
    """打印系统横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          A股短线量化系统 v3.0                                 ║
    ║          Professional A-Stock Short-Term Quant System       ║
    ║                                                              ║
    ║          Features:                                           ║
    ║            - 短线专用技术指标体系                             ║
    ║            - K线形态智能识别                                 ║
    ║            - A股特有规律因子                                 ║
    ║            - 仓位与风险控制                                  ║
    ║            - 5年历史数据自我验证                             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def analyze_stock(stock_code):
    """分析单只股票"""
    print(f"\n[*] 正在分析股票: {stock_code}")
    print("-" * 50)
    
    try:
        from data.data_fetcher import fetcher
        from engine.scorer import ComprehensiveScorer
        from report.reporter import ReportGenerator
        
        # 获取数据
        print(f"[1] 获取数据...")
        df = fetcher.get_daily_data(stock_code, '20240101', '20241231', adjust='qfq')
        if df is None or df.empty:
            print("[FAIL] 数据获取失败")
            return
        
        print(f"[OK] 获取到 {len(df)} 条数据")
        
        # 计算评分
        print(f"\n[2] 计算综合评分...")
        scorer = ComprehensiveScorer()
        score_result = scorer.score(df, stock_code)
        
        print(f"\n[OK] 综合评分: {score_result['total_score']:.1f}/100")
        
        # 生成报告
        print(f"\n[3] 生成分析报告...")
        reporter = ReportGenerator()
        report = reporter.generate_analysis_report(score_result, stock_code)
        
        print(report)
        
        # 仓位建议
        position = scorer.get_position_recommendation(score_result['total_score'])
        print(f"\n[推荐] {position['action']} - 建议仓位: {position['position']*100:.0f}%")
        
    except Exception as e:
        print(f"[ERROR] 分析失败: {e}")
        import traceback
        traceback.print_exc()


def run_backtest_single(stock_code):
    """单只股票回测"""
    print(f"\n[*] 回测股票: {stock_code}")
    print("-" * 50)
    
    try:
        from data.data_fetcher import fetcher
        from backtest.backtest_engine import BacktestEngine
        from backtest.validator import StrategyValidator
        
        # 获取数据
        print(f"[1] 获取数据...")
        df = fetcher.get_daily_data(stock_code, '20200101', '20241231', adjust='qfq')
        if df is None or df.empty:
            print("[FAIL] 数据获取失败")
            return
        
        print(f"[OK] 获取到 {len(df)} 条数据")
        
        # 创建策略函数
        validator = StrategyValidator()
        
        # 运行回测
        print(f"\n[2] 运行回测...")
        bt = BacktestEngine(initial_capital=100000)
        
        def strategy_func(data):
            return validator._calculate_score(data)
        
        result = bt.run_backtest(
            df, stock_code,
            strategy_func=strategy_func,
            stop_loss=-0.05,
            take_profit=0.08,
            max_hold_days=5
        )
        
        # 输出结果
        metrics = result.get('metrics', {})
        if not metrics:
            print("[FAIL] 回测失败")
            return
        
        print(f"\n[OK] 回测完成")
        print("-" * 50)
        print(f"  策略总收益:   {metrics.get('strategy_profit_rate', 0)*100:+.1f}%")
        print(f"  买入持有收益: {metrics.get('bh_profit_rate', 0)*100:+.1f}%")
        print(f"  相对收益:     {metrics.get('relative_profit', 0)*100:+.1f}%")
        print(f"  年化收益率:   {metrics.get('annual_return', 0)*100:+.1f}%")
        print(f"  最大回撤:    {metrics.get('max_drawdown', 0)*100:.1f}%")
        print(f"  夏普比率:     {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  胜率:        {metrics.get('win_rate', 0)*100:.1f}%")
        print(f"  盈亏比:       {metrics.get('profit_loss_ratio', 0):.2f}")
        print(f"  总交易次数:   {metrics.get('total_trades', 0)}次")
        print("-" * 50)
        
    except Exception as e:
        print(f"[ERROR] 回测失败: {e}")
        import traceback
        traceback.print_exc()


def run_strategy_validation():
    """运行策略验证"""
    print("\n[*] 开始策略验证...")
    print("-" * 50)
    
    try:
        from backtest.validator import StrategyValidator
        
        validator = StrategyValidator()
        summary = validator.validate_strategy()
        
        return summary
        
    except Exception as e:
        print(f"[ERROR] 验证失败: {e}")
        import traceback
        traceback.print_exc()


def batch_analyze():
    """批量分析多只股票"""
    print("\n[*] 批量分析股票池...")
    print("-" * 50)
    
    stocks = [
        ('000528', '柳工'),
        ('600519', '贵州茅台'),
        ('300750', '宁德时代'),
        ('002475', '立讯精密'),
        ('300059', '东方财富'),
    ]
    
    try:
        from data.data_fetcher import fetcher
        from engine.scorer import ComprehensiveScorer
        
        results = []
        
        for code, name in stocks:
            try:
                print(f"\n[*] 分析 {code} {name}...")
                df = fetcher.get_daily_data(code, '20240101', '20241231', adjust='qfq')
                
                if df is None or df.empty:
                    print(f"[FAIL] {code} 数据获取失败")
                    continue
                
                scorer = ComprehensiveScorer()
                score_result = scorer.score(df, code)
                
                results.append({
                    'code': code,
                    'name': name,
                    'score': score_result['total_score'],
                    'close': score_result.get('indicators', {}).get('close', 0)
                })
                
                position = scorer.get_position_recommendation(score_result['total_score'])
                print(f"[OK] {code} {name}: {score_result['total_score']:.1f}分 - {position['action']}")
                
            except Exception as e:
                print(f"[FAIL] {code} 分析失败: {e}")
        
        # 排序输出
        if results:
            print("\n" + "=" * 50)
            print("  股票池综合评分排名")
            print("=" * 50)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['code']} {r['name']:<8} {r['score']:.1f}分  (最新价: {r['close']:.2f})")
            
            print("=" * 50)
    
    except Exception as e:
        print(f"[ERROR] 批量分析失败: {e}")


def main():
    """主函数"""
    print_banner()
    
    while True:
        print("\n" + "=" * 50)
        print("  主菜单")
        print("=" * 50)
        print("  1. 单股分析")
        print("  2. 单股回测")
        print("  3. 策略验证（10只股票5年回测）")
        print("  4. 批量分析股票池")
        print("  0. 退出")
        print("=" * 50)
        
        try:
            choice = input("\n请选择操作 [0-4]: ").strip()
            
            if choice == '1':
                stock_code = input("请输入股票代码: ").strip()
                if stock_code:
                    analyze_stock(stock_code)
                else:
                    print("[WARN] 股票代码不能为空")
            
            elif choice == '2':
                stock_code = input("请输入股票代码: ").strip()
                if stock_code:
                    run_backtest_single(stock_code)
                else:
                    print("[WARN] 股票代码不能为空")
            
            elif choice == '3':
                confirm = input("此操作将回测10只股票5年数据，可能需要几分钟。是否继续？(y/n): ").strip().lower()
                if confirm == 'y':
                    run_strategy_validation()
                else:
                    print("[INFO] 已取消")
            
            elif choice == '4':
                batch_analyze()
            
            elif choice == '0':
                print("\n[INFO] 感谢使用A股短线量化系统 v3.0！")
                break
            
            else:
                print("[WARN] 无效选择，请重新输入")
        
        except KeyboardInterrupt:
            print("\n\n[INFO] 用户中断，退出程序")
            break
        except Exception as e:
            print(f"\n[ERROR] 发生错误: {e}")


if __name__ == '__main__':
    main()
