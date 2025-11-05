#!/usr/bin/env python3
"""快速测试中央服务器模式"""
import asyncio
import websockets
import json
import time

async def test():
    # 从日志中获取最新的 Cursor ID
    with open('/tmp/cursor_ortensia.log', 'r') as f:
        lines = f.readlines()
        cursor_id = None
        for line in reversed(lines):
            if 'Cursor ID:' in line:
                cursor_id = line.split('Cursor ID: ')[1].split()[0]
                break
    
    if not cursor_id:
        print("❌ 未找到 Cursor ID")
        return
    
    print(f"🔑 找到 Cursor ID: {cursor_id}")
    print(f"🔗 连接到中央服务器...")
    
    async with websockets.connect('ws://localhost:8765') as ws:
        print("✅ 已连接")
        
        # 注册为 Command Client
        client_id = "test-cc-001"
        register = {
            "type": "register",
            "from": client_id,
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_type": "command_client"
            }
        }
        
        print("📝 注册...")
        await ws.send(json.dumps(register))
        response = await ws.recv()
        print(f"✅ 注册成功: {json.loads(response)['type']}")
        
        # 发送命令
        print(f"\n📤 发送测试命令到 {cursor_id}...")
        command = {
            "type": "composer_send_prompt",
            "from": client_id,
            "to": cursor_id,
            "timestamp": int(time.time()),
            "payload": {
                "agent_id": "test-agent",
                "prompt": "写一个 Python 快速排序函数"
            }
        }
        
        await ws.send(json.dumps(command))
        print("⏳ 等待响应...")
        
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            result = json.loads(response)
            
            print(f"\n📬 收到响应:")
            print(f"   类型: {result['type']}")
            print(f"   来自: {result.get('from')}")
            
            if result['type'] == 'composer_send_prompt_result':
                payload = result['payload']
                if payload['success']:
                    print(f"   ✅ 成功: {payload['message']}")
                    print("\n" + "="*70)
                    print("  🎉 中央服务器模式测试成功！")
                    print("="*70)
                else:
                    print(f"   ❌ 失败: {payload['error']}")
            else:
                print(f"   收到的消息: {result}")
                
        except asyncio.TimeoutError:
            print("⚠️  30秒内未收到响应")

if __name__ == '__main__':
    asyncio.run(test())

