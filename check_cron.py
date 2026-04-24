# -*- coding: utf-8 -*-
"""
查询当前所有cron任务
"""
import sys
import os
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("📋 当前Cron任务列表")
print("=" * 60)
print()

# 使用openclaw脚本查询
openclaw_script = r"C:\Program Files\QClaw\resources\openclaw\config\skills\qclaw-openclaw\scripts\openclaw-win.cmd"

try:
    result = subprocess.run(
        [openclaw_script, "cron", "list"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=r"C:\Users\12408\.qclaw\workspace"
    )
    
    print(f"Exit Code: {result.returncode}")
    print()
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
        
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
