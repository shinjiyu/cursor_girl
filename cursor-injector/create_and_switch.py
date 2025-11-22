#!/usr/bin/env python3
"""
创建新对话并切换

完整演示：
1. 获取当前对话 ID
2. 创建新对话
3. 验证新对话创建成功
4. 切换回原对话
5. 再切换回新对话
"""

import asyncio
import json
import websockets


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


async def create_new_chat():
    """创建新对话"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找 New Chat 按钮
                const newChatButtons = Array.from(document.querySelectorAll('button, a, [role="button"]'))
                    .filter(el => {
                        const text = el.textContent?.toLowerCase() || '';
                        const ariaLabel = el.getAttribute('aria-label')?.toLowerCase() || '';
                        return text.includes('new chat') || ariaLabel.includes('new chat');
                    });
                
                if (newChatButtons.length === 0) {
                    return JSON.stringify({ error: 'New Chat button not found' });
                }
                
                // 点击第一个找到的按钮
                newChatButtons[0].click();
                
                return JSON.stringify({
                    success: true,
                    button_text: newChatButtons[0].textContent?.trim(),
                    button_aria: newChatButtons[0].getAttribute('aria-label')
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


async def list_all_conversations():
    """列出所有对话（不需要打开面板）"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const conversations = [];
                const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                
                // 查找所有包含 UUID 的可点击元素
                const clickableElements = document.querySelectorAll('a, button, [onclick], [class*="conversation"], [class*="chat"]');
                const seen = new Set();
                
                clickableElements.forEach(el => {
                    const html = el.outerHTML.substring(0, 2000);
                    const uuids = html.match(uuidRegex);
                    
                    if (uuids && uuids.length > 0) {
                        const uuid = uuids[0].toLowerCase();
                        
                        if (seen.has(uuid)) return;
                        seen.add(uuid);
                        
                        const text = el.textContent?.trim().substring(0, 100) || '';
                        
                        if (text.length > 3 || el.getAttribute('aria-label')) {
                            conversations.push({
                                conversation_id: uuid,
                                text: text,
                                aria_label: el.getAttribute('aria-label'),
                                element: {
                                    tag: el.tagName.toLowerCase(),
                                    className: el.className.substring(0, 100)
                                }
                            });
                        }
                    }
                });
                
                return JSON.stringify({
                    total: conversations.length,
                    conversations: conversations
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


async def open_history_and_switch(target_id):
    """打开历史面板并切换到指定对话"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (async () => {{
                const targetId = '{target_id}';
                
                // 1. 先打开 History 面板
                const historyButton = document.querySelector('[aria-label*="Show Chat History"]');
                if (historyButton) {{
                    historyButton.click();
                    
                    // 等待面板加载
                    await new Promise(resolve => setTimeout(resolve, 800));
                }}
                
                // 2. 查找目标对话并点击
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) {{
                    return JSON.stringify({{ error: 'auxiliarybar not found' }});
                }}
                
                const clickableElements = auxiliarybar.querySelectorAll('a, button, [onclick], [class*="item"]');
                
                for (const el of clickableElements) {{
                    const html = el.outerHTML.toLowerCase();
                    if (html.includes(targetId.toLowerCase())) {{
                        el.click();
                        
                        return JSON.stringify({{
                            success: true,
                            switched_to: targetId,
                            element_text: el.textContent?.substring(0, 100)
                        }});
                    }}
                }}
                
                return JSON.stringify({{ error: 'Target conversation not found in history' }});
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
    print("🎬 Cursor 对话创建与切换完整演示")
    print("=" * 80)
    print()
    
    # 步骤 1: 记录原始对话
    print("1️⃣  记录当前对话 ID")
    print("-" * 80)
    original = await get_current_conversation_id()
    
    if 'error' in original:
        print(f"❌ 错误: {original['error']}")
        return
    
    original_id = original.get('conversation_id')
    print(f"✅ 原始对话 ID: {original_id}")
    print()
    
    # 步骤 2: 创建新对话
    print("2️⃣  创建新对话")
    print("-" * 80)
    print("🔄 正在点击 'New Chat' 按钮...")
    
    create_result = await create_new_chat()
    
    if 'error' in create_result:
        print(f"❌ 错误: {create_result['error']}")
        return
    
    print(f"✅ 已点击: {create_result.get('button_text', 'New Chat')}")
    print()
    
    # 等待新对话加载
    print("⏳ 等待新对话加载...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 3: 验证新对话
    print("3️⃣  验证新对话")
    print("-" * 80)
    new_conv = await get_current_conversation_id()
    
    if 'error' in new_conv:
        print(f"❌ 错误: {new_conv['error']}")
        return
    
    new_id = new_conv.get('conversation_id')
    print(f"✅ 新对话 ID: {new_id}")
    
    if new_id != original_id:
        print(f"🎉 成功创建新对话！")
        print(f"   原始: {original_id}")
        print(f"   新的: {new_id}")
    else:
        print(f"⚠️  对话 ID 未改变，可能需要更多时间")
    print()
    
    # 步骤 4: 列出所有对话
    print("4️⃣  列出所有可用对话")
    print("-" * 80)
    all_convs = await list_all_conversations()
    
    if 'error' in all_convs:
        print(f"❌ 错误: {all_convs['error']}")
    else:
        convs = all_convs.get('conversations', [])
        print(f"✅ 找到 {len(convs)} 个对话:\n")
        
        for idx, conv in enumerate(convs[:5], 1):
            is_current = conv['conversation_id'].lower() == new_id.lower() if new_id else False
            is_original = conv['conversation_id'].lower() == original_id.lower()
            
            marker = "🎯 [当前]" if is_current else ("📌 [原始]" if is_original else f"   [{idx}]")
            print(f"{marker} {conv['conversation_id']}")
            if conv['text']:
                print(f"      文本: {conv['text'][:80]}")
            if conv['aria_label']:
                print(f"      标签: {conv['aria_label']}")
            print()
    
    # 步骤 5: 切换回原始对话
    print("5️⃣  切换回原始对话")
    print("-" * 80)
    print(f"🔄 正在切换到: {original_id}")
    
    switch_result = await open_history_and_switch(original_id)
    
    if 'error' in switch_result:
        print(f"❌ 切换失败: {switch_result['error']}")
    else:
        print(f"✅ 已切换")
        if switch_result.get('element_text'):
            print(f"   点击了: {switch_result['element_text'][:80]}")
    print()
    
    # 等待切换完成
    print("⏳ 等待切换完成...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 6: 验证切换
    print("6️⃣  验证切换结果")
    print("-" * 80)
    current = await get_current_conversation_id()
    
    if 'error' in current:
        print(f"❌ 错误: {current['error']}")
    else:
        current_id = current.get('conversation_id')
        print(f"当前对话 ID: {current_id}")
        
        if current_id and current_id.lower() == original_id.lower():
            print("🎉 成功切换回原始对话！")
        else:
            print(f"⚠️  当前对话不是原始对话")
            print(f"   期望: {original_id}")
            print(f"   实际: {current_id}")
    print()
    
    # 步骤 7: 再切换到新对话
    print("7️⃣  切换到新对话")
    print("-" * 80)
    print(f"🔄 正在切换到: {new_id}")
    
    switch_result2 = await open_history_and_switch(new_id)
    
    if 'error' in switch_result2:
        print(f"❌ 切换失败: {switch_result2['error']}")
    else:
        print(f"✅ 已切换")
    print()
    
    print("⏳ 等待切换完成...")
    await asyncio.sleep(2)
    print()
    
    # 最终验证
    print("8️⃣  最终验证")
    print("-" * 80)
    final = await get_current_conversation_id()
    
    if 'error' in final:
        print(f"❌ 错误: {final['error']}")
    else:
        final_id = final.get('conversation_id')
        print(f"最终对话 ID: {final_id}")
        
        if final_id and final_id.lower() == new_id.lower():
            print("🎉 成功切换到新对话！")
        else:
            print(f"⚠️  当前对话不是新对话")
    print()
    
    print("=" * 80)
    print("✅ 演示完成")
    print("=" * 80)
    print()
    print("📊 演示摘要:")
    print(f"   原始对话: {original_id}")
    print(f"   新建对话: {new_id}")
    print(f"   最终对话: {final.get('conversation_id', 'unknown')}")
    print()


if __name__ == "__main__":
    print("\n💡 这将创建新对话并演示切换功能！")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

