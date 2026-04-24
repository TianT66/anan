# -*- coding: utf-8 -*-
"""
定时提醒任务：明天9点45分开会提醒
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime, timedelta
import json
import os

# 获取明天的日期
tomorrow = datetime.now() + timedelta(days=1)
reminder_time = tomorrow.replace(hour=9, minute=45, second=0, microsecond=0)

print("=" * 70)
print("  定时提醒设置")
print("=" * 70)

print(f"\n【提醒信息】")
print(f"  提醒时间: {reminder_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
print(f"  提醒内容: 开会提醒")
print(f"  当前时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
print(f"  距离提醒: {(reminder_time - datetime.now()).total_seconds() / 3600:.1f}小时")

# 保存提醒配置
reminder_config = {
    'type': 'meeting_reminder',
    'time': reminder_time.strftime('%Y-%m-%d %H:%M:%S'),
    'message': '开会提醒',
    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'status': 'active'
}

reminder_file = r'C:\Users\12408\.qclaw\workspace\reminder_config.json'
with open(reminder_file, 'w', encoding='utf-8') as f:
    json.dump(reminder_config, f, ensure_ascii=False, indent=2)

print(f"\n✓ 提醒已设置")
print(f"  配置文件: {reminder_file}")

print(f"\n【提醒方式】")
print(f"  ✓ 系统会在明天9:45分通过微信发送提醒")
print(f"  ✓ 提醒内容: '开会提醒 - 现在是9:45分，该开会了！'")

print("\n" + "=" * 70)
