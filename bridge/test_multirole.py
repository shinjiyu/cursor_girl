#!/usr/bin/env python3
"""
测试多角色客户端注册

演示如何让一个客户端同时拥有多个角色（例如同时是 aituber 和 command_client）
"""

import asyncio
import websockets
import json
import time

SERVER_URL = "ws://localhost:8765"


async def test_single_role():
    """测试单角色注册（旧协议）"""
    print("\n" + "=" * 70)
    print("测试 1: 单角色注册（旧协议兼容）")
    print("=" * 70)
    
    async with websockets.connect(SERVER_URL) as ws:
        # 注册为 aituber_client
        register_msg = {
            "type": "register",
            "from": "test-single-role",
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_type": "aituber_client",  # ← 单角色（旧协议）
                "platform": "darwin",
                "pid": 99999
            }
        }
        
        await ws.send(json.dumps(register_msg))
        response = await ws.recv()
        result = json.loads(response)
        
        print(f"✅ 注册成功")
        print(f"   客户端 ID: {result['payload']['assigned_id']}")
        print(f"   角色: aituber_client（单角色）")
        
        await asyncio.sleep(1)


async def test_multiple_roles():
    """测试多角色注册（新协议）"""
    print("\n" + "=" * 70)
    print("测试 2: 多角色注册（新协议）")
    print("=" * 70)
    
    async with websockets.connect(SERVER_URL) as ws:
        # 注册为 aituber_client + command_client
        register_msg = {
            "type": "register",
            "from": "test-multi-role",
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_types": [  # ← 多角色列表（新协议）
                    "aituber_client",
                    "command_client"
                ],
                "platform": "darwin",
                "pid": 99998
            }
        }
        
        await ws.send(json.dumps(register_msg))
        response = await ws.recv()
        result = json.loads(response)
        
        print(f"✅ 注册成功")
        print(f"   客户端 ID: {result['payload']['assigned_id']}")
        print(f"   角色: aituber_client, command_client（多角色）")
        print(f"   服务器支持多角色: {result['payload']['server_info'].get('multi_role', False)}")
        
        await asyncio.sleep(1)


async def test_add_role():
    """测试添加角色（重复注册）"""
    print("\n" + "=" * 70)
    print("测试 3: 添加角色（重复注册同一客户端 ID）")
    print("=" * 70)
    
    async with websockets.connect(SERVER_URL) as ws:
        client_id = "test-add-role"
        
        # 第一次注册：只有 aituber_client
        register_msg_1 = {
            "type": "register",
            "from": client_id,
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_types": ["aituber_client"],
                "platform": "darwin",
                "pid": 99997
            }
        }
        
        await ws.send(json.dumps(register_msg_1))
        await ws.recv()
        print(f"✅ 第一次注册")
        print(f"   角色: [aituber_client]")
        
        await asyncio.sleep(1)
        
        # 第二次注册：添加 command_client 角色
        register_msg_2 = {
            "type": "register",
            "from": client_id,
            "to": "server",
            "timestamp": int(time.time()),
            "payload": {
                "client_types": ["command_client"],  # 添加新角色
                "platform": "darwin",
                "pid": 99997
            }
        }
        
        await ws.send(json.dumps(register_msg_2))
        await ws.recv()
        print(f"✅ 第二次注册（添加角色）")
        print(f"   角色: [aituber_client, command_client]")
        
        await asyncio.sleep(1)


async def main():
    """运行所有测试"""
    print("\n🌸 Ortensia 多角色客户端测试")
    print("=" * 70)
    
    try:
        await test_single_role()
        await test_multiple_roles()
        await test_add_role()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试完成！")
        print("=" * 70)
        print("\n请查看服务器日志，确认角色注册情况：")
        print("  tail -50 /tmp/ortensia_multirole.log | grep -E '(注册|角色)'")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())

