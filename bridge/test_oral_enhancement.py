#!/usr/bin/env python3
"""
测试 oral 标签优化效果
对比优化前后的差异
"""

import asyncio
import websockets
import json
import time


async def test_oral_enhancement():
    print("🎀 测试社区推荐的 oral 标签优化")
    print("=" * 60)
    print()
    
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "oral-test-client",
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
        
        # 测试不同情感的 oral 级别
        test_cases = [
            {
                "text": "欧尼酱，我回来啦！今天过得很开心哦！",
                "emotion": "happy",
                "expected_oral": "[oral_6]",
                "delay": 10
            },
            {
                "text": "哇！这个太厉害了！我超级兴奋！",
                "emotion": "excited",
                "expected_oral": "[oral_7]",
                "delay": 10
            },
            {
                "text": "嗯...今天有点不开心呢...",
                "emotion": "sad",
                "expected_oral": "[oral_3]",
                "delay": 10
            },
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] 测试情感: {test['emotion']}")
            print(f"   文本: {test['text']}")
            print(f"   预期标签: {test['expected_oral']}")
            
            msg = {
                "type": "aituber_receive_text",
                "from": "oral-test-client",
                "to": "aituber",
                "timestamp": int(time.time() * 1000),
                "payload": {
                    "text": test['text'],
                    "emotion": test['emotion'],
                    "conversation_id": "oral-enhancement-test"
                }
            }
            
            await websocket.send(json.dumps(msg))
            print(f"   ✅ 已发送，等待生成...")
            await asyncio.sleep(test['delay'])
            print()
        
        print("=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        print()
        print("🎧 播放测试音频:")
        print("   happy:   oral_6 + laugh (最萌)")
        print("   excited: oral_7 + laugh + speed (超元气)")
        print("   sad:     oral_3 + uv_break (柔和)")
        print()
        print("📊 对比原来的效果:")
        print("   原来: 只有情感标签")
        print("   现在: oral 标签 + 情感标签 (更自然更萌)")
        print()


if __name__ == "__main__":
    asyncio.run(test_oral_enhancement())
























