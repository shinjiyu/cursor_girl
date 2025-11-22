#!/usr/bin/env python3
"""
测试环境变量是否能从 inject 传递到 hook
"""

import os
import sys

print("=" * 60)
print("测试环境变量传递")
print("=" * 60)

inject_id = os.getenv('ORTENSIA_INJECT_ID', '')
print(f"\nORTENSIA_INJECT_ID = '{inject_id}'")

if inject_id:
    print("✅ 环境变量成功传递！")
else:
    print("❌ 环境变量未传递")

print("\n所有环境变量:")
for key in sorted(os.environ.keys()):
    if 'ORTENSIA' in key or 'CURSOR' in key or 'ELECTRON' in key:
        print(f"  {key} = {os.environ[key]}")

print("=" * 60)

