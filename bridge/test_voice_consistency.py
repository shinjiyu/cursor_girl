#!/usr/bin/env python3
"""
测试音色一致性
验证修复后，每次生成的声音是否一致
"""

import asyncio
import websockets
import json
import time


async def test_consistency():
    print("=" * 60)
    print("🎤 音色一致性测试")
    print("=" * 60)
    print()
    print("📋 测试目标:")
    print("   生成 5 次相同文本，验证音色是否完全一致")
    print("   ✅ 成功标准: 所有音频都是同样的女声/萝莉音")
    print("   ❌ 失败标准: 出现男声或不同的女声")
    print()
    
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "consistency-test-client",
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
        print("✅ 已连接到服务器")
        print()
        
        # 测试文本 - 简单且能明显区分男女声
        test_text = "你好，我是オルテンシア。这是音色一致性测试。"
        
        print(f"📝 测试文本: {test_text}")
        print(f"🎯 固定 seed: 1234")
        print()
        
        # 生成 5 次
        for i in range(1, 6):
            print(f"[{i}/5] 生成第 {i} 次...")
            
            msg = {
                "type": "aituber_receive_text",
                "from": "consistency-test-client",
                "to": "aituber",
                "timestamp": int(time.time() * 1000),
                "payload": {
                    "text": test_text,
                    "emotion": "neutral",
                    "conversation_id": f"consistency-test-{i}"
                }
            }
            
            await websocket.send(json.dumps(msg))
            print(f"   ✅ 已发送，等待生成...")
            await asyncio.sleep(8)
            print()
        
        print("=" * 60)
        print("✅ 生成完成！")
        print("=" * 60)
        print()
        print("🎧 验证方法:")
        print("   1. 播放所有音频，听听是否是同一个声音")
        print("   2. 检查音频文件大小是否相近（相同文本应该差不多）")
        print()
        print("📁 查看文件:")
        print("   ls -lht bridge/tts_output/*.wav | head -5")
        print()
        print("🔊 逐个播放:")
        for i in range(1, 6):
            print(f"   # 第 {i} 次生成")
            print(f"   afplay bridge/tts_output/<filename>.wav")
        print()
        print("💡 判断标准:")
        print("   ✅ 如果 5 次都是同样的萝莉音 → 修复成功！")
        print("   ❌ 如果出现男声或不同女声 → 还需调试")
        print()


if __name__ == "__main__":
    asyncio.run(test_consistency())
























