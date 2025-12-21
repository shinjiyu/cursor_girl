#!/usr/bin/env python3
"""快速测试 TTS 修复"""

import asyncio
import websockets
import json
import time


async def test():
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "tts-fix-test",
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
        await websocket.recv()
        print("✅ 已连接")
        
        # 发送测试消息
        msg = {
            "type": "aituber_receive_text",
            "from": "tts-fix-test",
            "to": "aituber",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "text": "测试音色修复，这是第一次生成。",
                "emotion": "neutral",
                "conversation_id": "tts-fix-test-1"
            }
        }
        
        await websocket.send(json.dumps(msg))
        print("✅ 已发送测试消息，等待 TTS 生成...")
        await asyncio.sleep(8)
        
        # 再发送一次
        msg["payload"]["text"] = "第二次生成，音色应该和第一次一样。"
        msg["payload"]["conversation_id"] = "tts-fix-test-2"
        await websocket.send(json.dumps(msg))
        print("✅ 已发送第二条消息")
        await asyncio.sleep(8)


if __name__ == "__main__":
    asyncio.run(test())






















