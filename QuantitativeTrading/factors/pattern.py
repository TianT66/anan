# -*- coding: utf-8 -*-
"""
K线形态识别模块 - A股短线量化系统 v3.0
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np


class PatternRecognition:
    """K线形态识别器"""
    
    def __init__(self):
        self.patterns = {}
    
    def detect_all_patterns(self, df, idx=-1):
        """
        检测所有K线形态
        :param df: 包含OHLCV数据的DataFrame
        :param idx: 检测的索引位置（-1为最新）
        :return: 形态检测结果字典
        """
        if len(df) < abs(idx) + 5:
            return {'pattern': None, 'score': 0, 'details': ['数据不足']}
        
        results = {}
        
        # 检测各种形态
        results['bullish_engulfing'] = self._is_bullish_engulfing(df, idx)
        results['hammer'] = self._is_hammer(df, idx)
        results['morning_star'] = self._is_morning_star(df, idx)
        results['evening_star'] = self._is_evening_star(df, idx)
        results['spinning_top'] = self._is_spinning_top(df, idx)
        results['small_white_up'] = self._is_small_white_up(df, idx)
        results['shooting_star'] = self._is_shooting_star(df, idx)
        results['doji'] = self._is_doji(df, idx)
        
        return results
    
    def score_patterns(self, df, idx=-1):
        """
        对K线形态进行评分
        返回格式: {'score': int, 'details': list}
        """
        if len(df) < abs(idx) + 2:
            return {'score': 0, 'details': ['数据不足']}
        
        score = 0
        details = []
        
        # 阳包阴（吞没形态）：+15分
        if self._is_bullish_engulfing(df, idx):
            score += 15
            details.append("阳包阴(吞没形态) [+15]")
        
        # 底部十字星 +锤子线：+10分
        is_doji = self._is_doji(df, idx)
        is_hammer = self._is_hammer(df, idx)
        if is_doji or is_hammer:
            score += 10
            if is_doji:
                details.append("底部十字星 [+10]")
            if is_hammer:
                details.append("锤子线 [+10]")
        
        # 仙人指路（长上影）：-10分
        if self._is_shooting_star(df, idx):
            score -= 10
            details.append("仙人指路(长上影) [-10]")
        
        # 高位螺旋桨：-15分
        if self._is_spinning_top(df, idx):
            # 检查是否在高位
            ma5 = df['ma5'].iloc[idx]
            close = df['close'].iloc[idx]
            if close > ma5 * 1.05:  # 高位区域
                score -= 15
                details.append("高位螺旋桨 [-15]")
        
        # 连续小阳线攀升：+10分
        if self._is_small_white_up(df, idx):
            score += 10
            details.append("连续小阳线攀升 [+10]")
        
        # 早晨之星：+15分（强烈看涨信号）
        if self._is_morning_star(df, idx):
            score += 15
            details.append("早晨之星 [+15]")
        
        # 黄昏之星：-15分（强烈看跌信号）
        if self._is_evening_star(df, idx):
            score -= 15
            details.append("黄昏之星 [-15]")
        
        return {'score': score, 'details': details}
    
    def _is_bullish_engulfing(self, df, idx=-1):
        """
        阳包阴（看涨吞没形态）
        条件：1. 第一根K线是阴线
              2. 第二根K线是阳线
              3. 第二根K线的实体完全覆盖第一根K线
        """
        if len(df) < abs(idx) + 2:
            return False
        
        # 需要前一根K线
        i = idx - 1
        
        # 第一根K线（阴线）
        open1 = df['open'].iloc[i]
        close1 = df['close'].iloc[i]
        body1 = abs(close1 - open1)
        is_bearish1 = close1 < open1
        
        # 第二根K线（阳线）
        open2 = df['open'].iloc[idx]
        close2 = df['close'].iloc[idx]
        body2 = close2 - open2
        is_bullish2 = close2 > open2
        
        if not (is_bearish1 and is_bullish2):
            return False
        
        # 检查吞没
        body_covered = (open2 <= close1) and (close2 >= open1)
        
        return body_covered
    
    def _is_hammer(self, df, idx=-1):
        """
        锤子线
        条件：1. 下影线是实体的2倍以上
              2. 上影线很短（<实体的10%）
              3. 实体在价格区间的上部
        """
        if len(df) < abs(idx) + 1:
            return False
        
        open_price = df['open'].iloc[idx]
        close = df['close'].iloc[idx]
        high = df['high'].iloc[idx]
        low = df['low'].iloc[idx]
        
        body = abs(close - open_price)
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        total_range = high - low
        
        if total_range <= 0:
            return False
        
        # 下影线是实体的2倍以上
        # 上影线很短
        # 实体在价格区间上部（阳线）
        is_small_upper = upper_shadow < body * 0.1
        is_long_lower = lower_shadow > body * 2
        is_white = close > open_price
        
        # 判断是否在底部区域
        is_at_bottom = low < df['ma5'].iloc[idx] * 0.98 if 'ma5' in df.columns else True
        
        return is_small_upper and is_long_lower and is_white and is_at_bottom
    
    def _is_doji(self, df, idx=-1):
        """
        十字星
        条件：开盘价和收盘价非常接近（差异<0.1%）
        """
        if len(df) < abs(idx) + 1:
            return False
        
        open_price = df['open'].iloc[idx]
        close = df['close'].iloc[idx]
        
        if open_price == 0:
            return False
        
        # 差异小于0.5%
        diff_ratio = abs(close - open_price) / open_price
        is_doji = diff_ratio < 0.005
        
        # 同时需要有上下影线
        high = df['high'].iloc[idx]
        low = df['low'].iloc[idx]
        body = abs(close - open_price)
        total_range = high - low
        
        has_shadow = total_range > body * 2
        
        return is_doji and has_shadow
    
    def _is_morning_star(self, df, idx=-1):
        """
        早晨之星（三日形态）
        第一天：大阴线，下跌趋势
        第二天：小实体（十字星最好），显示犹豫
        第三天：大阳线，确认反转
        """
        if len(df) < abs(idx) + 3:
            return False
        
        # 三根K线
        i = idx - 2
        o1, c1, h1, l1 = self._get_ohlc(df, i)
        o2, c2, h2, l2 = self._get_ohlc(df, i+1)
        o3, c3, h3, l3 = self._get_ohlc(df, idx)
        
        # 第一天：大阴线
        body1 = abs(c1 - o1)
        range1 = h1 - l1
        is_big_bearish1 = (c1 < o1) and (body1 > range1 * 0.7)
        
        # 第二天：小实体
        body2 = abs(c2 - o2)
        range2 = h2 - l2
        is_small2 = body2 < body1 * 0.3
        
        # 第三天：大阳线
        body3 = c3 - o3
        range3 = h3 - l3
        is_big_bullish3 = (c3 > o3) and (body3 > range3 * 0.7)
        
        # 价格关系：第三天收盘在第一天实体中上部
        price_confirm = c3 > (o1 + c1) / 2
        
        return is_big_bearish1 and is_small2 and is_big_bullish3 and price_confirm
    
    def _is_evening_star(self, df, idx=-1):
        """
        黄昏之星（三日形态）
        第一天：大阳线，上涨趋势
        第二天：小实体，显示犹豫
        第三天：大阴线，确认反转
        """
        if len(df) < abs(idx) + 3:
            return False
        
        i = idx - 2
        o1, c1, h1, l1 = self._get_ohlc(df, i)
        o2, c2, h2, l2 = self._get_ohlc(df, i+1)
        o3, c3, h3, l3 = self._get_ohlc(df, idx)
        
        # 第一天：大阳线
        body1 = c1 - o1
        range1 = h1 - l1
        is_big_bullish1 = (c1 > o1) and (body1 > range1 * 0.7)
        
        # 第二天：小实体
        body2 = abs(c2 - o2)
        is_small2 = body2 < body1 * 0.3
        
        # 第三天：大阴线
        body3 = abs(c3 - o3)
        range3 = h3 - l3
        is_big_bearish3 = (c3 < o3) and (body3 > range3 * 0.7)
        
        # 价格关系：第三天收盘在第一天实体中下部
        price_confirm = c3 < (o1 + c1) / 2
        
        return is_big_bullish1 and is_small2 and is_big_bearish3 and price_confirm
    
    def _is_spinning_top(self, df, idx=-1):
        """
        螺旋桨（陀螺线）
        条件：上下影线都很长，实体很小
        """
        if len(df) < abs(idx) + 1:
            return False
        
        o, c, h, l = self._get_ohlc(df, idx)
        
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        total_range = h - l
        
        if total_range <= 0:
            return False
        
        # 实体小于整根K线的30%
        is_small_body = body < total_range * 0.3
        
        # 上下影线都比较长（>实体的50%）
        is_long_shadow = (upper_shadow > body * 0.5) and (lower_shadow > body * 0.5)
        
        return is_small_body and is_long_shadow
    
    def _is_shooting_star(self, df, idx=-1):
        """
        射击之星（仙人指路）
        条件：上影线很长（>实体的2倍），下影线很短
        """
        if len(df) < abs(idx) + 1:
            return False
        
        o, c, h, l = self._get_ohlc(df, idx)
        
        body = abs(c - o)
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        
        # 上影线很长
        is_long_upper = upper_shadow > body * 2
        
        # 下影线很短
        is_short_lower = lower_shadow < body * 0.3
        
        return is_long_upper and is_short_lower
    
    def _is_small_white_up(self, df, idx=-1):
        """
        连续小阳线攀升
        检查最近N天是否有连续的小阳线上涨
        """
        if len(df) < abs(idx) + 4:
            return False
        
        # 检查最近3天
        count = 0
        for i in range(idx - 2, idx + 1):
            o, c, h, l = self._get_ohlc(df, i)
            body = c - o
            total_range = h - l
            
            # 小阳线：涨幅<2%，实体>影线
            if body > 0 and body > 0 and total_range > 0:
                body_ratio = body / total_range
                pct_change = body / o * 100
                if pct_change < 2 and body_ratio > 0.5:
                    count += 1
        
        return count >= 3
    
    def _get_ohlc(self, df, idx):
        """获取指定索引的OHLC数据"""
        return (
            df['open'].iloc[idx],
            df['close'].iloc[idx],
            df['high'].iloc[idx],
            df['low'].iloc[idx]
        )
    
    def get_pattern_description(self, results):
        """获取形态描述"""
        patterns_found = []
        for pattern, detected in results.items():
            if detected:
                pattern_names = {
                    'bullish_engulfing': '阳包阴',
                    'hammer': '锤子线',
                    'morning_star': '早晨之星',
                    'evening_star': '黄昏之星',
                    'spinning_top': '螺旋桨',
                    'small_white_up': '连续小阳线',
                    'shooting_star': '射击之星',
                    'doji': '十字星'
                }
                patterns_found.append(pattern_names.get(pattern, pattern))
        
        return patterns_found if patterns_found else ['无明显形态']


# 全局实例
pattern_recognizer = PatternRecognition()


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, '..')
    from data.data_fetcher import fetcher
    
    df = fetcher.get_daily_data('000528', '20240101', '20241231')
    pr = PatternRecognition()
    
    results = pr.detect_all_patterns(df)
    print("[OK] Patterns detected:")
    for pattern, detected in results.items():
        if detected:
            print(f"  - {pattern}: detected")
    
    score_result = pr.score_patterns(df)
    print(f"\nPattern Score: {score_result['score']}")
    print(f"Details: {score_result['details']}")
