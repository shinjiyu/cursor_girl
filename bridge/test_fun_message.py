#!/usr/bin/env python3
"""
发送一条有趣的消息测试 ChatTTS
"""

import asyncio
import websockets
import json
import time


async def send_fun_message():
    print("🎤 发送有趣的测试消息...")
    print()
    
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "fun-test-client",
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
        
        # 测试不同情感的消息
        messages = [
            {
                "text": "哈哈，太有意思了！我现在可以用 ChatTTS 说话啦！声音听起来是不是很自然呢？",
                "emotion": "excited",
                "delay": 12
            },
            {
                "text": "嗯，让我想想。今天的天气真不错，我们可以一起做些有趣的事情。比如写代码、调试程序，或者优化性能！",
                "emotion": "calm",
                "delay": 15
            },
            {
                "text": "哇！真是太棒了！新的 ChatTTS 引擎音质超级好，而且还支持情感控制。这比之前的 macOS TTS 强太多了！",
                "emotion": "happy",
                "delay": 15
            }
        ]
        
        for i, msg_data in enumerate(messages, 1):
            print(f"{i}. 发送消息: {msg_data['text'][:30]}...")
            print(f"   情感: {msg_data['emotion']}")
            
            test_msg = {
                "type": "aituber_receive_text",
                "from": "fun-test-client",
                "to": "aituber",
                "timestamp": int(time.time() * 1000),
                "payload": {
                    "text": msg_data["text"],
                    "emotion": msg_data["emotion"],
                    "conversation_id": "fun-test"
                }
            }
            
            await websocket.send(json.dumps(test_msg))
            print(f"   ✅ 已发送，等待生成...")
            
            # 等待 TTS 生成
            await asyncio.sleep(msg_data["delay"])
            print()
        
        print("=" * 60)
        print("✅ 所有消息已发送！")
        print("=" * 60)
        print()
        print("查看生成的文件:")
        print("  ls -lht bridge/tts_output/ | head -5")
        print()
        print("播放最新的音频:")
        print("  afplay bridge/tts_output/$(ls -t bridge/tts_output/ | head -1)")
        print()


if __name__ == "__main__":
    asyncio.run(send_fun_message())






















