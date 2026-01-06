#!/usr/bin/env python3
"""
测试 stop Hook 是否正确发送 agent_completed 事件
"""

import sys
import json
from pathlib import Path

# 模拟 Cursor 调用 stop Hook
test_input = {
    "status": "completed",  # 状态：completed, aborted, error
    "loop_count": 1,
    "conversation_id": "e595bde3-ae8a-4754-a3f2-1d38871068e0",
    "workspace": "/Users/user/Documents/ cursorgirl",
}

print("=" * 60)
print("🧪 测试 stop Hook")
print("=" * 60)
print()
print("📥 输入数据:")
print(json.dumps(test_input, indent=2, ensure_ascii=False))
print()

# 将输入写入临时文件
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(test_input, f)
    temp_file = f.name

print(f"📁 临时文件: {temp_file}")
print()

# 调用 stop Hook
hook_path = Path(__file__).parent / "hooks" / "stop.py"
print(f"🔧 Hook 路径: {hook_path}")
print()

import subprocess
env = {
    "ORTENSIA_INPUT_FILE": temp_file,
    "ORTENSIA_WS_SERVER": "ws://localhost:8765",
    "PATH": sys.executable.rsplit('/', 1)[0] + ":" + subprocess.os.environ.get('PATH', '')
}

print("🚀 执行 Hook...")
print()

result = subprocess.run(
    [sys.executable, str(hook_path)],
    env=env,
    capture_output=True,
    text=True
)

print("=" * 60)
print("📤 输出:")
print("=" * 60)
print(result.stdout)

if result.stderr:
    print()
    print("=" * 60)
    print("⚠️  错误输出:")
    print("=" * 60)
    print(result.stderr)

print()
print("=" * 60)
print(f"✅ 退出码: {result.returncode}")
print("=" * 60)

# 清理临时文件
import os
os.unlink(temp_file)
























