#!/usr/bin/env python3
"""
最终版本：正确切换对话

发现：
- 对话项结构：<div id="id_{conversation_id}"><div class="...cursor-pointer...">
- 需要点击那个有 cursor-pointer 类的 div
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


async def open_history_panel():
    """打开历史面板"""
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
                }}
                
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


async def list_all_conversations():
    """列出所有对话"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) {
                    return JSON.stringify({ error: 'auxiliarybar not found' });
                }
                
                const conversations = [];
                
                // 查找所有 id="id_{uuid}" 格式的元素
                const idRegex = /^id_([a-f0-9-]{36})$/;
                
                auxiliarybar.querySelectorAll('[id]').forEach(el => {
                    const match = el.id.match(idRegex);
                    if (match) {
                        const convId = match[1];
                        
                        // 查找其中的可点击元素
                        const clickable = el.querySelector('.cursor-pointer, [class*="cursor-pointer"]');
                        
                        // 获取对话文本
                        const textDiv = el.querySelector('.max-w-full');
                        const text = textDiv ? textDiv.textContent?.trim() : el.textContent?.trim();
                        
                        // 检查是否被选中
                        const isSelected = el.querySelector('[data-is-selected="true"]') !== null;
                        
                        conversations.push({
                            conversation_id: convId,
                            text: text?.substring(0, 100),
                            isSelected: isSelected,
                            hasClickable: !!clickable
                        });
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


async def switch_to_conversation(conversation_id):
    """切换到指定对话"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetId = '{conversation_id}';
                const elementId = 'id_' + targetId;
                
                const container = document.getElementById(elementId);
                if (!container) {{
                    return JSON.stringify({{ error: 'Conversation container not found: ' + elementId }});
                }}
                
                // 查找可点击元素
                const clickable = container.querySelector('.cursor-pointer, [class*="cursor-pointer"]');
                
                if (!clickable) {{
                    return JSON.stringify({{ error: 'Clickable element not found' }});
                }}
                
                console.log('Clicking conversation:', targetId);
                clickable.click();
                
                return JSON.stringify({{
                    success: true,
                    clicked_id: targetId,
                    element_class: clickable.className.substring(0, 150)
                }});
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
    print("🎯 最终版本：正确切换对话")
    print("=" * 80)
    print()
    
    # 步骤 1: 获取当前对话
    print("1️⃣  当前对话")
    print("-" * 80)
    current = await get_current_conversation_id()
    current_id = current.get('conversation_id')
    print(f"✅ {current_id}")
    print()
    
    # 步骤 2: 打开历史面板
    print("2️⃣  打开历史面板")
    print("-" * 80)
    await open_history_panel()
    await asyncio.sleep(1)
    print("✅ 已打开")
    print()
    
    # 步骤 3: 列出所有对话
    print("3️⃣  列出所有对话")
    print("-" * 80)
    convs_data = await list_all_conversations()
    
    if 'error' in convs_data:
        print(f"❌ 错误: {convs_data['error']}")
        return
    
    convs = convs_data.get('conversations', [])
    print(f"✅ 找到 {len(convs)} 个对话:\n")
    
    for idx, conv in enumerate(convs, 1):
        marker = "🎯" if conv['isSelected'] else f" {idx}."
        print(f"{marker} {conv['conversation_id']}")
        print(f"    {conv['text']}")
        if conv['isSelected']:
            print(f"    [当前选中]")
        print()
    
    # 步骤 4: 选择一个不同的对话
    target_conv = None
    for conv in convs:
        if not conv['isSelected']:
            target_conv = conv
            break
    
    if not target_conv:
        print("⚠️  只有一个对话，无法切换")
        return
    
    print("4️⃣  切换对话")
    print("-" * 80)
    print(f"目标: {target_conv['conversation_id']}")
    print(f"文本: {target_conv['text']}")
    print()
    
    switch_result = await switch_to_conversation(target_conv['conversation_id'])
    
    if 'error' in switch_result:
        print(f"❌ 失败: {switch_result['error']}")
        return
    
    print(f"✅ 已点击!")
    print()
    
    # 等待切换
    print("⏳ 等待切换...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 5: 验证
    print("5️⃣  验证切换结果")
    print("-" * 80)
    new_current = await get_current_conversation_id()
    new_id = new_current.get('conversation_id')
    
    print(f"新对话: {new_id}")
    print()
    
    if new_id == target_conv['conversation_id']:
        print("🎉 切换成功！")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    else:
        print(f"⚠️  切换未完成")
        print(f"   期望: {target_conv['conversation_id']}")
        print(f"   实际: {new_id}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

