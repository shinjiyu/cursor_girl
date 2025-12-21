#!/usr/bin/env python3
"""
测试 AGENT_COMPLETED 事件
模拟 hook 发送事件到 WebSocket 服务器
"""

import asyncio
import websockets
import json
import time

async def test_agent_completed():
    """测试发送 AGENT_COMPLETED 事件"""
    
    # 测试数据
    conversation_id = "e595bde3-bcc4-4bb4-9ebc-0cadf0cbd6da"
    client_id = f"hook-{conversation_id}"
    ws_server = "ws://localhost:8765"
    
    print(f"🔧 测试发送 AGENT_COMPLETED 事件")
    print(f"   Conversation ID: {conversation_id}")
    print(f"   Client ID: {client_id}")
    print(f"   WebSocket Server: {ws_server}")
    print()
    
    try:
        async with websockets.connect(ws_server, open_timeout=2, close_timeout=1) as websocket:
            print("✅ WebSocket 已连接")
            
            # 1. 注册
            register_msg = {
                "type": "register",
                "from": client_id,
                "to": None,
                "timestamp": int(time.time() * 1000),
                "payload": {"client_type": "agent_hook"}
            }
            await websocket.send(json.dumps(register_msg))
            print(f"📤 已发送注册消息")
            
            # 接收注册确认
            response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
            print(f"📨 收到响应: {response}")
            
            # 2. 发送 AGENT_COMPLETED 事件
            event_msg = {
                "type": "agent_completed",
                "from": client_id,
                "to": "",  # 广播
                "timestamp": int(time.time() * 1000),
                "payload": {
                    "agent_id": "default",
                    "result": "success",
                    "summary": "任务已完成"
                }
            }
            await websocket.send(json.dumps(event_msg))
            print(f"✅ AGENT_COMPLETED 事件已发送")
            print(f"   Event: {json.dumps(event_msg, indent=2)}")
            
            # 等待一下，看看是否有响应
            await asyncio.sleep(1)
            
    except asyncio.TimeoutError:
        print("❌ WebSocket 连接超时")
    except ConnectionRefusedError:
        print("❌ WebSocket 服务器未运行 (Connection refused)")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT_COMPLETED 事件测试")
    print("=" * 60)
    asyncio.run(test_agent_completed())
    print("=" * 60)






















