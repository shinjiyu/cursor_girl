#!/usr/bin/env python3
"""
测试固定的萝莉音色
"""

import asyncio
import websockets
import json
import time


async def test_fixed_voice():
    print("🎀 测试固定萝莉音色 (seed=1234)")
    print()
    
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "voice-test-client",
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
        
        # 发送3条测试消息，验证音色一致性
        test_messages = [
            "欧尼酱，我回来啦！今天过得怎么样呀？",
            "嘿嘿，我发现了一个超级有趣的东西哦！",
            "嗯嗯，我知道了！交给我吧，一定会做好的！",
        ]
        
        for i, text in enumerate(test_messages, 1):
            print(f"[{i}/3] 发送: {text}")
            
            msg = {
                "type": "aituber_receive_text",
                "from": "voice-test-client",
                "to": "aituber",
                "timestamp": int(time.time() * 1000),
                "payload": {
                    "text": text,
                    "emotion": "happy",
                    "conversation_id": "voice-consistency-test"
                }
            }
            
            await websocket.send(json.dumps(msg))
            print(f"   ✅ 已发送，等待生成...")
            await asyncio.sleep(10)
            print()
        
        print("=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        print()
        print("📊 验证结果:")
        print("   1. 三段语音应该是同一个声音（萝莉音）")
        print("   2. 音色甜美可爱，音调较高")
        print("   3. 每次生成的音色都一致")
        print()
        print("🎧 播放音频验证:")
        print("   ls -lt bridge/tts_output/*.wav | head -3")
        print()


if __name__ == "__main__":
    asyncio.run(test_fixed_voice())
























