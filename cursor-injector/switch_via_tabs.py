#!/usr/bin/env python3
"""
通过 Tab 标签切换对话

在 Cursor 中，聊天对话可能以 Tab 的形式显示在顶部
尝试找到并点击这些 Tab 来切换对话
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


async def find_conversation_tabs():
    """查找所有对话 Tab"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const tabs = [];
                const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                
                // 1. 查找所有 role="tab" 的元素
                const roleTabElements = document.querySelectorAll('[role="tab"]');
                console.log('Found role=tab elements:', roleTabElements.length);
                
                roleTabElements.forEach(el => {
                    const html = el.outerHTML;
                    const uuids = html.match(uuidRegex);
                    
                    if (uuids && uuids.length > 0) {
                        tabs.push({
                            type: 'role-tab',
                            conversation_id: uuids[0],
                            text: el.textContent?.trim().substring(0, 100) || '',
                            aria_label: el.getAttribute('aria-label') || '',
                            aria_selected: el.getAttribute('aria-selected'),
                            className: el.className.substring(0, 200),
                            id: el.id
                        });
                    }
                });
                
                // 2. 查找 class 包含 "tab" 的元素
                const classTabElements = document.querySelectorAll('[class*="tab"]');
                console.log('Found class*=tab elements:', classTabElements.length);
                
                const seen = new Set(tabs.map(t => t.conversation_id));
                
                classTabElements.forEach(el => {
                    const html = el.outerHTML;
                    const uuids = html.match(uuidRegex);
                    
                    if (uuids && uuids.length > 0 && !seen.has(uuids[0])) {
                        seen.add(uuids[0]);
                        tabs.push({
                            type: 'class-tab',
                            conversation_id: uuids[0],
                            text: el.textContent?.trim().substring(0, 100) || '',
                            className: el.className.substring(0, 200),
                            tag: el.tagName.toLowerCase()
                        });
                    }
                });
                
                // 3. 查找顶部的 tabs container
                const tabsContainer = document.querySelector('.tabs-container, .editor-tabs, [class*="tabs"]');
                console.log('Tabs container found:', !!tabsContainer);
                
                if (tabsContainer) {
                    const allElements = tabsContainer.querySelectorAll('*');
                    allElements.forEach(el => {
                        const html = el.outerHTML;
                        const uuids = html.match(uuidRegex);
                        
                        if (uuids && uuids.length > 0 && !seen.has(uuids[0])) {
                            seen.add(uuids[0]);
                            tabs.push({
                                type: 'tabs-container',
                                conversation_id: uuids[0],
                                text: el.textContent?.trim().substring(0, 100) || '',
                                className: el.className.substring(0, 200),
                                tag: el.tagName.toLowerCase()
                            });
                        }
                    });
                }
                
                return JSON.stringify({
                    total: tabs.length,
                    tabs: tabs,
                    has_tabs_container: !!tabsContainer
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


async def click_tab_by_conversation_id(conversation_id):
    """点击指定的对话 Tab"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetId = '{conversation_id}'.toLowerCase();
                
                // 1. 先尝试 role="tab"
                const roleTabs = document.querySelectorAll('[role="tab"]');
                for (const tab of roleTabs) {{
                    const html = tab.outerHTML.toLowerCase();
                    if (html.includes(targetId)) {{
                        console.log('Clicking role=tab');
                        tab.click();
                        return JSON.stringify({{
                            success: true,
                            method: 'role-tab',
                            text: tab.textContent?.substring(0, 100)
                        }});
                    }}
                }}
                
                // 2. 尝试所有包含 tab 的可点击元素
                const allClickable = document.querySelectorAll('[class*="tab"]');
                for (const el of allClickable) {{
                    const html = el.outerHTML.toLowerCase();
                    if (html.includes(targetId)) {{
                        console.log('Clicking class*=tab');
                        el.click();
                        return JSON.stringify({{
                            success: true,
                            method: 'class-tab',
                            text: el.textContent?.substring(0, 100)
                        }});
                    }}
                }}
                
                // 3. 尝试任何包含该 ID 的元素
                const allElements = document.querySelectorAll('*');
                for (const el of allElements) {{
                    if (el.id.toLowerCase().includes(targetId) || 
                        el.className.toLowerCase().includes(targetId)) {{
                        console.log('Clicking any matching element');
                        el.click();
                        return JSON.stringify({{
                            success: true,
                            method: 'any-element',
                            element_id: el.id,
                            element_class: el.className.substring(0, 100)
                        }});
                    }}
                }}
                
                return JSON.stringify({{ error: 'Tab not found' }});
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
    print("🔖 通过 Tab 标签切换对话")
    print("=" * 80)
    print()
    
    # 步骤 1: 获取当前对话
    print("1️⃣  获取当前对话")
    print("-" * 80)
    current = await get_current_conversation_id()
    
    if 'error' in current:
        print(f"❌ 错误: {current['error']}")
        return
    
    current_id = current.get('conversation_id')
    print(f"✅ 当前对话: {current_id}")
    print()
    
    # 步骤 2: 查找所有 Tab
    print("2️⃣  查找所有对话 Tab")
    print("-" * 80)
    tabs_data = await find_conversation_tabs()
    
    if 'error' in tabs_data:
        print(f"❌ 错误: {tabs_data['error']}")
        return
    
    tabs = tabs_data.get('tabs', [])
    has_container = tabs_data.get('has_tabs_container', False)
    
    print(f"✅ 找到 {len(tabs)} 个 Tab 标签")
    print(f"   Tabs Container 存在: {'是' if has_container else '否'}")
    print()
    
    if len(tabs) == 0:
        print("⚠️  没有找到任何 Tab 标签")
        print("   对话可能不是以 Tab 形式显示的")
        return
    
    # 显示所有 Tab
    print("📋 所有找到的 Tab:")
    print()
    for idx, tab in enumerate(tabs, 1):
        is_current = tab['conversation_id'].lower() == current_id.lower()
        marker = "🎯" if is_current else f"{idx}."
        
        print(f"{marker} {tab['conversation_id']}")
        print(f"   类型: {tab['type']}")
        if tab.get('text'):
            print(f"   文本: {tab['text']}")
        if tab.get('aria_label'):
            print(f"   标签: {tab['aria_label']}")
        if tab.get('aria_selected'):
            print(f"   选中: {tab['aria_selected']}")
        print()
    
    # 步骤 3: 切换到另一个 Tab
    target_tab = None
    for tab in tabs:
        if tab['conversation_id'].lower() != current_id.lower():
            target_tab = tab
            break
    
    if not target_tab:
        print("⚠️  只有一个 Tab，无法切换")
        return
    
    print("3️⃣  切换到另一个对话")
    print("-" * 80)
    print(f"目标对话: {target_tab['conversation_id']}")
    if target_tab.get('text'):
        print(f"文本预览: {target_tab['text']}")
    print()
    
    print("🔄 正在点击 Tab...")
    click_result = await click_tab_by_conversation_id(target_tab['conversation_id'])
    
    if 'error' in click_result:
        print(f"❌ 点击失败: {click_result['error']}")
        return
    
    print(f"✅ 已点击 Tab")
    print(f"   方法: {click_result.get('method')}")
    if click_result.get('text'):
        print(f"   文本: {click_result['text']}")
    print()
    
    # 等待切换
    print("⏳ 等待切换完成...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 4: 验证切换
    print("4️⃣  验证切换结果")
    print("-" * 80)
    new_current = await get_current_conversation_id()
    
    if 'error' in new_current:
        print(f"❌ 错误: {new_current['error']}")
        return
    
    new_id = new_current.get('conversation_id')
    print(f"当前对话: {new_id}")
    print()
    
    if new_id and new_id.lower() == target_tab['conversation_id'].lower():
        print("🎉 切换成功！")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    else:
        print("⚠️  切换可能失败或未生效")
        print(f"   期望: {target_tab['conversation_id']}")
        print(f"   实际: {new_id}")
    
    print()
    print("=" * 80)
    print("✅ 演示完成")
    print("=" * 80)


if __name__ == "__main__":
    print("\n💡 尝试通过 Tab 标签切换对话")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

