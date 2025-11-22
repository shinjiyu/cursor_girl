#!/usr/bin/env python3
"""
完整演示：切换对话并切换回来

演示流程：
1. 记录当前对话 A
2. 切换到对话 B
3. 验证在 B
4. 切换回对话 A
5. 验证回到 A
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
                const idRegex = /^id_([a-f0-9-]{36})$/;
                
                auxiliarybar.querySelectorAll('[id]').forEach(el => {
                    const match = el.id.match(idRegex);
                    if (match) {
                        const convId = match[1];
                        const clickable = el.querySelector('.cursor-pointer, [class*="cursor-pointer"]');
                        const textDiv = el.querySelector('.max-w-full');
                        const text = textDiv ? textDiv.textContent?.trim() : el.textContent?.trim();
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
                
                const clickable = container.querySelector('.cursor-pointer, [class*="cursor-pointer"]');
                
                if (!clickable) {{
                    return JSON.stringify({{ error: 'Clickable element not found' }});
                }}
                
                clickable.click();
                
                return JSON.stringify({{
                    success: true,
                    clicked_id: targetId
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
    print("🎭 完整演示：来回切换对话")
    print("=" * 80)
    print()
    
    # ========== 第一步：记录起点 ==========
    print("📍 步骤 1: 记录起点")
    print("-" * 80)
    
    original = await get_current_conversation_id()
    original_id = original.get('conversation_id')
    
    print(f"✅ 起始对话: {original_id}")
    print()
    
    # ========== 第二步：打开历史面板 ==========
    print("📂 步骤 2: 打开历史面板")
    print("-" * 80)
    
    await open_history_panel()
    await asyncio.sleep(1)
    
    print("✅ 历史面板已打开")
    print()
    
    # ========== 第三步：列出所有对话 ==========
    print("📋 步骤 3: 列出所有对话")
    print("-" * 80)
    
    convs_data = await list_all_conversations()
    convs = convs_data.get('conversations', [])
    
    print(f"找到 {len(convs)} 个对话:\n")
    
    for idx, conv in enumerate(convs, 1):
        marker = "🎯" if conv['conversation_id'] == original_id else f" {idx}."
        status = "[当前]" if conv['isSelected'] else ""
        print(f"{marker} {conv['text'][:40]}")
        print(f"    ID: {conv['conversation_id']} {status}")
    
    print()
    
    # 选择一个不同的对话作为目标
    target_conv = None
    for conv in convs:
        if conv['conversation_id'] != original_id:
            target_conv = conv
            break
    
    if not target_conv:
        print("⚠️  只有一个对话，无法演示切换")
        return
    
    target_id = target_conv['conversation_id']
    
    # ========== 第四步：切换到目标对话 ==========
    print("➡️  步骤 4: 切换到另一个对话")
    print("-" * 80)
    print(f"目标对话: {target_conv['text'][:40]}")
    print(f"目标 ID: {target_id}")
    print()
    
    print("🔄 正在切换...")
    await switch_to_conversation(target_id)
    await asyncio.sleep(2)
    
    # 验证切换
    current_1 = await get_current_conversation_id()
    current_id_1 = current_1.get('conversation_id')
    
    print(f"✅ 当前对话: {current_id_1}")
    
    if current_id_1 == target_id:
        print(f"🎉 第一次切换成功！")
        print(f"   从: {original_id}")
        print(f"   到: {target_id}")
    else:
        print(f"⚠️  切换未完成")
        print(f"   期望: {target_id}")
        print(f"   实际: {current_id_1}")
    
    print()
    
    # ========== 第五步：重新打开历史面板 ==========
    print("📂 步骤 5: 重新打开历史面板")
    print("-" * 80)
    
    await open_history_panel()
    await asyncio.sleep(1)
    
    print("✅ 历史面板已重新打开")
    print()
    
    # ========== 第六步：切换回原对话 ==========
    print("⬅️  步骤 6: 切换回原对话")
    print("-" * 80)
    print(f"目标对话: {original_id}")
    print()
    
    print("🔄 正在切换回去...")
    await switch_to_conversation(original_id)
    await asyncio.sleep(2)
    
    # 验证切换回来
    current_2 = await get_current_conversation_id()
    current_id_2 = current_2.get('conversation_id')
    
    print(f"✅ 当前对话: {current_id_2}")
    
    if current_id_2 == original_id:
        print(f"🎉 第二次切换成功！")
        print(f"   从: {target_id}")
        print(f"   到: {original_id}")
    else:
        print(f"⚠️  切换未完成")
        print(f"   期望: {original_id}")
        print(f"   实际: {current_id_2}")
    
    print()
    
    # ========== 总结 ==========
    print("=" * 80)
    print("📊 演示总结")
    print("=" * 80)
    print()
    print(f"✅ 起始对话: {original_id}")
    print(f"✅ 切换到:   {target_id}")
    print(f"✅ 切换回:   {current_id_2}")
    print()
    
    success_1 = current_id_1 == target_id
    success_2 = current_id_2 == original_id
    
    if success_1 and success_2:
        print("🎉🎉🎉 完美！两次切换都成功！")
    elif success_1:
        print("✅ 第一次切换成功")
        print("⚠️  第二次切换失败")
    elif success_2:
        print("⚠️  第一次切换失败")
        print("✅ 第二次切换成功")
    else:
        print("⚠️  两次切换都失败")
    
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

