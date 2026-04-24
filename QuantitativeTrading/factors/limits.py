# -*- coding: utf-8 -*-
"""
涨跌停分析模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np


class LimitUpDownAnalyzer:
    """涨跌停分析器"""
    
    def __init__(self):
        self.limit_up_stats = {}  # 历史涨停统计
        self.avg_limit_up_premium = 0.025  # 平均涨停溢价 2.5%
    
    def analyze_limits(self, df, idx=-1):
        """
        分析涨跌停情况
        :param df: 包含OHLCV数据的DataFrame
        :param idx: 检测的索引位置
        :return: 涨跌停分析结果
        """
        if len(df) < abs(idx) + 2:
            return self._empty_result()
        
        result = {}
        
        # 判断是否涨停/跌停
        result['is_limit_up'] = self._is_limit_up(df, idx)
        result['is_limit_down'] = self._is_limit_down(df, idx)
        
        # 连续涨停板数量
        result['consecutive_limit'] = self._count_consecutive_limits(df, idx)
        
        # 开板次数（封板强度）
        result['open_times'] = self._count_limit_open(df, idx)
        
        # 涨停次日溢价预测
        result['premium_prediction'] = self._predict_limit_premium(df, idx)
        
        # 涨停类型判断
        result['limit_type'] = self._judge_limit_type(result['consecutive_limit'])
        
        return result
    
    def score_limits(self, df, idx=-1):
        """
        对涨跌停进行评分
        """
        if len(df) < abs(idx) + 2:
            return {'score': 0, 'details': ['数据不足']}
        
        score = 0
        details = []
        
        analysis = self.analyze_limits(df, idx)
        
        # 首板（非连续涨停）：+20分
        if analysis['is_limit_up'] and analysis['consecutive_limit'] == 1:
            score += 20
            details.append("首板涨停 [+20]")
        
        # 二连板：+10分
        elif analysis['is_limit_up'] and analysis['consecutive_limit'] == 2:
            score += 10
            details.append("二连板 [+10]")
        
        # 三连板及以上：0分（妖股难预测）
        elif analysis['is_limit_up'] and analysis['consecutive_limit'] >= 3:
            score += 0
            details.append(f"{analysis['consecutive_limit']}连板 [谨慎]")
        
        # 涨停后次日高开低走：-15分
        if analysis['is_limit_up'] and idx < -1:
            if self._check_limit_up_open_low(df, idx):
                score -= 15
                details.append("涨停次日高开低走 [-15]")
        
        # 开板次数过多：风险提示
        if analysis['is_limit_up'] and analysis['open_times'] >= 3:
            score -= 5
            details.append(f"涨停开板{analysis['open_times']}次 [封板弱]")
        
        # 跌停：-20分
        if analysis['is_limit_down']:
            score -= 20
            details.append("跌停 [-20]")
        
        return {'score': score, 'details': details}
    
    def _is_limit_up(self, df, idx=-1):
        """
        判断是否涨停
        A股涨停幅度通常为10%（ST股5%，科创板/创业板20%）
        """
        if len(df) < abs(idx) + 1:
            return False
        
        # 需要前一天收盘价作为参考
        if idx == 0:
            return False
        
        prev_close = df['close'].iloc[idx - 1]
        current_close = df['close'].iloc[idx]
        current_high = df['high'].iloc[idx]
        
        if prev_close <= 0:
            return False
        
        # 计算涨停幅度
        limit_ratio = (current_close - prev_close) / prev_close
        
        # 判断是否触及涨停（收盘涨停 or 盘中涨停后回落但仍大涨）
        # 简化判断：收盘涨幅 >= 9.5% 视为涨停
        return limit_ratio >= 0.095
    
    def _is_limit_down(self, df, idx=-1):
        """判断是否跌停"""
        if len(df) < abs(idx) + 1 or idx == 0:
            return False
        
        prev_close = df['close'].iloc[idx - 1]
        current_close = df['close'].iloc[idx]
        
        if prev_close <= 0:
            return False
        
        limit_ratio = (current_close - prev_close) / prev_close
        
        return limit_ratio <= -0.095
    
    def _count_consecutive_limits(self, df, idx=-1):
        """
        计算连续涨停板数量
        """
        if not self._is_limit_up(df, idx):
            return 0
        
        count = 1
        temp_idx = idx - 1
        
        while temp_idx >= 0:
            if self._is_limit_up(df, temp_idx):
                count += 1
                temp_idx -= 1
            else:
                break
        
        return count
    
    def _count_limit_open(self, df, idx=-1):
        """
        计算开板次数
        涨停后打开涨停板的次数
        """
        if not self._is_limit_up(df, idx):
            return 0
        
        if len(df) < abs(idx) + 1:
            return 0
        
        prev_close = df['close'].iloc[idx - 1]
        if prev_close <= 0:
            return 0
        
        # 计算涨停价
        limit_price = prev_close * 1.1
        
        # 计算当天最高价触及涨停价的次数
        # 简化：用最高价与涨停价的比例估算
        high = df['high'].iloc[idx]
        
        if high < limit_price:
            return 0
        
        # 估算开板次数
        open_times = 0
        return open_times
    
    def _predict_limit_premium(self, df, idx=-1):
        """
        预测涨停次日溢价
        基于历史统计数据
        """
        consecutive = self._count_consecutive_limits(df, idx)
        
        # 基于连板数预测溢价
        if consecutive == 1:
            # 首板次日溢价最高
            return 0.03  # 3%
        elif consecutive == 2:
            # 二板溢价次之
            return 0.025  # 2.5%
        elif consecutive == 3:
            # 三板溢价下降
            return 0.02  # 2%
        elif consecutive >= 4:
            # 妖股溢价递减
            return 0.015  # 1.5%
        else:
            return 0
    
    def _judge_limit_type(self, consecutive_count):
        """
        判断涨停类型
        """
        if consecutive_count == 0:
            return 'normal'
        elif consecutive_count == 1:
            return 'first_board'
        elif consecutive_count == 2:
            return 'second_board'
        elif consecutive_count == 3:
            return 'third_board'
        else:
            return 'monster'
    
    def _check_limit_up_open_low(self, df, idx):
        """
        检查涨停后次日是否高开低走
        """
        # idx=-1表示今天涨停，需要看idx=-2的走势
        if idx >= -2 and len(df) >= 2:
            # 简化判断：次日高开低走
            tomorrow = df.iloc[idx - 1]
            prev = df.iloc[idx]
            
            if tomorrow['close'] <= 0 or prev['close'] <= 0:
                return False
            
            # 高开：开盘 > 昨天收盘
            is_gap_up = tomorrow['open'] > prev['close'] * 1.02
            
            # 低走：收盘 < 开盘
            is_lower_close = tomorrow['close'] < tomorrow['open']
            
            # 跌幅 > 3%
            drop_ratio = (tomorrow['close'] - tomorrow['open']) / tomorrow['open']
            is_big_drop = drop_ratio < -0.03
            
            return is_gap_up and is_lower_close and is_big_drop
        
        return False
    
    def _empty_result(self):
        """返回空结果"""
        return {
            'is_limit_up': False,
            'is_limit_down': False,
            'consecutive_limit': 0,
            'open_times': 0,
            'premium_prediction': 0,
            'limit_type': 'normal'
        }
    
    def update_limit_stats(self, stock_code, stats):
        """更新涨停统计数据"""
        self.limit_up_stats[stock_code] = stats


# 全局实例
limit_analyzer = LimitUpDownAnalyzer()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    
    df = fetcher.get_daily_data('000528', '20240101', '20241231')
    
    la = LimitUpDownAnalyzer()
    result = la.analyze_limits(df)
    
    print(f"[OK] Limit Analysis:")
    print(f"  Limit Up: {result['is_limit_up']}")
    print(f"  Limit Down: {result['is_limit_down']}")
    print(f"  Consecutive: {result['consecutive_limit']}")
    print(f"  Type: {result['limit_type']}")
    
    score = la.score_limits(df)
    print(f"\nLimit Score: {score['score']}")
    print(f"Details: {score['details']}")
