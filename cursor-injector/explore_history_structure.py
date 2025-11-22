#!/usr/bin/env python3
"""
详细探索 Chat History 界面的 DOM 结构

目标：
1. 打开历史面板
2. 分析整个面板的层级结构
3. 找到每个对话项的 DOM 元素
4. 理解点击事件的绑定方式
5. 找到正确的切换方法
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


async def analyze_history_panel_structure():
    """详细分析历史面板的结构"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 1. 找到 auxiliarybar（历史面板的容器）
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) {
                    return JSON.stringify({ error: 'auxiliarybar not found' });
                }
                
                const structure = {
                    auxiliarybar: {
                        id: auxiliarybar.id,
                        className: auxiliarybar.className,
                        childrenCount: auxiliarybar.children.length,
                        children: []
                    }
                };
                
                // 2. 分析第一层子元素
                Array.from(auxiliarybar.children).forEach((child, idx) => {
                    structure.auxiliarybar.children.push({
                        index: idx,
                        tag: child.tagName.toLowerCase(),
                        id: child.id,
                        className: child.className.substring(0, 200),
                        role: child.getAttribute('role'),
                        childrenCount: child.children.length,
                        hasText: child.textContent?.trim().length > 0
                    });
                });
                
                // 3. 查找搜索框
                const searchBox = auxiliarybar.querySelector('input[type="text"], input[placeholder*="Search"]');
                structure.searchBox = searchBox ? {
                    exists: true,
                    placeholder: searchBox.placeholder,
                    id: searchBox.id,
                    value: searchBox.value
                } : { exists: false };
                
                // 4. 查找所有包含 "Today", "2w ago" 等时间标题的元素
                const timeHeaders = [];
                auxiliarybar.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim();
                    if (text && /^(Today|Yesterday|\d+[wdmh]\s+ago)$/i.test(text)) {
                        timeHeaders.push({
                            text: text,
                            tag: el.tagName.toLowerCase(),
                            className: el.className.substring(0, 200),
                            parentTag: el.parentElement?.tagName.toLowerCase(),
                            parentClassName: el.parentElement?.className.substring(0, 200)
                        });
                    }
                });
                structure.timeHeaders = timeHeaders;
                
                // 5. 查找对话项（可能是 li, div, a 等）
                const conversationItems = [];
                const uuidRegex = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/gi;
                
                // 查找所有可能的对话项容器
                const possibleContainers = auxiliarybar.querySelectorAll('ul, ol, [role="list"], [class*="list"]');
                
                possibleContainers.forEach((container, containerIdx) => {
                    const items = container.children;
                    
                    Array.from(items).forEach((item, itemIdx) => {
                        const text = item.textContent?.trim();
                        const html = item.outerHTML;
                        const uuids = html.match(uuidRegex);
                        
                        // 只记录有内容或有 UUID 的项
                        if ((text && text.length > 3) || uuids) {
                            conversationItems.push({
                                containerIndex: containerIdx,
                                itemIndex: itemIdx,
                                tag: item.tagName.toLowerCase(),
                                className: item.className.substring(0, 200),
                                id: item.id,
                                role: item.getAttribute('role'),
                                text: text?.substring(0, 150),
                                hasUUID: !!uuids,
                                uuids: uuids || [],
                                // 检查是否有点击事件
                                hasOnClick: item.onclick !== null,
                                hasClickableChild: !!item.querySelector('a, button, [onclick]'),
                                // 获取可点击子元素的信息
                                clickableChildren: Array.from(item.querySelectorAll('a, button, [role="button"]')).map(child => ({
                                    tag: child.tagName.toLowerCase(),
                                    text: child.textContent?.trim().substring(0, 100),
                                    className: child.className.substring(0, 100),
                                    role: child.getAttribute('role'),
                                    ariaLabel: child.getAttribute('aria-label')
                                }))
                            });
                        }
                    });
                });
                
                structure.conversationItems = conversationItems;
                
                // 6. 查找 "Current" 标记
                const currentMarkers = [];
                auxiliarybar.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim();
                    if (text === 'Current' || el.getAttribute('aria-label')?.includes('Current')) {
                        currentMarkers.push({
                            text: text,
                            tag: el.tagName.toLowerCase(),
                            className: el.className.substring(0, 200),
                            ariaLabel: el.getAttribute('aria-label')
                        });
                    }
                });
                structure.currentMarkers = currentMarkers;
                
                return JSON.stringify(structure, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def find_conversation_by_text(search_text):
    """通过文本查找对话项"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const searchText = '{search_text}';
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                if (!auxiliarybar) {{
                    return JSON.stringify({{ error: 'auxiliarybar not found' }});
                }}
                
                const matches = [];
                
                // 查找所有包含搜索文本的元素
                auxiliarybar.querySelectorAll('*').forEach(el => {{
                    const text = el.textContent?.trim();
                    if (text && text.includes(searchText)) {{
                        // 找到最近的可点击父元素
                        let clickableParent = el;
                        while (clickableParent && clickableParent !== auxiliarybar) {{
                            if (clickableParent.tagName === 'A' || 
                                clickableParent.tagName === 'BUTTON' ||
                                clickableParent.onclick ||
                                clickableParent.getAttribute('role') === 'button') {{
                                break;
                            }}
                            clickableParent = clickableParent.parentElement;
                        }}
                        
                        matches.push({{
                            element: {{
                                tag: el.tagName.toLowerCase(),
                                text: text.substring(0, 200),
                                className: el.className.substring(0, 200),
                                id: el.id
                            }},
                            clickableParent: clickableParent && clickableParent !== auxiliarybar ? {{
                                tag: clickableParent.tagName.toLowerCase(),
                                className: clickableParent.className.substring(0, 200),
                                id: clickableParent.id,
                                role: clickableParent.getAttribute('role'),
                                ariaLabel: clickableParent.getAttribute('aria-label')
                            }} : null
                        }});
                    }}
                }});
                
                return JSON.stringify({{
                    searchText: searchText,
                    totalMatches: matches.length,
                    matches: matches
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
    print("🔍 详细探索 Chat History 界面结构")
    print("=" * 80)
    print()
    
    # 步骤 1: 打开历史面板
    print("1️⃣  打开历史面板")
    print("-" * 80)
    open_result = await open_history_panel()
    
    if 'error' in open_result:
        print(f"❌ 错误: {open_result['error']}")
        return
    
    print("✅ 历史面板已打开")
    print()
    
    # 等待加载
    print("⏳ 等待面板加载...")
    await asyncio.sleep(1)
    print()
    
    # 步骤 2: 分析结构
    print("2️⃣  分析面板结构")
    print("-" * 80)
    structure = await analyze_history_panel_structure()
    
    if 'error' in structure:
        print(f"❌ 错误: {structure['error']}")
        return
    
    # 显示结构信息
    print("📦 Auxiliarybar 容器:")
    aux_info = structure.get('auxiliarybar', {})
    print(f"   ID: {aux_info.get('id')}")
    print(f"   子元素数量: {aux_info.get('childrenCount')}")
    print()
    
    print("🔍 搜索框:")
    search_info = structure.get('searchBox', {})
    if search_info.get('exists'):
        print(f"   ✅ 存在")
        print(f"   Placeholder: {search_info.get('placeholder')}")
    else:
        print(f"   ❌ 未找到")
    print()
    
    print("📅 时间标题:")
    time_headers = structure.get('timeHeaders', [])
    print(f"   找到 {len(time_headers)} 个时间标题:")
    for header in time_headers:
        print(f"   - {header['text']}")
        print(f"     标签: <{header['tag']}> 类名: {header['className'][:50]}")
    print()
    
    print("💬 对话项:")
    conv_items = structure.get('conversationItems', [])
    print(f"   找到 {len(conv_items)} 个可能的对话项:\n")
    
    for idx, item in enumerate(conv_items, 1):
        print(f"   [{idx}] <{item['tag']}>")
        print(f"       文本: {item['text']}")
        print(f"       类名: {item['className'][:80]}")
        if item['role']:
            print(f"       Role: {item['role']}")
        if item['hasUUID']:
            print(f"       UUID: {item['uuids'][0] if item['uuids'] else 'N/A'}")
        print(f"       可点击: {item['hasOnClick'] or item['hasClickableChild']}")
        
        if item['clickableChildren']:
            print(f"       可点击子元素:")
            for child in item['clickableChildren']:
                print(f"         - <{child['tag']}> {child['text'][:60]}")
        print()
    
    print("🎯 Current 标记:")
    current_markers = structure.get('currentMarkers', [])
    if current_markers:
        for marker in current_markers:
            print(f"   - {marker['text']}")
            print(f"     标签: <{marker['tag']}> 类名: {marker['className'][:50]}")
    else:
        print("   ❌ 未找到")
    print()
    
    # 步骤 3: 按文本查找对话
    print("3️⃣  查找特定对话")
    print("-" * 80)
    
    # 从截图中我们看到有这些对话
    search_texts = [
        "删除并重新部署hooks",
        "修改本地缓存的git账号密码",
        "审查设计可行性"
    ]
    
    for search_text in search_texts:
        print(f"\n🔎 搜索: '{search_text}'")
        print("-" * 60)
        
        find_result = await find_conversation_by_text(search_text)
        
        if 'error' in find_result:
            print(f"   ❌ 错误: {find_result['error']}")
            continue
        
        matches = find_result.get('matches', [])
        print(f"   找到 {len(matches)} 个匹配项:\n")
        
        for idx, match in enumerate(matches[:3], 1):  # 只显示前 3 个
            element = match.get('element', {})
            clickable = match.get('clickableParent')
            
            print(f"   匹配 {idx}:")
            print(f"     元素: <{element['tag']}> {element['text'][:80]}")
            
            if clickable:
                print(f"     可点击父元素: <{clickable['tag']}>")
                print(f"       类名: {clickable['className'][:80]}")
                if clickable['role']:
                    print(f"       Role: {clickable['role']}")
                if clickable['ariaLabel']:
                    print(f"       Aria-Label: {clickable['ariaLabel'][:60]}")
            else:
                print(f"     ⚠️  未找到可点击父元素")
            print()
    
    print("=" * 80)
    print("✅ 结构分析完成")
    print("=" * 80)
    print()
    
    print("💡 总结:")
    print(f"   - 对话项数量: {len(conv_items)}")
    print(f"   - 时间分组: {len(time_headers)}")
    print(f"   - 有 UUID 的项: {sum(1 for item in conv_items if item['hasUUID'])}")
    print(f"   - 可点击的项: {sum(1 for item in conv_items if item['hasOnClick'] or item['hasClickableChild'])}")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

