#!/usr/bin/env python3
"""
实际切换 Cursor 对话

演示对话切换功能：
1. 获取当前对话 ID
2. 打开 Chat History
3. 列出所有可用对话
4. 切换到另一个对话
5. 验证切换成功
"""

import asyncio
import json
import websockets
import time


async def execute_js(code):
    """通过 inject 执行 JS 代码"""
    try:
        async with websockets.connect('ws://localhost:9876') as ws:
            await ws.send(code)
            response = await ws.recv()
            result = json.loads(response)
            return result
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_current_conversation_id():
    """获取当前对话 ID"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return JSON.stringify({ error: 'No windows' });
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const el = document.querySelector('[id^="composer-bottom-add-context-"]');
                if (!el) return JSON.stringify({ error: 'Not found' });
                
                const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
                return JSON.stringify({
                    conversation_id: match ? match[1] : null
                });
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def open_history_panel():
    """打开 Chat History 面板"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const historyButton = document.querySelector('[aria-label*="Show Chat History"]');
                if (!historyButton) {
                    return JSON.stringify({ error: 'History button not found' });
                }
                
                historyButton.click();
                return JSON.stringify({ success: true });
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def list_conversations():
    """列出所有可用的对话"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 等待一下让面板加载
                return new Promise(resolve => {
                    setTimeout(() => {
                        const conversations = [];
                        const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                        
                        // 查找 auxiliarybar 中的所有元素
                        const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                        if (!auxiliarybar) {
                            resolve(JSON.stringify({ error: 'auxiliarybar not found' }));
                            return;
                        }
                        
                        // 查找所有可能是对话项的可点击元素
                        const clickableElements = auxiliarybar.querySelectorAll('a, button, [onclick], [class*="item"], [class*="row"]');
                        
                        const seen = new Set();
                        
                        clickableElements.forEach(el => {
                            const html = el.outerHTML.substring(0, 2000);
                            const uuids = html.match(uuidRegex);
                            
                            if (uuids && uuids.length > 0) {
                                // 使用第一个 UUID 作为标识
                                const uuid = uuids[0].toLowerCase();
                                
                                // 避免重复
                                if (seen.has(uuid)) return;
                                seen.add(uuid);
                                
                                // 获取文本内容
                                const text = el.textContent?.trim().substring(0, 100) || '';
                                
                                // 检查是否是有效的对话项（有文本内容）
                                if (text.length > 5) {
                                    conversations.push({
                                        conversation_id: uuid,
                                        text: text,
                                        element: {
                                            tag: el.tagName.toLowerCase(),
                                            className: el.className.substring(0, 100),
                                            id: el.id
                                        }
                                    });
                                }
                            }
                        });
                        
                        resolve(JSON.stringify({
                            total: conversations.length,
                            conversations: conversations
                        }));
                    }, 800);
                });
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def switch_to_conversation(target_id):
    """切换到指定对话"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetId = '{target_id}';
                
                // 查找包含目标 ID 的可点击元素
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) {{
                    return JSON.stringify({{ error: 'auxiliarybar not found' }});
                }}
                
                // 查找所有可点击元素
                const clickableElements = auxiliarybar.querySelectorAll('a, button, [onclick], [class*="item"], [class*="row"]');
                
                for (const el of clickableElements) {{
                    const html = el.outerHTML.toLowerCase();
                    if (html.includes(targetId.toLowerCase())) {{
                        // 找到了！点击它
                        el.click();
                        
                        return JSON.stringify({{
                            success: true,
                            clicked_element: {{
                                tag: el.tagName.toLowerCase(),
                                text: el.textContent?.substring(0, 100),
                                className: el.className.substring(0, 100)
                            }}
                        }});
                    }}
                }}
                
                return JSON.stringify({{ error: 'Conversation not found' }});
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def main():
    print("=" * 80)
    print("🔄 Cursor 对话切换演示")
    print("=" * 80)
    print()
    
    # 步骤 1: 获取当前对话 ID
    print("1️⃣  获取当前对话 ID")
    print("-" * 80)
    current = await get_current_conversation_id()
    
    if 'error' in current:
        print(f"❌ 错误: {current['error']}")
        return
    
    current_id = current.get('conversation_id')
    print(f"✅ 当前对话 ID: {current_id}")
    print()
    
    # 步骤 2: 打开 Chat History 面板
    print("2️⃣  打开 Chat History 面板")
    print("-" * 80)
    open_result = await open_history_panel()
    
    if 'error' in open_result:
        print(f"❌ 错误: {open_result['error']}")
        return
    
    print(f"✅ History 面板已打开")
    print()
    
    # 等待面板加载
    print("⏳ 等待面板加载...")
    await asyncio.sleep(1)
    print()
    
    # 步骤 3: 列出所有对话
    print("3️⃣  列出所有可用对话")
    print("-" * 80)
    conversations_data = await list_conversations()
    
    if 'error' in conversations_data:
        print(f"❌ 错误: {conversations_data['error']}")
        return
    
    conversations = conversations_data.get('conversations', [])
    print(f"✅ 找到 {len(conversations)} 个对话:\n")
    
    for idx, conv in enumerate(conversations[:10], 1):  # 只显示前 10 个
        is_current = conv['conversation_id'].lower() == current_id.lower()
        marker = "🎯 [当前]" if is_current else f"   [{idx}]"
        print(f"{marker} {conv['conversation_id']}")
        print(f"      文本: {conv['text']}")
        print()
    
    # 步骤 4: 选择一个不同的对话进行切换
    print("4️⃣  切换到另一个对话")
    print("-" * 80)
    
    # 找到第一个不是当前对话的对话
    target_conv = None
    for conv in conversations:
        if conv['conversation_id'].lower() != current_id.lower():
            target_conv = conv
            break
    
    if not target_conv:
        print("⚠️  没有找到其他对话可以切换")
        return
    
    print(f"目标对话: {target_conv['conversation_id']}")
    print(f"文本预览: {target_conv['text']}")
    print()
    
    # 执行切换
    print("🔄 正在切换...")
    switch_result = await switch_to_conversation(target_conv['conversation_id'])
    
    if 'error' in switch_result:
        print(f"❌ 切换失败: {switch_result['error']}")
        return
    
    print(f"✅ 已点击对话项")
    print(f"   标签: {switch_result['clicked_element']['tag']}")
    print(f"   文本: {switch_result['clicked_element']['text']}")
    print()
    
    # 等待切换完成
    print("⏳ 等待切换完成...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 5: 验证切换成功
    print("5️⃣  验证切换结果")
    print("-" * 80)
    new_current = await get_current_conversation_id()
    
    if 'error' in new_current:
        print(f"❌ 错误: {new_current['error']}")
        return
    
    new_id = new_current.get('conversation_id')
    print(f"新的对话 ID: {new_id}")
    print()
    
    if new_id and new_id.lower() == target_conv['conversation_id'].lower():
        print("🎉 切换成功！")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    elif new_id and new_id != current_id:
        print("✅ 对话已切换（可能切换到了其他对话）")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    else:
        print("⚠️  对话 ID 未改变，切换可能失败或需要更多时间")
        print(f"   当前仍是: {new_id}")
    
    print()
    print("=" * 80)
    print("✅ 演示完成")
    print("=" * 80)


if __name__ == "__main__":
    print("\n💡 这将会切换你的 Cursor 对话！")
    print("确保:")
    print("1. Cursor 已启动")
    print("2. Ortensia inject 正在运行")
    print("3. 有多个对话可供切换")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

