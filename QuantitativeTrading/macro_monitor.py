# -*- coding: utf-8 -*-
"""
宏观事件监控系统 - 量化系统 v5.0
同步经济周期、国际事件、政策导向
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\12408\.qclaw\workspace\QuantitativeTrading')

from datetime import datetime


class MacroMonitor:
    """宏观监控系统"""
    
    def __init__(self):
        self.data_sources = {
            'economic': '经济数据（PMI/CPI/PPI/利率）',
            'policy': '国内政策（央行/证监会/国务院）',
            'international': '国际事件（美联储/地缘政治）',
            'five_year_plan': '十五五规划（产业政策）'
        }
    
    def get_economic_cycle(self):
        """
        经济周期判断
        基于PMI、CPI、PPI、利率等数据
        """
        # 模拟当前经济状态（实际应接入Wind/Choice数据）
        economic_data = {
            'pmi': 49.2,  # 制造业PMI
            'pmi_trend': '下降',  # 环比变化
            'cpi': 0.7,  # 通胀率
            'ppi': -2.5,  # 工业品价格
            'gdp_growth': 5.2,  # GDP增速
            'interest_rate': 3.45,  # LPR利率
            'm2_growth': 8.7,  # M2增速
            'credit_growth': 9.5,  # 社融增速
        }
        
        # 经济周期判断
        cycle_score = 0
        cycle_signals = []
        
        # PMI判断
        if economic_data['pmi'] > 50:
            cycle_score += 2
            cycle_signals.append("PMI>50，制造业扩张")
        elif economic_data['pmi'] > 48:
            cycle_score += 0
            cycle_signals.append("PMI在荣枯线附近，经济承压")
        else:
            cycle_score -= 2
            cycle_signals.append("PMI<48，制造业收缩")
        
        # PPI判断（通缩/通胀）
        if economic_data['ppi'] < -3:
            cycle_score -= 1
            cycle_signals.append("PPI深度负值，通缩风险")
        elif economic_data['ppi'] > 3:
            cycle_score -= 1
            cycle_signals.append("PPI过高，通胀压力")
        
        # 利率判断
        if economic_data['interest_rate'] < 3.5:
            cycle_score += 1
            cycle_signals.append("低利率环境，流动性宽松")
        
        # 确定周期阶段
        if cycle_score >= 3:
            cycle = 'EXPANSION'  # 扩张期
            position = 0.80
        elif cycle_score >= 1:
            cycle = 'RECOVERY'  # 复苏期
            position = 0.70
        elif cycle_score >= -1:
            cycle = 'SLOWDOWN'  # 放缓期
            position = 0.50
        else:
            cycle = 'RECESSION'  # 衰退期
            position = 0.30
        
        return {
            'cycle': cycle,
            'cycle_cn': {
                'EXPANSION': '扩张期',
                'RECOVERY': '复苏期',
                'SLOWDOWN': '放缓期',
                'RECESSION': '衰退期'
            }.get(cycle, '未知'),
            'score': cycle_score,
            'data': economic_data,
            'signals': cycle_signals,
            'position_suggestion': position
        }
    
    def get_policy_signals(self):
        """
        政策信号监控
        央行货币政策、证监会监管政策、国务院产业政策
        """
        # 模拟当前政策环境
        policies = {
            'monetary': {  # 货币政策
                'direction': '宽松',
                'recent_actions': [
                    '2025-02-20: 央行降准0.5个百分点',
                    '2025-01-15: LPR下调10个基点',
                ],
                'outlook': '继续宽松',
                'impact': 1  # 正面
            },
            'regulatory': {  # 监管政策
                'direction': '稳市场',
                'recent_actions': [
                    '2025-03-10: 证监会加强退市监管',
                    '2025-02-28: 限制融券做空',
                ],
                'outlook': '从严监管',
                'impact': 0  # 中性
            },
            'fiscal': {  # 财政政策
                'direction': '积极',
                'recent_actions': [
                    '2025-03-05: 政府工作报告：赤字率3%',
                    '2025-03-01: 发行特别国债1万亿',
                ],
                'outlook': '持续发力',
                'impact': 1  # 正面
            }
        }
        
        # 计算政策综合得分
        policy_score = sum(p['impact'] for p in policies.values())
        
        return {
            'score': policy_score,
            'policies': policies,
            'overall': '积极宽松' if policy_score > 0 else '紧缩' if policy_score < 0 else '中性',
            'position_adjust': 0.10 if policy_score > 0 else -0.10 if policy_score < 0 else 0
        }
    
    def get_international_events(self):
        """
        国际敏感事件监控
        美联储政策、地缘政治、贸易战
        """
        events = {
            'fed': {  # 美联储
                'current_rate': 5.25,
                'expected_moves': [
                    {'date': '2025-03-20', 'action': '维持利率不变', 'probability': 0.70},
                    {'date': '2025-05-01', 'action': '降息25bp', 'probability': 0.60},
                ],
                'impact': 0,  # 中性，预期降息利好
                'risk_level': '中等'
            },
            'geopolitics': {  # 地缘政治
                'hotspots': [
                    '中东局势：伊朗-以色列紧张',
                    '台海局势：持续紧张',
                    '俄乌冲突：持续',
                ],
                'impact': -1,  # 负面，避险情绪
                'risk_level': '高'
            },
            'trade': {  # 贸易战
                'issues': [
                    '中美科技脱钩：芯片限制持续',
                    '关税：美国对华关税维持',
                    '新能源：欧盟反补贴调查',
                ],
                'impact': -1,  # 负面
                'risk_level': '中等'
            }
        }
        
        # 计算国际风险得分
        risk_score = sum(e['impact'] for e in events.values())
        
        return {
            'score': risk_score,
            'events': events,
            'risk_level': '高' if risk_score < -2 else '中等' if risk_score < 0 else '低',
            'position_adjust': -0.15 if risk_score < -2 else -0.10 if risk_score < 0 else 0
        }
    
    def get_five_year_plan(self):
        """
        十五五规划（2026-2030）产业方向
        提前布局政策支持产业
        """
        plan = {
            'period': '2026-2030',
            'key_industries': [
                {
                    'name': '人工智能',
                    'priority': '最高',
                    'targets': 'AI算力翻倍，大模型自主可控',
                    'beneficiaries': ['算力芯片', '光模块', '数据中心', '大模型'],
                    'investment_scale': '万亿级',
                    'timeline': '2026年起加速'
                },
                {
                    'name': '新能源',
                    'priority': '高',
                    'targets': '非化石能源占比25%，储能大规模应用',
                    'beneficiaries': ['光伏', '储能', '氢能', '智能电网'],
                    'investment_scale': '万亿级',
                    'timeline': '持续推进'
                },
                {
                    'name': '半导体',
                    'priority': '最高',
                    'targets': '14nm以下自主可控，国产替代率70%',
                    'beneficiaries': ['设备', '材料', 'EDA', '制造'],
                    'investment_scale': '万亿级',
                    'timeline': '2026-2027关键期'
                },
                {
                    'name': '生物医药',
                    'priority': '高',
                    'targets': '创新药自主可控，CXO产业升级',
                    'beneficiaries': ['创新药', 'CXO', '医疗器械', '基因治疗'],
                    'investment_scale': '千亿级',
                    'timeline': '持续推进'
                },
                {
                    'name': '高端制造',
                    'priority': '高',
                    'targets': '工业机器人密度翻倍，智能制造普及',
                    'beneficiaries': ['工业机器人', '数控机床', '工业软件'],
                    'investment_scale': '万亿级',
                    'timeline': '2026年起加速'
                }
            ],
            'regional': [
                '长三角：集成电路、人工智能',
                '珠三角：新能源、智能制造',
                '京津冀：科技创新、数字经济',
                '成渝：电子信息、装备制造'
            ]
        }
        
        return plan
    
    def get_composite_signal(self):
        """
        综合宏观信号
        整合所有宏观因素给出最终仓位建议
        """
        economic = self.get_economic_cycle()
        policy = self.get_policy_signals()
        international = self.get_international_events()
        
        # 基础仓位（经济周期决定）
        base_position = economic['position_suggestion']
        
        # 政策调整
        policy_adjust = policy['position_adjust']
        
        # 国际风险调整
        international_adjust = international['position_adjust']
        
        # 综合仓位
        final_position = base_position + policy_adjust + international_adjust
        final_position = max(0.20, min(0.90, final_position))  # 限制在20%-90%
        
        # 生成综合报告
        signals = []
        signals.extend(economic['signals'])
        signals.append(f"政策环境：{policy['overall']}")
        signals.append(f"国际风险：{international['risk_level']}")
        
        return {
            'economic_cycle': economic['cycle_cn'],
            'economic_score': economic['score'],
            'policy_score': policy['score'],
            'international_score': international['score'],
            'base_position': base_position,
            'policy_adjust': policy_adjust,
            'international_adjust': international_adjust,
            'final_position': final_position,
            'signals': signals,
            'key_industries': self.get_five_year_plan()['key_industries']
        }


def print_macro_report():
    """打印宏观报告"""
    monitor = MacroMonitor()
    signal = monitor.get_composite_signal()
    plan = monitor.get_five_year_plan()
    
    print("=" * 80)
    print("  宏观事件监控系统 v5.0")
    print("  分析时间:", datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("=" * 80)
    
    print("\n【一、经济周期判断】")
    print(f"  当前周期: {signal['economic_cycle']}")
    print(f"  经济评分: {signal['economic_score']}/5")
    print(f"  基础仓位: {signal['base_position']*100:.0f}%")
    print("\n  关键信号:")
    for s in signal['signals'][:5]:
        print(f"    - {s}")
    
    print("\n【二、政策环境】")
    policy = monitor.get_policy_signals()
    print(f"  政策综合评分: {policy['score']}")
    print(f"  政策基调: {policy['overall']}")
    print(f"  仓位调整: {policy['position_adjust']*100:+.0f}%")
    print("\n  近期政策:")
    for action in policy['policies']['monetary']['recent_actions'][:2]:
        print(f"    - {action}")
    
    print("\n【三、国际事件风险】")
    international = monitor.get_international_events()
    print(f"  国际风险评分: {international['score']}")
    print(f"  风险等级: {international['risk_level']}")
    print(f"  仓位调整: {international['position_adjust']*100:+.0f}%")
    print("\n  关注事件:")
    for hotspot in international['events']['geopolitics']['hotspots'][:2]:
        print(f"    - {hotspot}")
    
    print("\n【四、十五五规划产业方向】")
    print(f"  规划期: {plan['period']}")
    print("\n  重点产业:")
    for industry in plan['key_industries'][:3]:
        print(f"    {industry['name']} ({industry['priority']}优先级)")
        print(f"      目标: {industry['targets']}")
        print(f"      投资规模: {industry['investment_scale']}")
        print(f"      受益: {', '.join(industry['beneficiaries'][:3])}")
    
    print("\n【五、综合仓位建议】")
    print(f"  经济周期基础仓位: {signal['base_position']*100:.0f}%")
    print(f"  政策调整: {signal['policy_adjust']*100:+.0f}%")
    print(f"  国际风险调整: {signal['international_adjust']*100:+.0f}%")
    print(f"\n  >>> 最终建议仓位: {signal['final_position']*100:.0f}% <<<")
    
    print("\n【六、行业配置建议】")
    if signal['final_position'] > 0.60:
        print("  市场环境: 积极")
        print("  超配: 科技成长（AI、半导体、新能源）")
        print("  标配: 消费、医药")
        print("  低配: 银行、公用事业")
    elif signal['final_position'] > 0.40:
        print("  市场环境: 中性")
        print("  均衡配置: 价值+成长各半")
        print("  关注: 十五五规划受益产业")
    else:
        print("  市场环境: 谨慎")
        print("  超配: 防御性板块（高股息、医药、消费）")
        print("  低配: 周期、科技成长")
        print("  保留: 60%以上现金")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_macro_report()
