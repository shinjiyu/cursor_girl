#!/usr/bin/env python3
"""
找到真正的历史面板

目标：找到包含"修改本地缓存的git账号密码"等对话的真实面板
这可能是一个：
- 下拉菜单
- 弹出层
- 对话框
- 侧边栏的特定区域
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


async def search_for_text_in_dom(search_text):
    """在整个 DOM 中搜索特定文本"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const searchText = '{search_text}';
                const matches = [];
                
                // 搜索所有包含这个文本的元素
                document.querySelectorAll('*').forEach(el => {{
                    const text = el.textContent?.trim();
                    // 找到恰好包含这个文本的最小元素
                    if (text && text.includes(searchText) && text.length < 200) {{
                        const directText = Array.from(el.childNodes)
                            .filter(node => node.nodeType === 3) // Text nodes
                            .map(node => node.textContent.trim())
                            .join(' ');
                        
                        matches.push({{
                            tag: el.tagName.toLowerCase(),
                            className: el.className.substring(0, 200),
                            id: el.id,
                            text: text,
                            directText: directText,
                            isClickable: el.tagName === 'A' || el.tagName === 'BUTTON' || el.onclick !== null,
                            parentTag: el.parentElement?.tagName.toLowerCase(),
                            parentClassName: el.parentElement?.className.substring(0, 200),
                            // 找最近的可点击父元素
                            clickableParentFound: false,
                            htmlPreview: el.outerHTML.substring(0, 400)
                        }});
                    }}
                }});
                
                // 为每个匹配查找可点击父元素
                matches.forEach(match => {{
                    const el = Array.from(document.querySelectorAll('*')).find(e => 
                        e.outerHTML.substring(0, 400) === match.htmlPreview
                    );
                    
                    if (el) {{
                        let parent = el.parentElement;
                        let depth = 0;
                        
                        while (parent && depth < 10) {{
                            if (parent.tagName === 'A' || 
                                parent.tagName === 'BUTTON' ||
                                parent.onclick ||
                                parent.getAttribute('role') === 'button' ||
                                parent.getAttribute('onclick')) {{
                                match.clickableParent = {{
                                    tag: parent.tagName.toLowerCase(),
                                    className: parent.className.substring(0, 200),
                                    id: parent.id,
                                    role: parent.getAttribute('role'),
                                    depth: depth
                                }};
                                match.clickableParentFound = true;
                                break;
                            }}
                            parent = parent.parentElement;
                            depth++;
                        }}
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


async def find_all_dropdowns_and_panels():
    """查找所有下拉菜单和弹出面板"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const panels = [];
                
                // 1. 查找所有可能是弹出层的元素
                const selectors = [
                    '[role="dialog"]',
                    '[role="menu"]',
                    '[role="listbox"]',
                    '[class*="dropdown"]',
                    '[class*="popup"]',
                    '[class*="popover"]',
                    '[class*="modal"]',
                    '[class*="panel"]',
                    '[class*="overlay"]',
                    '[style*="position: fixed"]',
                    '[style*="position: absolute"]'
                ];
                
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        // 只记录可见且有内容的元素
                        if (el.offsetParent !== null && el.textContent?.trim().length > 20) {
                            panels.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                className: el.className.substring(0, 200),
                                id: el.id,
                                role: el.getAttribute('role'),
                                textPreview: el.textContent?.trim().substring(0, 200),
                                childrenCount: el.children.length,
                                hasSearch: !!el.querySelector('input[placeholder*="Search"]'),
                                // 检查是否包含我们要找的对话
                                hasConversations: el.textContent?.includes('修改本地缓存') || 
                                                  el.textContent?.includes('审查设计')
                            });
                        }
                    });
                });
                
                return JSON.stringify({
                    totalPanels: panels.length,
                    panels: panels
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


async def click_conversation_by_text(conversation_text):
    """通过文本点击对话"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const searchText = '{conversation_text}';
                
                // 找到所有包含这个文本的元素
                const allElements = Array.from(document.querySelectorAll('*'));
                
                for (const el of allElements) {{
                    const text = el.textContent?.trim();
                    if (text && text.includes(searchText) && text.length < 200) {{
                        // 尝试点击这个元素
                        console.log('Found element:', el);
                        
                        // 如果本身可点击，直接点击
                        if (el.tagName === 'A' || el.tagName === 'BUTTON' || el.onclick) {{
                            console.log('Clicking element itself');
                            el.click();
                            return JSON.stringify({{
                                success: true,
                                method: 'direct',
                                tag: el.tagName.toLowerCase(),
                                text: text.substring(0, 100)
                            }});
                        }}
                        
                        // 否则找可点击的父元素
                        let parent = el.parentElement;
                        let depth = 0;
                        
                        while (parent && depth < 10) {{
                            if (parent.tagName === 'A' || 
                                parent.tagName === 'BUTTON' ||
                                parent.onclick ||
                                parent.getAttribute('role') === 'button') {{
                                console.log('Clicking parent at depth', depth);
                                parent.click();
                                return JSON.stringify({{
                                    success: true,
                                    method: 'parent',
                                    depth: depth,
                                    tag: parent.tagName.toLowerCase(),
                                    text: text.substring(0, 100)
                                }});
                            }}
                            parent = parent.parentElement;
                            depth++;
                        }}
                        
                        // 如果没找到可点击父元素，尝试直接触发点击事件
                        console.log('Dispatching click event');
                        el.dispatchEvent(new MouseEvent('click', {{ bubbles: true }}));
                        return JSON.stringify({{
                            success: true,
                            method: 'event',
                            tag: el.tagName.toLowerCase(),
                            text: text.substring(0, 100)
                        }});
                    }}
                }}
                
                return JSON.stringify({{ error: 'Element not found' }});
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
    print("🔍 查找真正的历史面板")
    print("=" * 80)
    print()
    
    # 步骤 1: 搜索特定对话文本
    print("1️⃣  搜索对话文本在 DOM 中的位置")
    print("-" * 80)
    
    search_texts = [
        "修改本地缓存的git账号密码",
        "审查设计可行性",
        "查找开源本地TTS实现"
    ]
    
    for search_text in search_texts:
        print(f"\n🔎 搜索: '{search_text}'")
        print("-" * 60)
        
        search_result = await search_for_text_in_dom(search_text)
        
        if 'error' in search_result:
            print(f"   ❌ 错误: {search_result['error']}")
            continue
        
        matches = search_result.get('matches', [])
        print(f"   找到 {len(matches)} 个匹配:\n")
        
        for idx, match in enumerate(matches[:2], 1):
            print(f"   匹配 {idx}:")
            print(f"     标签: <{match['tag']}>")
            print(f"     文本: {match['text'][:80]}")
            print(f"     类名: {match['className'][:80]}")
            print(f"     自身可点击: {match['isClickable']}")
            
            if match.get('clickableParent'):
                cp = match['clickableParent']
                print(f"     可点击父元素: <{cp['tag']}> (深度 {cp['depth']})")
                print(f"       类名: {cp['className'][:80]}")
            else:
                print(f"     ⚠️  未找到可点击父元素")
            
            # 显示 HTML 预览
            print(f"     HTML: {match['htmlPreview'][:150]}...")
            print()
        
        if matches:
            break  # 找到一个就够了
    
    # 步骤 2: 查找所有弹出面板
    print("\n2️⃣  查找所有弹出面板和下拉菜单")
    print("-" * 80)
    
    panels_data = await find_all_dropdowns_and_panels()
    
    if 'error' in panels_data:
        print(f"❌ 错误: {panels_data['error']}")
    else:
        panels = panels_data.get('panels', [])
        print(f"✅ 找到 {len(panels)} 个面板/弹出层:\n")
        
        # 只显示包含对话的面板
        conversation_panels = [p for p in panels if p.get('hasConversations')]
        
        if conversation_panels:
            print(f"🎯 包含对话的面板: {len(conversation_panels)} 个\n")
            for idx, panel in enumerate(conversation_panels[:3], 1):
                print(f"面板 {idx}:")
                print(f"  选择器: {panel['selector']}")
                print(f"  标签: <{panel['tag']}>")
                print(f"  类名: {panel['className'][:80]}")
                print(f"  Role: {panel['role']}")
                print(f"  有搜索框: {panel['hasSearch']}")
                print(f"  文本预览: {panel['textPreview'][:100]}...")
                print()
        else:
            print("⚠️  没有找到包含对话的面板")
            print(f"显示前 3 个面板:\n")
            for idx, panel in enumerate(panels[:3], 1):
                print(f"面板 {idx}:")
                print(f"  标签: <{panel['tag']}>")
                print(f"  类名: {panel['className'][:80]}")
                print(f"  文本: {panel['textPreview'][:100]}")
                print()
    
    # 步骤 3: 尝试点击对话
    print("3️⃣  尝试点击对话")
    print("-" * 80)
    
    if matches:
        click_text = search_texts[0] if search_texts else "修改本地缓存"
        print(f"🔄 正在点击: '{click_text}'")
        
        click_result = await click_conversation_by_text(click_text)
        
        if 'error' in click_result:
            print(f"❌ 点击失败: {click_result['error']}")
        else:
            print(f"✅ 已点击!")
            print(f"   方法: {click_result.get('method')}")
            print(f"   标签: <{click_result.get('tag')}>")
            print(f"   文本: {click_result.get('text')}")
    else:
        print("⚠️  未找到可点击的对话")
    
    print()
    print("=" * 80)
    print("✅ 搜索完成")
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

