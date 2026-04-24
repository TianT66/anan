# -*- coding: utf-8 -*-
"""
交易信号模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SignalGenerator:
    """交易信号生成器"""
    
    def __init__(self):
        self.last_signal = None
        self.position = 0  # 0: 空仓, 1: 持仓
        
    def generate_signal(self, df, score_result, position_size=None):
        """
        生成交易信号
        :param df: 包含所有指标的DataFrame
        :param score_result: 综合评分结果
        :param position_size: 当前持仓比例
        :return: 交易信号
        """
        if len(df) < 5:
            return self._create_signal('HOLD', '数据不足')
        
        signal = {
            'timestamp': datetime.now(),
            'close': df['close'].iloc[-1],
            'total_score': score_result.get('total_score', 50),
            'action': 'HOLD',
            'reason': '',
            'risk_warning': False
        }
        
        # 1. 检查止损止盈
        stop_result = self._check_stop_loss_profit(df, score_result)
        if stop_result['triggered']:
            signal['action'] = stop_result['action']
            signal['reason'] = stop_result['reason']
            signal['risk_warning'] = True
            return signal
        
        # 2. 检查持仓时间
        hold_days = self._check_hold_days(df)
        if hold_days >= 5:
            signal['action'] = 'SELL'
            signal['reason'] = f'持仓超过{max(5, 0)}天，最大持仓5天'
            return signal
        
        # 3. 根据评分生成信号
        total_score = score_result.get('total_score', 50)
        
        # 买入信号
        if total_score >= 65 and (position_size is None or position_size == 0):
            signal['action'] = 'BUY'
            signal['reason'] = self._get_buy_reason(score_result)
            signal['position_ratio'] = self._get_position_ratio(total_score)
        
        # 加仓信号
        elif total_score >= 75 and position_size is not None and 0 < position_size < 0.4:
            signal['action'] = 'ADD'
            signal['reason'] = f'评分优秀({total_score:.0f}分)，建议加仓'
            signal['position_ratio'] = min(0.4, position_size + 0.15)
        
        # 减仓信号
        elif total_score < 45 and position_size is not None and position_size > 0:
            signal['action'] = 'REDUCE'
            signal['reason'] = f'评分较弱({total_score:.0f}分)，建议减仓'
            signal['position_ratio'] = position_size * 0.5
        
        # 卖出信号
        elif total_score < 40 and position_size is not None and position_size > 0:
            signal['action'] = 'SELL'
            signal['reason'] = f'评分差({total_score:.0f}分)，建议清仓'
        
        # 持有信号
        else:
            signal['action'] = 'HOLD'
            signal['reason'] = f'评分中性({total_score:.0f}分)，观望'
        
        # 4. 风险警告检查
        risk_warning = self._check_risk_warnings(df, score_result)
        signal['risk_warning'] = risk_warning
        
        return signal
    
    def _check_stop_loss_profit(self, df, score_result):
        """
        检查止损止盈
        """
        if len(df) < 2:
            return {'triggered': False}
        
        # 获取最近N天的价格变化
        latest_pct = df['pct_change'].iloc[-1]
        
        # 简单止损止盈判断
        # 实际应该跟踪买入成本
        if latest_pct <= -5:
            return {
                'triggered': True,
                'action': 'STOP_LOSS',
                'reason': f'触及止损线({latest_pct:.1f}%)'
            }
        elif latest_pct >= 8:
            return {
                'triggered': True,
                'action': 'TAKE_PROFIT',
                'reason': f'触及止盈线({latest_pct:.1f}%)'
            }
        
        return {'triggered': False}
    
    def _check_hold_days(self, df):
        """检查持仓天数"""
        # 这里应该跟踪持仓开始日期
        # 简化处理：检查最近5天内是否有买入信号
        return 0  # 默认返回0，不触发
    
    def _get_buy_reason(self, score_result):
        """获取买入理由"""
        reasons = []
        
        # 汇总各因子得分
        if score_result.get('limit', {}).get('score', 0) > 10:
            reasons.append('涨停板效应')
        
        if score_result.get('pattern', {}).get('score', 0) > 10:
            reasons.append('K线形态佳')
        
        if score_result.get('momentum', {}).get('score', 0) > 10:
            reasons.append('短线动能强劲')
        
        if score_result.get('ma_system', {}).get('score', 0) > 15:
            reasons.append('均线多头排列')
        
        if score_result.get('macd', {}).get('score', 0) > 15:
            reasons.append('MACD金叉')
        
        if not reasons:
            reasons.append('综合评分优秀')
        
        return '+'.join(reasons[:3])
    
    def _get_position_ratio(self, score):
        """根据评分获取建议仓位比例"""
        if score > 85:
            return 0.40
        elif score >= 75:
            return 0.30
        elif score >= 65:
            return 0.25
        elif score >= 55:
            return 0.15
        else:
            return 0.10
    
    def _check_risk_warnings(self, df, score_result):
        """检查风险警告"""
        warnings = []
        
        # RSI超买
        rsi = score_result.get('indicators', {}).get('rsi_6', 50)
        if rsi > 80:
            warnings.append('RSI严重超买')
        
        # KDJ超买
        kdj_j = score_result.get('indicators', {}).get('kdj_j', 50)
        if kdj_j > 120:
            warnings.append('KDJ严重超买')
        
        # 高位放量下跌
        vol_ratio = score_result.get('indicators', {}).get('vol_ratio', 1)
        pct = score_result.get('indicators', {}).get('pct_change', 0)
        if vol_ratio > 2 and pct < -2:
            warnings.append('高位放量下跌')
        
        # 连续涨幅过大
        pct_5d = score_result.get('indicators', {}).get('pct_5d', 0)
        if pct_5d > 20:
            warnings.append('5日涨幅过大，追高风险')
        
        return warnings if warnings else False
    
    def _create_signal(self, action, reason):
        """创建交易信号"""
        return {
            'timestamp': datetime.now(),
            'close': 0,
            'total_score': 50,
            'action': action,
            'reason': reason,
            'risk_warning': False
        }
    
    def format_signal(self, signal):
        """格式化交易信号输出"""
        action = signal.get('action', 'HOLD')
        
        action_text = {
            'BUY': '[买入]',
            'SELL': '[卖出]',
            'ADD': '[加仓]',
            'REDUCE': '[减仓]',
            'HOLD': '[持有]',
            'STOP_LOSS': '[止损]',
            'TAKE_PROFIT': '[止盈]'
        }.get(action, action)
        
        output = f"{action_text} {signal.get('reason', '')}"
        
        if signal.get('risk_warning'):
            warnings = signal.get('risk_warning')
            if warnings:
                if isinstance(warnings, list):
                    output += f" [警告: {', '.join(warnings)}]"
                else:
                    output += f" [警告: {warnings}]"
        
        return output


# 全局实例
signal_generator = SignalGenerator()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    from engine.scorer import ComprehensiveScorer
    
    df = fetcher.get_daily_data('000528', '20240101', '20241231')
    
    cs = ComprehensiveScorer()
    score_result = cs.score(df, '000528')
    
    sg = SignalGenerator()
    signal = sg.generate_signal(df, score_result, position_size=0)
    
    print("[OK] Signal Generated:")
    print(f"  Action: {signal['action']}")
    print(f"  Reason: {signal['reason']}")
    print(f"  Formatted: {sg.format_signal(signal)}")
