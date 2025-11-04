#!/usr/bin/env python3
"""快速测试脚本 - 获取一次 DOM 快照并测试基本操作"""

import asyncio
import sys
import os

# 导入监控器和操作器
sys.path.insert(0, os.path.dirname(__file__))
from dom_monitor import DOMMonitor
from composer_operations import ComposerOperator


async def main():
    print('=' * 70)
    print('  🧪 Cursor 快速测试')
    print('=' * 70)
    print()
    
    # 测试 1: 获取 DOM 快照
    print('测试 1: 获取 DOM 快照')
    print('─' * 70)
    
    monitor = DOMMonitor()
    await monitor.connect()
    
    snapshot = await monitor.get_composer_snapshot()
    monitor.print_snapshot(snapshot)
    
    await monitor.stop_monitoring()
    
    print()
    
    # 测试 2: 测试基本操作
    print('测试 2: 测试基本操作')
    print('─' * 70)
    
    operator = ComposerOperator()
    await operator.connect()
    
    # 2.1 查找输入框
    print('\n2.1 查找输入框...')
    result = await operator.find_input()
    if result['success']:
        print(f'✅ 找到输入框')
        print(f'   为空: {result.get("isEmpty")}')
        print(f'   内容: "{result.get("content", "")[:50]}"')
    else:
        print(f'❌ {result.get("error")}')
    
    # 2.2 查找提交按钮
    print('\n2.2 查找提交按钮...')
    result = await operator.find_submit_button()
    if result['success']:
        print(f'✅ 找到提交按钮')
        print(f'   禁用: {result.get("disabled")}')
        print(f'   文本: "{result.get("text")}"')
    else:
        print(f'❌ {result.get("error")}')
    
    # 2.3 判断是否正在工作
    print('\n2.3 判断 Agent 是否正在工作...')
    result = await operator.is_agent_working()
    print(f'   正在工作: {result.get("isWorking")}')
    print(f'   指示器: {result.get("indicators")}')
    
    # 2.4 检查错误
    print('\n2.4 检查错误...')
    result = await operator.check_error()
    print(f'   有错误: {result.get("hasError")}')
    if result.get("hasError"):
        print(f'   错误信息: {result.get("error")}')
    
    print()
    print('=' * 70)
    print('  ✅ 快速测试完成')
    print('=' * 70)
    print()
    
    if operator.ws:
        await operator.ws.close()


if __name__ == '__main__':
    asyncio.run(main())

