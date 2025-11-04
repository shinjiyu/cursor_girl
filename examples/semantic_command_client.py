#!/usr/bin/env python3
"""
语义命令客户端示例

演示如何使用高层次语义接口：agent_execute_prompt
这个命令会完成完整的操作流程：输入 → 提交 → 执行
"""

import asyncio
import websockets
import json
import sys
import os

# 添加 protocol.py 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge'))

from protocol import MessageBuilder, MessageType, ClientType, Platform


async def semantic_example():
    """语义操作示例"""
    
    print('=' * 70)
    print('  🎯 Ortensia 语义命令客户端示例')
    print('=' * 70)
    print()
    print('演示高层次语义接口：agent_execute_prompt')
    print('这个命令封装了完整的操作流程：')
    print('  1. 输入提示词到 Composer')
    print('  2. 提交执行（回车或点击按钮）')
    print('  3. 可选：等待执行完成')
    print()
    print('=' * 70)
    print()
    
    server_url = 'ws://localhost:8765'
    
    print(f'🔗 连接到中央Server: {server_url}')
    
    try:
        async with websockets.connect(server_url) as ws:
            print('✅ 已连接\n')
            
            # 注册为 Command Client
            print('📝 注册为 Command Client (ID: semantic-cc-001)')
            
            register_msg = MessageBuilder.register(
                from_id="semantic-cc-001",
                client_type=ClientType.COMMAND_CLIENT,
                platform=Platform.DARWIN,
                pid=os.getpid()
            )
            
            await ws.send(register_msg.to_json())
            print('✅ 注册消息已发送\n')
            
            # 等待注册确认
            print('👂 等待注册确认...')
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['type'] == 'register_ack' and response['payload']['success']:
                print(f'✅ 注册成功！')
                print(f'   🔑 分配ID: {response["payload"]["assigned_id"]}')
                print(f'   ℹ️  服务器信息: {response["payload"]["server_info"]}')
            else:
                print(f'❌ 注册失败')
                return False
            
            print()
            print('=' * 70)
            print('  🔍 查找可用的 Cursor 实例')
            print('=' * 70)
            print()
            
            # 等待一下，让 Cursor 有时间连接
            print('⏳ 等待 5 秒...')
            await asyncio.sleep(5)
            
            # 这里简化处理，假设已知 cursor_id
            # 实际应用中应该从 Server 获取已连接的 Cursor 列表
            cursor_id = input('请输入 Cursor ID（查看 Cursor 日志获取，或直接回车使用默认格式 cursor-XXXXX）: ')
            if not cursor_id:
                cursor_id = "cursor-" + str(os.getpid())  # 临时方案
                print(f'使用默认 ID: {cursor_id}')
            
            print()
            print('=' * 70)
            print('  🚀 演示 1: 输入并执行提示词（不等待完成）')
            print('=' * 70)
            print()
            
            prompt1 = "写一个 Python 函数计算斐波那契数列的第 n 项"
            
            print(f'💬 提示词: "{prompt1}"')
            print(f'📤 发送到: {cursor_id}')
            print(f'⚙️  选项: wait_for_completion=False')
            print()
            
            # 使用高层次语义接口
            execute_msg = MessageBuilder.agent_execute_prompt(
                from_id="semantic-cc-001",
                to_id=cursor_id,
                agent_id="default",
                prompt=prompt1,
                wait_for_completion=False,  # 不等待完成
                timeout=300000,             # 5 分钟
                clear_first=True            # 先清空输入框
            )
            
            await ws.send(execute_msg.to_json())
            print('✅ 命令已发送')
            print()
            
            # 等待响应
            print('👂 等待响应...')
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            print(f'📨 收到消息: {response["type"]}')
            
            if response['type'] == 'agent_execute_prompt_result':
                payload = response['payload']
                
                if payload['success']:
                    print()
                    print('✅ 操作成功！')
                    print(f'   阶段: {payload["phase"]}')
                    print(f'   消息: {payload.get("message")}')
                    print(f'   输入完成: {payload["input_completed"]}')
                    print(f'   提交完成: {payload["submit_completed"]}')
                else:
                    print()
                    print(f'❌ 操作失败')
                    print(f'   阶段: {payload["phase"]}')
                    print(f'   错误: {payload.get("error")}')
            
            print()
            print('💡 提示：因为 wait_for_completion=False，所以命令')
            print('   在提交后立即返回，不等待 Agent 执行完成。')
            print()
            
            # 等待用户查看效果
            input('按回车继续下一个演示...')
            
            print()
            print('=' * 70)
            print('  🚀 演示 2: 输入并执行提示词（等待完成）')
            print('=' * 70)
            print()
            
            prompt2 = "解释一下什么是装饰器模式"
            
            print(f'💬 提示词: "{prompt2}"')
            print(f'📤 发送到: {cursor_id}')
            print(f'⚙️  选项: wait_for_completion=True')
            print(f'⏱️  超时: 60 秒')
            print()
            
            # 使用高层次语义接口（等待完成）
            execute_msg = MessageBuilder.agent_execute_prompt(
                from_id="semantic-cc-001",
                to_id=cursor_id,
                agent_id="default",
                prompt=prompt2,
                wait_for_completion=True,   # 等待完成
                timeout=60000,              # 60 秒
                clear_first=True
            )
            
            await ws.send(execute_msg.to_json())
            print('✅ 命令已发送')
            print('⏳ 等待执行完成（最多 60 秒）...')
            print()
            
            # 等待响应（可能需要较长时间）
            try:
                response_str = await asyncio.wait_for(ws.recv(), timeout=65)
                response = json.loads(response_str)
                
                print(f'📨 收到消息: {response["type"]}')
                
                if response['type'] == 'agent_execute_prompt_result':
                    payload = response['payload']
                    
                    if payload['success']:
                        print()
                        print('✅ 执行完成！')
                        print(f'   阶段: {payload["phase"]}')
                        print(f'   消息: {payload.get("message")}')
                        print(f'   执行时间: {payload.get("execution_time")} ms')
                        print(f'   最终状态: {payload.get("status")}')
                    else:
                        print()
                        print(f'❌ 执行失败')
                        print(f'   阶段: {payload["phase"]}')
                        print(f'   错误: {payload.get("error")}')
                        
            except asyncio.TimeoutError:
                print()
                print('⚠️  等待超时（65 秒）')
            
            print()
            print('💡 提示：因为 wait_for_completion=True，所以命令')
            print('   会等待 Agent 执行完成后才返回。')
            print()
            
            # 等待用户查看效果
            input('按回车继续下一个演示...')
            
            print()
            print('=' * 70)
            print('  🚀 演示 3: 停止 Agent 执行')
            print('=' * 70)
            print()
            
            # 先发送一个长任务
            long_prompt = "详细分析 Python 的 GIL（全局解释器锁）的实现原理和影响"
            
            print(f'💬 提示词: "{long_prompt}"')
            print(f'📤 发送到: {cursor_id}')
            print(f'⚙️  选项: wait_for_completion=False')
            print()
            
            execute_msg = MessageBuilder.agent_execute_prompt(
                from_id="semantic-cc-001",
                to_id=cursor_id,
                agent_id="default",
                prompt=long_prompt,
                wait_for_completion=False,
                timeout=300000,
                clear_first=True
            )
            
            await ws.send(execute_msg.to_json())
            print('✅ 长任务已发送')
            
            # 等待响应
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['type'] == 'agent_execute_prompt_result':
                if response['payload']['success']:
                    print('✅ 任务已提交')
            
            print()
            print('⏳ 等待 3 秒，让 Agent 开始执行...')
            await asyncio.sleep(3)
            
            print()
            print('🛑 现在发送停止指令...')
            
            # 发送停止指令
            stop_msg = MessageBuilder.agent_stop_execution(
                from_id="semantic-cc-001",
                to_id=cursor_id,
                agent_id="default",
                reason="用户演示停止功能"
            )
            
            await ws.send(stop_msg.to_json())
            print('✅ 停止指令已发送')
            print()
            
            # 等待响应
            print('👂 等待响应...')
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['type'] == 'agent_stop_execution_result':
                payload = response['payload']
                
                if payload['success']:
                    print('✅ 停止成功')
                    print(f'   消息: {payload.get("message")}')
                else:
                    print('❌ 停止失败')
                    print(f'   错误: {payload.get("error")}')
            
            print()
            print('=' * 70)
            print('  ✅ 所有演示完成！')
            print('=' * 70)
            print()
            
            print('📝 总结：')
            print('  1. agent_execute_prompt - 完整的语义操作')
            print('     • 封装了输入、提交、执行的完整流程')
            print('     • 可选择是否等待执行完成')
            print('     • 返回详细的执行状态')
            print()
            print('  2. agent_stop_execution - 停止 Agent')
            print('     • 可以中断正在执行的任务')
            print('     • 适用于长时间运行的任务')
            print()
            print('  3. 对比底层操作（composer_send_prompt）：')
            print('     • 底层：只负责输入文字到输入框')
            print('     • 语义：完成输入+提交+执行的完整流程')
            print()
            
            return True
    
    except ConnectionRefusedError:
        print('❌ 连接被拒绝')
        print('💡 请确保中央Server正在运行:')
        print('   python3 bridge/websocket_server.py')
        return False
    
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await semantic_example()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  演示被中断')
        sys.exit(1)

