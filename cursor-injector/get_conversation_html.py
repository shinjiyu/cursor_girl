#!/usr/bin/env python3
"""
获取对话项的完整 HTML 结构

获取"修改本地缓存的git帐号密码"这个对话项的完整 HTML
分析其结构并找到正确的点击方式
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


async def get_conversation_html():
    """获取对话项的完整 HTML"""
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const searchText = '修改本地缓存的git帐号密码';
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                
                if (!auxiliarybar) {
                    return JSON.stringify({ error: 'auxiliarybar not found' });
                }
                
                // 找到包含这个文本的最小元素
                let bestMatch = null;
                let minLength = Infinity;
                
                auxiliarybar.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim();
                    
                    if (text && text.includes(searchText)) {
                        // 排除代码内容
                        if (!text.includes('.py') && !text.includes('#!/')) {
                            if (text.length < minLength && text.length < 200) {
                                minLength = text.length;
                                bestMatch = el;
                            }
                        }
                    }
                });
                
                if (!bestMatch) {
                    return JSON.stringify({ error: 'Element not found' });
                }
                
                // 获取这个元素及其祖先的完整信息
                const chain = [];
                let current = bestMatch;
                let depth = 0;
                
                while (current && current !== auxiliarybar && depth < 15) {
                    // 获取所有事件监听器（尝试）
                    const hasListeners = current.onclick !== null;
                    
                    chain.push({
                        depth: depth,
                        tag: current.tagName.toLowerCase(),
                        className: current.className,
                        id: current.id,
                        role: current.getAttribute('role'),
                        ariaLabel: current.getAttribute('aria-label'),
                        dataAttributes: Array.from(current.attributes)
                            .filter(attr => attr.name.startsWith('data-'))
                            .map(attr => ({ name: attr.name, value: attr.value })),
                        hasOnClick: hasListeners,
                        textContent: current.textContent?.trim().substring(0, 150),
                        // 完整 HTML（限制长度）
                        outerHTML: current.outerHTML.substring(0, 1000),
                        // 检查 CSS 属性
                        computedStyle: {
                            cursor: window.getComputedStyle(current).cursor,
                            pointerEvents: window.getComputedStyle(current).pointerEvents,
                            userSelect: window.getComputedStyle(current).userSelect
                        }
                    });
                    
                    current = current.parentElement;
                    depth++;
                }
                
                return JSON.stringify({
                    found: true,
                    searchText: searchText,
                    matchedText: bestMatch.textContent?.trim(),
                    chain: chain
                }, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        return json.loads(result.get('result', '{}'))
    return {"error": result.get('error')}


async def main():
    print("=" * 80)
    print("🔬 获取对话项 HTML 结构")
    print("=" * 80)
    print()
    
    data = await get_conversation_html()
    
    if 'error' in data:
        print(f"❌ 错误: {data['error']}")
        return
    
    print(f"✅ 找到: {data['searchText']}")
    print(f"匹配文本: {data['matchedText']}")
    print()
    
    chain = data.get('chain', [])
    print(f"元素层级链（共 {len(chain)} 层）:\n")
    print("=" * 80)
    
    for element in chain:
        print(f"\n层级 {element['depth']}: <{element['tag']}>")
        print("-" * 80)
        
        if element['id']:
            print(f"ID: {element['id']}")
        
        if element['className']:
            print(f"类名: {element['className']}")
        
        if element['role']:
            print(f"Role: {element['role']}")
        
        if element['ariaLabel']:
            print(f"Aria-Label: {element['ariaLabel']}")
        
        if element['dataAttributes']:
            print(f"Data 属性:")
            for attr in element['dataAttributes']:
                print(f"  - {attr['name']}: {attr['value']}")
        
        print(f"有 onClick: {element['hasOnClick']}")
        
        style = element['computedStyle']
        print(f"CSS cursor: {style['cursor']}")
        print(f"CSS pointer-events: {style['pointerEvents']}")
        
        if element['depth'] < 5:
            print(f"\n文本: {element['textContent']}")
            print(f"\nHTML:")
            print(element['outerHTML'])
    
    print()
    print("=" * 80)
    print("✅ 分析完成")
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

