#!/usr/bin/env python3
"""
测试 AITuber Kit 与中央服务器的集成

测试流程:
1. 连接到中央服务器
2. 发送消息给 AITuber
3. 接收 AITuber 的响应
"""

import asyncio
import json
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge'))

from websocket_client import WebSocketClient
from protocol import MessageBuilder, ClientType, Platform, MessageType


async def test_aituber_integration():
    """测试 AITuber 集成"""
    print("=" * 70)
    print("  🌸 测试 AITuber Kit 与中央服务器集成")
    print("=" * 70)
    print()
    
    # 创建客户端
    client = WebSocketClient("ws://localhost:8765")
    
    try:
        # 1. 连接到服务器
        print("📡 步骤 1: 连接到中央服务器...")
        await client.connect()
        print("✅ 已连接")
        print()
        
        # 2. 注册为 Command Client
        print("📝 步骤 2: 注册客户端...")
        register_msg = MessageBuilder.register(
            client_id="test-command-client",
            client_type=ClientType.COMMAND_CLIENT,
            platform=Platform.DARWIN,
            pid=os.getpid(),
            version="1.0.0"
        )
        
        await client.send_message(register_msg)
        
        # 等待注册响应
        response = await client.receive_message(timeout=5.0)
        if response and response.type == MessageType.REGISTER_ACK:
            print(f"✅ 注册成功: {response.payload}")
        else:
            print(f"⚠️  注册响应: {response}")
        print()
        
        # 3. 发送消息给 AITuber
        print("📤 步骤 3: 发送文本消息给 AITuber...")
        
        # 构造 AITuber 消息
        aituber_msg = {
            "type": MessageType.AITUBER_RECEIVE_TEXT.value,
            "from": "test-command-client",
            "to": "aituber-*",  # 发送给所有 AITuber 客户端
            "timestamp": int(asyncio.get_event_loop().time() * 1000),
            "payload": {
                "text": "你好！这是来自测试的消息。",
                "role": "user",
                "emotion": "happy",
                "type": "text"
            }
        }
        
        await client.ws.send(json.dumps(aituber_msg))
        print("✅ 消息已发送")
        print()
        
        # 4. 等待 AITuber 响应
        print("⏳ 步骤 4: 等待 AITuber 响应...")
        print("   （请确保 AITuber Kit 正在运行并已启用外部联动模式）")
        print()
        
        try:
            # 等待 10 秒接收响应
            response = await client.receive_message(timeout=10.0)
            if response:
                print(f"📨 收到响应: {response.type}")
                print(f"   内容: {response.payload}")
            else:
                print("⚠️  未收到响应（可能 AITuber 未连接或未启用外部联动）")
        except asyncio.TimeoutError:
            print("⏱️  响应超时（这是正常的，AITuber 可能没有回复功能）")
        
        print()
        print("=" * 70)
        print("  ✅ 测试完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 断开连接
        if client.ws:
            await client.disconnect()


async def test_check_aituber_connected():
    """检查 AITuber 是否已连接"""
    print("=" * 70)
    print("  🔍 检查 AITuber 客户端连接状态")
    print("=" * 70)
    print()
    
    client = WebSocketClient("ws://localhost:8765")
    
    try:
        await client.connect()
        
        # 注册
        register_msg = MessageBuilder.register(
            client_id="test-checker",
            client_type=ClientType.COMMAND_CLIENT,
            platform=Platform.DARWIN,
            pid=os.getpid(),
            version="1.0.0"
        )
        await client.send_message(register_msg)
        await client.receive_message(timeout=3.0)
        
        print("✅ 已连接到中央服务器")
        print()
        print("💡 提示:")
        print("   - 请在 AITuber Kit 中启用'外部联动模式'")
        print("   - 检查浏览器控制台是否显示'Ortensia 连接成功'")
        print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        if client.ws:
            await client.disconnect()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试 AITuber Kit 集成')
    parser.add_argument('--check', action='store_true', help='只检查连接状态')
    args = parser.parse_args()
    
    if args.check:
        asyncio.run(test_check_aituber_connected())
    else:
        asyncio.run(test_aituber_integration())

