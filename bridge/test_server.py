#!/usr/bin/env python3
"""
测试中央Server基本功能
"""

import asyncio
import websockets
import json
import sys
import os

# 添加 protocol.py 到路径
sys.path.insert(0, os.path.dirname(__file__))

from protocol import MessageBuilder, MessageType, ClientType, Platform


async def test_server():
    """测试服务器连接和基本功能"""
    
    print('=' * 70)
    print('  🧪 测试中央 WebSocket Server')
    print('=' * 70)
    print()
    
    server_url = 'ws://localhost:8765'
    
    print(f'📡 连接到 {server_url}...')
    
    try:
        async with websockets.connect(server_url) as ws:
            print('✅ 连接成功\n')
            
            # 测试 1: 注册
            print('━' * 70)
            print('  测试 1: 注册为 Command Client')
            print('━' * 70)
            
            register_msg = MessageBuilder.register(
                from_id="test-cc-001",
                client_type=ClientType.COMMAND_CLIENT,
                platform=Platform.DARWIN,
                pid=os.getpid()
            )
            
            await ws.send(register_msg.to_json())
            print('📤 注册消息已发送')
            
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            print(f'📨 收到响应: {response["type"]}')
            
            if response['type'] == 'register_ack':
                if response['payload']['success']:
                    print(f'✅ 注册成功: {response["payload"]["assigned_id"]}')
                    print(f'   服务器信息: {response["payload"]["server_info"]}')
                else:
                    print(f'❌ 注册失败: {response["payload"]["error"]}')
                    return False
            else:
                print(f'❌ 收到意外响应类型: {response["type"]}')
                return False
            
            print()
            
            # 测试 2: 心跳
            print('━' * 70)
            print('  测试 2: 心跳')
            print('━' * 70)
            
            heartbeat_msg = MessageBuilder.heartbeat("test-cc-001")
            await ws.send(heartbeat_msg.to_json())
            print('📤 心跳消息已发送')
            
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['type'] == 'heartbeat_ack':
                print(f'✅ 收到心跳响应')
                print(f'   服务器时间: {response["payload"]["server_time"]}')
            else:
                print(f'❌ 收到意外响应: {response["type"]}')
            
            print()
            
            # 测试 3: 发送命令到不存在的 Cursor
            print('━' * 70)
            print('  测试 3: 发送命令到不存在的 Cursor')
            print('━' * 70)
            
            prompt_msg = MessageBuilder.composer_send_prompt(
                from_id="test-cc-001",
                to_id="cursor-nonexistent",
                agent_id="default",
                prompt="测试提示词"
            )
            
            await ws.send(prompt_msg.to_json())
            print('📤 命令已发送到 cursor-nonexistent')
            
            # 应该收到错误响应
            response_str = await asyncio.wait_for(ws.recv(), timeout=2.0)
            response = json.loads(response_str)
            
            if response['type'] == 'composer_send_prompt_result':
                if not response['payload']['success']:
                    print(f'✅ 正确收到错误响应')
                    print(f'   错误信息: {response["payload"]["error"]}')
                else:
                    print(f'❌ 不应该成功')
            else:
                print(f'⚠️  收到其他响应: {response["type"]}')
            
            print()
            
            # 测试完成
            print('=' * 70)
            print('  ✅ 所有测试通过！')
            print('=' * 70)
            print()
            
            return True
    
    except ConnectionRefusedError:
        print('❌ 连接被拒绝')
        print('💡 请确保中央Server正在运行:')
        print('   python3 bridge/websocket_server.py')
        return False
    
    except asyncio.TimeoutError:
        print('❌ 超时')
        return False
    
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_server()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  测试被中断')
        sys.exit(1)

