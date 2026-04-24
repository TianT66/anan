# -*- coding: utf-8 -*-
"""
验证报告模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from datetime import datetime


class ValidatorReportGenerator:
    """验证报告生成器"""
    
    def generate_full_report(self, summary, stock_results):
        """生成完整的验证报告"""
        lines = []
        
        lines.append("=" * 80)
        lines.append("                    A股短线量化系统 v3.0 - 策略验证报告")
        lines.append(f"                    生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        
        # 策略概述
        lines.append("\n【策略概述】")
        lines.append("-" * 40)
        lines.append(f"  策略名称: A股短线多因子策略 v3.0")
        lines.append(f"  策略类型: 短线量化交易")
        lines.append(f"  核心因子:")
        lines.append(f"    - 技术指标: 均线系统、MACD、KDJ、RSI")
        lines.append(f"    - K线形态: 阳包阴、锤子线、早晨之星等")
        lines.append(f"    - 量价配合: 放量上涨、缩量回调等")
        lines.append(f"    - 市场情绪: 涨停板效应、板块联动")
        lines.append(f"  回测标的: A股10只代表性股票")
        lines.append(f"  回测周期: 2020-01-01 至 2024-12-31 (5年)")
        lines.append(f"  初始资金: 100,000元")
        
        # 总体表现
        lines.append("\n【总体表现】")
        lines.append("-" * 40)
        
        strategy_ret = summary.get('avg_strategy_return', 0) * 100
        bh_ret = summary.get('avg_bh_return', 0) * 100
        rel_ret = summary.get('avg_relative', 0) * 100
        annual_ret = summary.get('avg_annual', 0) * 100
        max_dd = summary.get('avg_max_dd', 0) * 100
        sharpe = summary.get('avg_sharpe', 0)
        win_rate = summary.get('avg_win_rate', 0) * 100
        profit_loss = summary.get('avg_profit_loss', 0)
        
        lines.append(f"  策略总收益率:     {strategy_ret:+.1f}%")
        lines.append(f"  买入持有收益率:   {bh_ret:+.1f}%")
        lines.append(f"  相对收益:         {rel_ret:+.1f}%")
        lines.append(f"  年化收益率:       {annual_ret:.1f}%")
        lines.append(f"  最大回撤:         {max_dd:.1f}%")
        lines.append(f"  夏普比率:         {sharpe:.2f}")
        lines.append(f"  胜率:             {win_rate:.1f}%")
        lines.append(f"  盈亏比:           {profit_loss:.2f}")
        lines.append(f"  总交易次数:       {summary.get('total_trades', 0)}次")
        
        # 验证结论
        lines.append("\n【验证结论】")
        lines.append("-" * 40)
        
        checks = [
            ("年化收益 > 10%", annual_ret > 10),
            ("最大回撤 < 20%", max_dd < 20),
            ("夏普比率 > 0.5", sharpe > 0.5),
            ("胜率 > 50%", win_rate > 50),
            ("跑赢基准", rel_ret > 0),
        ]
        
        for check_name, passed in checks:
            status = "[PASS]" if passed else "[FAIL]"
            lines.append(f"  {status} {check_name}")
        
        # 分股票表现
        lines.append("\n【分股票表现明细】")
        lines.append("-" * 80)
        lines.append(f"{'代码':<8} {'名称':<8} {'行业':<10} {'策略%':>8} {'持有%':>8} {'相对%':>8} {'胜率':>6} {'回撤':>7} {'交易':>5}")
        lines.append("-" * 80)
        
        for sr in stock_results:
            m = sr['metrics']
            lines.append(
                f"{sr['code']:<8} {sr['name']:<8} {sr['sector']:<10} "
                f"{m.get('strategy_profit_rate', 0)*100:>+7.1f}% {m.get('bh_profit_rate', 0)*100:>+7.1f}% "
                f"{m.get('relative_profit', 0)*100:>+7.1f}% {m.get('win_rate', 0)*100:>5.1f}% "
                f"{m.get('max_drawdown', 0)*100:>6.1f}% {m.get('total_trades', 0):>5d}"
            )
        
        lines.append("-" * 80)
        
        # 行业分析
        lines.append("\n【行业分析】")
        lines.append("-" * 40)
        
        sector_results = {}
        for sr in stock_results:
            sector = sr['sector']
            if sector not in sector_results:
                sector_results[sector] = []
            sector_results[sector].append(sr['metrics'].get('relative_profit', 0) * 100)
        
        for sector, rel_returns in sorted(sector_results.items(), key=lambda x: -sum(x[1])/len(x[1]) if x[1] else 0):
            avg_rel = sum(rel_returns) / len(rel_returns) if rel_returns else 0
            status = "[优秀]" if avg_rel > 10 else ("[良好]" if avg_rel > 0 else "[较弱]")
            lines.append(f"  {sector:<10} 平均相对收益: {avg_rel:+.1f}% {status}")
        
        # 改进建议
        lines.append("\n【改进建议】")
        lines.append("-" * 40)
        
        suggestions = [
            "1. 短线策略适合波动较大的消费、科技类股票，建议重点配置",
            "2. 金融、周期类股票短线效果一般，建议采用中线或长线策略",
            "3. 建议设置动态止损，根据市场波动调整止损幅度",
            "4. 关注板块轮动机会，在强势板块中精选个股",
            "5. 控制单股仓位，避免过度集中风险",
            "6. 结合大盘指数，避免在大盘弱势时重仓操作",
        ]
        
        for s in suggestions:
            lines.append(f"  {s}")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


# 全局实例
validator_report_generator = ValidatorReportGenerator()
