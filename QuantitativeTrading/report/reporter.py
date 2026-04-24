# -*- coding: utf-8 -*-
"""
报告生成模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from datetime import datetime


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.template = """
================================================================
              A股短线量化分析报告
              {timestamp}
================================================================

【股票信息】
  股票代码: {stock_code}
  股票名称: {stock_name}
  分析日期: {analysis_date}

【综合评分】
  总得分: {total_score}/100
  评级: {rating}
  建议仓位: {position_ratio}

【分项得分】
{factor_scores}

【关键指标】
{indicators}

【交易信号】
  信号: {signal}
  原因: {signal_reason}

【风险提示】
{risk_warnings}

================================================================
"""
    
    def generate_analysis_report(self, score_result, stock_code, stock_name=None):
        """生成单股分析报告"""
        if stock_name is None:
            stock_name = stock_code
        
        # 计算评级
        total_score = score_result.get('total_score', 50)
        if total_score >= 80:
            rating = "A (强烈推荐)"
        elif total_score >= 70:
            rating = "B (推荐买入)"
        elif total_score >= 60:
            rating = "C (谨慎买入)"
        elif total_score >= 50:
            rating = "D (观望)"
        else:
            rating = "E (建议回避)"
        
        # 仓位建议
        position_ratio = self._get_position_text(total_score)
        
        # 分项得分
        factor_lines = []
        factor_names = {
            'fund_flow': '资金动向',
            'pattern': 'K线形态',
            'volume_price': '量价配合',
            'momentum': '短线动能',
            'ma_system': '均线系统',
            'macd': 'MACD',
            'kdj': 'KDJ',
            'rsi': 'RSI',
            'limit': '涨跌停',
            'sentiment': '情绪周期'
        }
        
        for key, name in factor_names.items():
            if key in score_result:
                factor = score_result[key]
                score = factor.get('score', 0) if isinstance(factor, dict) else factor
                factor_lines.append(f"  {name}: {score:+.0f}分")
        
        # 关键指标
        indicators = score_result.get('indicators', {})
        indicator_lines = []
        if indicators:
            indicator_lines.append(f"  收盘价: {indicators.get('close', 0):.2f}")
            indicator_lines.append(f"  MA5: {indicators.get('ma5', 0):.2f}")
            indicator_lines.append(f"  MA10: {indicators.get('ma10', 0):.2f}")
            indicator_lines.append(f"  MA20: {indicators.get('ma20', 0):.2f}")
            indicator_lines.append(f"  MACD: {indicators.get('macd', 0):.3f}")
            indicator_lines.append(f"  MACD Signal: {indicators.get('macd_signal', 0):.3f}")
            indicator_lines.append(f"  KDJ K: {indicators.get('kdj_k', 0):.1f}")
            indicator_lines.append(f"  KDJ D: {indicators.get('kdj_d', 0):.1f}")
            indicator_lines.append(f"  KDJ J: {indicators.get('kdj_j', 0):.1f}")
            indicator_lines.append(f"  RSI(6): {indicators.get('rsi_6', 0):.1f}")
            indicator_lines.append(f"  量比: {indicators.get('vol_ratio', 0):.2f}")
            indicator_lines.append(f"  3日涨幅: {indicators.get('pct_3d', 0):.2f}%")
            indicator_lines.append(f"  5日涨幅: {indicators.get('pct_5d', 0):.2f}%")
            indicator_lines.append(f"  今日涨幅: {indicators.get('pct_change', 0):.2f}%")
        
        # 交易信号
        signal_lines = score_result.get('details', [])[:3]
        signal_text = '\n  '.join(signal_lines) if signal_lines else '无明显信号'
        
        # 风险提示
        risk_lines = []
        if indicators.get('rsi_6', 50) > 80:
            risk_lines.append("- RSI严重超买，注意回调风险")
        if indicators.get('kdj_j', 50) > 120:
            risk_lines.append("- KDJ严重超买，注意回调风险")
        if indicators.get('pct_5d', 0) > 20:
            risk_lines.append("- 5日涨幅过大，追高风险高")
        if not risk_lines:
            risk_lines.append("- 暂无明显风险提示")
        
        # 填充模板
        report = self.template.format(
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=datetime.now().strftime('%Y-%m-%d'),
            total_score=total_score,
            rating=rating,
            position_ratio=position_ratio,
            factor_scores='\n'.join(factor_lines) if factor_lines else '  暂无数据',
            indicators='\n'.join(indicator_lines) if indicator_lines else '  暂无数据',
            signal='\n  '.join([score_result.get('total_score', 50) >= 65 and '买入' or '观望']) if True else '观望',
            signal_reason=signal_text,
            risk_warnings='\n'.join(risk_lines)
        )
        
        return report
    
    def _get_position_text(self, score):
        """获取仓位建议文本"""
        if score >= 75:
            return f"重仓 (40%)"
        elif score >= 65:
            return f"标准 (25%)"
        elif score >= 55:
            return f"轻仓 (15%)"
        elif score >= 45:
            return "持有不动"
        else:
            return "清仓观望"


# 全局实例
report_generator = ReportGenerator()
