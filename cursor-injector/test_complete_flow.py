#!/usr/bin/env python3
"""
完整流程测试：输入 → 提交 → 等待完成

使用更新后的 composer_operations.py，验证所有新功能：
1. 确保在 Editor tab
2. Cmd+I 唤出 Composer（如果需要）
3. 输入文字
4. 点击上箭头按钮提交
5. 等待执行完成
"""

import asyncio
from composer_operations import ComposerOperator


async def test_complete_flow():
    """测试完整流程"""
    operator = ComposerOperator()
    await operator.connect()
    
    print('=' * 70)
    print('  🧪 完整流程测试')
    print('=' * 70)
    print()
    
    # 测试 1: 不等待完成
    print('【测试 1】执行提示词（不等待完成）')
    print('─' * 70)
    result1 = await operator.execute_prompt(
        prompt="用 Python 实现快速排序算法",
        wait_for_completion=False
    )
    
    if result1['success']:
        print('✅ 测试 1 通过：提示词已成功提交')
    else:
        print(f'❌ 测试 1 失败：{result1.get("error")}')
        return
    
    print()
    print('─' * 70)
    input('按回车继续测试 2（等待上一个任务完成）...')
    print()
    
    # 等待上一个任务完成
    print('⏳ 等待上一个任务完成...')
    wait_result = await operator.wait_for_completion(timeout=60)
    
    if wait_result['success']:
        print(f'✅ 任务已完成（耗时 {wait_result["elapsed"]:.1f} 秒）')
    else:
        print(f'⚠️  任务未完成或出错：{wait_result.get("error")}')
    
    print()
    print('─' * 70)
    input('按回车继续测试 2（等待完成模式）...')
    print()
    
    # 测试 2: 等待完成
    print('【测试 2】执行提示词（等待完成）')
    print('─' * 70)
    result2 = await operator.execute_prompt(
        prompt="解释一下二分查找的时间复杂度",
        wait_for_completion=True,
        timeout=60
    )
    
    if result2['success']:
        print('✅ 测试 2 通过：提示词执行完成')
    else:
        print(f'❌ 测试 2 失败：{result2.get("error")}')
    
    print()
    print('=' * 70)
    print('  ✅ 所有测试完成')
    print('=' * 70)


async def test_individual_functions():
    """测试单个功能"""
    operator = ComposerOperator()
    await operator.connect()
    
    print('=' * 70)
    print('  🧪 单个功能测试')
    print('=' * 70)
    print()
    
    # 测试 1: ensure_editor_tab
    print('【测试 1】确保在 Editor tab')
    print('─' * 70)
    result = await operator.ensure_editor_tab()
    print(f'结果: {result}')
    print()
    
    # 测试 2: ensure_composer_ready
    print('【测试 2】确保 Composer 就绪')
    print('─' * 70)
    result = await operator.ensure_composer_ready()
    print(f'结果: {result}')
    print()
    
    # 测试 3: find_input
    print('【测试 3】查找输入框')
    print('─' * 70)
    result = await operator.find_input()
    print(f'结果: {result}')
    print()
    
    # 测试 4: input_text
    print('【测试 4】输入测试文字')
    print('─' * 70)
    result = await operator.input_text("测试输入", clear_first=True)
    print(f'结果: {result}')
    print()
    
    # 等待按钮出现
    await asyncio.sleep(0.5)
    
    # 测试 5: find_submit_button
    print('【测试 5】查找提交按钮')
    print('─' * 70)
    result = await operator.find_submit_button()
    print(f'结果: {result}')
    print()
    
    # 测试 6: wait_for_submit_button
    print('【测试 6】等待提交按钮出现')
    print('─' * 70)
    result = await operator.wait_for_submit_button(timeout=5)
    print(f'结果: {result}')
    print()
    
    # 测试 7: is_agent_working
    print('【测试 7】检查 Agent 是否正在工作')
    print('─' * 70)
    result = await operator.is_agent_working()
    print(f'结果: {result}')
    print()
    
    print('=' * 70)
    print('  ✅ 所有单个功能测试完成')
    print('=' * 70)


async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--individual':
        # 测试单个功能
        await test_individual_functions()
    else:
        # 测试完整流程
        await test_complete_flow()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  测试被中断')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()

