#!/usr/bin/env python3
"""
测试 Conversation ID 协议 (V10)

测试内容：
1. 向 inject 发送 get_conversation_id 请求
2. 接收并解析响应
3. 验证 conversation_id 格式
4. 演示 Hook 如何使用这个 ID
"""

import asyncio
import json
import websockets


async def test_get_conversation_id():
    """测试获取 conversation_id"""
    
    print("=" * 80)
    print("🧪 测试 Conversation ID 协议 (V10)")
    print("=" * 80)
    print()
    
    try:
        # 连接到本地 inject
        print("📡 连接到 inject (ws://localhost:9876)...")
        async with websockets.connect('ws://localhost:9876') as ws:
            print("✅ 已连接")
            print()
            
            # 构造获取 conversation_id 的 JS 代码
            # 这模拟服务器向 inject 发送 get_conversation_id 请求
            code = """
            (async () => {
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                
                if (windows.length === 0) {
                    return JSON.stringify({ 
                        success: false, 
                        error: 'No windows' 
                    });
                }
                
                const result = await windows[0].webContents.executeJavaScript(`
                    (() => {
                        const el = document.querySelector('[id^="composer-bottom-add-context-"]');
                        if (!el) {
                            return JSON.stringify({ found: false });
                        }
                        
                        const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                        return JSON.stringify({
                            found: true,
                            conversation_id: match ? match[1] : null
                        });
                    })()
                `);
                
                return result;
            })()
            """
            
            print("📤 发送请求: get_conversation_id")
            await ws.send(code)
            
            print("⏳ 等待响应...")
            response = await ws.recv()
            
            print("✅ 收到响应")
            print()
            
            # 解析响应
            response_data = json.loads(response)
            
            if not response_data.get('success'):
                print(f"❌ 执行失败: {response_data.get('error')}")
                return
            
            result_str = response_data.get('result', '{}')
            result = json.loads(result_str)
            
            print("=" * 80)
            print("📊 响应内容")
            print("=" * 80)
            print()
            
            if not result.get('found'):
                print("⚠️  未找到当前对话")
                print("   可能原因：")
                print("   - 没有打开的对话")
                print("   - Composer 未激活")
                return
            
            conversation_id = result.get('conversation_id')
            
            print(f"✅ Conversation ID: {conversation_id}")
            print()
            
            # 验证格式
            print("🔍 验证格式")
            print("-" * 80)
            
            if not conversation_id:
                print("❌ ID 为空")
                return
            
            # UUID 格式: 8-4-4-4-12
            parts = conversation_id.split('-')
            if len(parts) == 5:
                lengths = [len(p) for p in parts]
                if lengths == [8, 4, 4, 4, 12]:
                    print("✅ 格式正确: 标准 UUID (8-4-4-4-12)")
                else:
                    print(f"⚠️  格式异常: {lengths}")
            else:
                print(f"⚠️  不是标准 UUID 格式: {len(parts)} 部分")
            
            print()
            
            # 演示 Hook 如何使用
            print("=" * 80)
            print("💡 Hook 使用示例")
            print("=" * 80)
            print()
            
            hook_id = f"hook-{conversation_id}"
            print(f"Hook ID: {hook_id}")
            print()
            
            print("Hook 发送消息示例:")
            print("-" * 80)
            
            message = {
                "type": "aituber_receive_text",
                "from": hook_id,
                "to": "aituber",
                "timestamp": int(asyncio.get_event_loop().time() * 1000),
                "payload": {
                    "text": "这是一条测试消息",
                    "emotion": "neutral",
                    "source": "hook",
                    "hook_name": "test",
                    "conversation_id": conversation_id
                }
            }
            
            print(json.dumps(message, indent=2, ensure_ascii=False))
            print()
            
            # 演示服务器如何关联
            print("=" * 80)
            print("🔗 服务器关联示例")
            print("=" * 80)
            print()
            
            print("步骤 1: Hook 发送消息，from='hook-{conversation_id}'")
            print(f"        Hook ID: {hook_id}")
            print()
            
            print("步骤 2: 服务器提取 conversation_id")
            print(f"        提取: {hook_id} → {conversation_id}")
            print()
            
            print("步骤 3: 服务器查询所有 inject 的 conversation_id")
            print("        (通过 get_conversation_id 协议)")
            print()
            
            print("步骤 4: 匹配并建立映射")
            print(f"        conversation_to_inject['{conversation_id}'] = 'inject-{12345}'")
            print()
            
            print("步骤 5: 后续消息直接使用缓存的映射")
            print()
            
            print("=" * 80)
            print("✅ 测试完成")
            print("=" * 80)
            
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket 错误: {e}")
        print()
        print("请确保：")
        print("  1. Cursor 已启动")
        print("  2. Inject V10 已安装")
        print("  3. 本地 Server 在运行 (ws://localhost:9876)")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def test_hook_id_generation():
    """测试 Hook ID 生成逻辑"""
    
    print()
    print("=" * 80)
    print("🧪 测试 Hook ID 生成逻辑")
    print("=" * 80)
    print()
    
    # 模拟不同的输入情况
    test_cases = [
        {
            "name": "正常情况",
            "conversation_id": "2d8f9386-9864-4a51-b089-a7342029bb41",
            "expected": "hook-2d8f9386-9864-4a51-b089-a7342029bb41"
        },
        {
            "name": "没有 conversation_id",
            "conversation_id": None,
            "workspace": "/Users/user/project",
            "expected": "hook-{workspace_hash}"
        },
        {
            "name": "conversation_id 为 unknown",
            "conversation_id": "unknown",
            "workspace": "/Users/user/project",
            "expected": "hook-{workspace_hash}"
        }
    ]
    
    for test in test_cases:
        print(f"测试用例: {test['name']}")
        print("-" * 80)
        
        conversation_id = test.get('conversation_id')
        
        if conversation_id and conversation_id != 'unknown':
            client_id = f"hook-{conversation_id}"
            print(f"  Conversation ID: {conversation_id}")
            print(f"  Hook ID: {client_id}")
            
            if client_id == test['expected']:
                print("  ✅ 符合预期")
            else:
                print(f"  ⚠️  预期: {test['expected']}")
        else:
            import hashlib
            workspace = test.get('workspace', 'unknown')
            workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:8]
            client_id = f"hook-{workspace_hash}"
            
            print(f"  Conversation ID: {conversation_id or '(未提供)'}")
            print(f"  Workspace: {workspace}")
            print(f"  Workspace Hash: {workspace_hash}")
            print(f"  Hook ID: {client_id}")
            print(f"  ✅ 使用备用方案")
        
        print()


if __name__ == "__main__":
    print()
    print("💡 Conversation ID 协议测试工具 (V10)")
    print()
    
    try:
        # 测试 1: 获取 conversation_id
        asyncio.run(test_get_conversation_id())
        
        # 测试 2: Hook ID 生成
        asyncio.run(test_hook_id_generation())
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

