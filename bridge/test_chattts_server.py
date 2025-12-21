#!/usr/bin/env python3
"""
测试 WebSocket 服务器的 ChatTTS 功能
"""

import asyncio
import websockets
import json
import time


async def test_chattts():
    print("=" * 60)
    print("🎤 测试 ChatTTS 集成")
    print("=" * 60)
    print()
    
    # 连接到服务器
    uri = "ws://localhost:8765"
    print(f"1. 连接到服务器: {uri}")
    
    async with websockets.connect(uri) as websocket:
        print("✅ 连接成功")
        print()
        
        # 注册为命令客户端
        print("2. 注册为命令客户端...")
        register_msg = {
            "type": "register",
            "from": "test-client-chattts",
            "to": "server",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "client_types": ["command_client"],
                "platform": "darwin",
                "pid": 0,
                "version": "1.0.0"
            }
        }
        
        await websocket.send(json.dumps(register_msg))
        
        # 等待注册响应
        response = await websocket.recv()
        resp_data = json.loads(response)
        print(f"✅ 注册响应: {resp_data['type']}")
        print()
        
        # 发送测试消息（会触发 TTS）
        print("3. 发送测试消息...")
        test_msg = {
            "type": "aituber_receive_text",
            "from": "test-client-chattts",
            "to": "aituber",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "text": "你好，这是一个 ChatTTS 测试。今天天气很好！",
                "emotion": "happy",
                "conversation_id": "test-conversation"
            }
        }
        
        await websocket.send(json.dumps(test_msg))
        print("✅ 消息已发送")
        print()
        
        print("4. 等待服务器处理...")
        print("   （服务器会生成 TTS 音频）")
        
        # 等待一段时间让服务器处理
        await asyncio.sleep(8)
        
        print()
        print("5. 检查服务器日志...")
        print("   执行: tail -50 /tmp/ws_server.log")
        print()
        
    print("=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print()
    print("检查结果:")
    print("  1. 查看日志: tail -f /tmp/ws_server.log")
    print("  2. 检查生成的音频文件: ls -lh bridge/tts_output/")
    print()


if __name__ == "__main__":
    asyncio.run(test_chattts())






















