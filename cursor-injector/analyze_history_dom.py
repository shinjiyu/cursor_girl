#!/usr/bin/env python3
"""
精确分析历史面板的 DOM 结构

专注于：
1. 找到实际的对话列表容器
2. 分析每个对话项的完整 HTML 结构
3. 找到可点击元素的确切位置
4. 测试点击功能
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


async def get_history_panel_html():
    """获取历史面板的完整 HTML"""
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
                
                // 获取完整 HTML（限制长度）
                const html = auxiliarybar.outerHTML.substring(0, 50000);
                
                return JSON.stringify({
                    html: html,
                    length: auxiliarybar.outerHTML.length
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


async def find_conversation_list_containers():
    """找到对话列表的容器"""
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
                
                const containers = [];
                
                // 1. 查找包含 "2w ago", "Today" 等时间文本的父容器
                const timeTexts = ['Today', '2w ago', '3w ago', 'Yesterday'];
                const timeElements = [];
                
                auxiliarybar.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim();
                    if (timeTexts.some(t => text === t)) {
                        timeElements.push(el);
                    }
                });
                
                console.log('Found time elements:', timeElements.length);
                
                // 2. 找到这些时间元素的父容器
                timeElements.forEach((timeEl, idx) => {
                    let container = timeEl.parentElement;
                    let depth = 0;
                    
                    // 向上找 3 层
                    while (container && depth < 5) {
                        const children = Array.from(container.children);
                        
                        // 检查这个容器下是否有多个子元素（对话项）
                        if (children.length > 2) {
                            containers.push({
                                type: 'time-parent',
                                depth: depth,
                                tag: container.tagName.toLowerCase(),
                                className: container.className.substring(0, 200),
                                id: container.id,
                                childrenCount: children.length,
                                timeText: timeEl.textContent?.trim(),
                                // 获取部分子元素的信息
                                children: children.slice(0, 10).map(child => ({
                                    tag: child.tagName.toLowerCase(),
                                    className: child.className.substring(0, 100),
                                    text: child.textContent?.trim().substring(0, 80),
                                    hasLink: !!child.querySelector('a'),
                                    hasButton: !!child.querySelector('button')
                                }))
                            });
                        }
                        
                        container = container.parentElement;
                        depth++;
                    }
                });
                
                // 3. 查找所有 scrollable 容器（对话列表通常是可滚动的）
                const scrollables = auxiliarybar.querySelectorAll('[class*="scroll"], [style*="overflow"]');
                scrollables.forEach(el => {
                    if (el.children.length > 1) {
                        containers.push({
                            type: 'scrollable',
                            tag: el.tagName.toLowerCase(),
                            className: el.className.substring(0, 200),
                            id: el.id,
                            childrenCount: el.children.length
                        });
                    }
                });
                
                return JSON.stringify({
                    totalContainers: containers.length,
                    containers: containers
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


async def analyze_specific_conversation_item():
    """分析"删除并重新部署hooks"这个对话项的完整结构"""
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
                
                // 查找包含"删除并重新部署hooks"的元素
                const searchText = '删除并重新部署hooks';
                let targetElement = null;
                
                auxiliarybar.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim();
                    if (text && text.includes(searchText) && text.length < 100) {
                        // 找最小的包含这个文本的元素
                        if (!targetElement || el.textContent.length < targetElement.textContent.length) {
                            targetElement = el;
                        }
                    }
                });
                
                if (!targetElement) {
                    return JSON.stringify({ error: 'Target element not found' });
                }
                
                // 分析这个元素及其父元素链
                const elementChain = [];
                let current = targetElement;
                let depth = 0;
                
                while (current && current !== auxiliarybar && depth < 10) {
                    const links = Array.from(current.querySelectorAll('a'));
                    const buttons = Array.from(current.querySelectorAll('button'));
                    
                    elementChain.push({
                        depth: depth,
                        tag: current.tagName.toLowerCase(),
                        className: current.className.substring(0, 200),
                        id: current.id,
                        role: current.getAttribute('role'),
                        ariaLabel: current.getAttribute('aria-label'),
                        text: current.textContent?.trim().substring(0, 100),
                        hasOnClick: current.onclick !== null,
                        // 子元素信息
                        directChildren: Array.from(current.children).map(child => ({
                            tag: child.tagName.toLowerCase(),
                            className: child.className.substring(0, 100),
                            text: child.textContent?.trim().substring(0, 60)
                        })),
                        // 链接信息
                        links: links.map(link => ({
                            href: link.href,
                            text: link.textContent?.trim(),
                            className: link.className.substring(0, 100),
                            id: link.id
                        })),
                        // 按钮信息
                        buttons: buttons.map(btn => ({
                            text: btn.textContent?.trim(),
                            className: btn.className.substring(0, 100),
                            type: btn.type
                        })),
                        // 部分 HTML
                        htmlPreview: current.outerHTML.substring(0, 500)
                    });
                    
                    current = current.parentElement;
                    depth++;
                }
                
                return JSON.stringify({
                    found: true,
                    searchText: searchText,
                    elementChain: elementChain
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


async def click_conversation_link():
    """尝试点击对话链接"""
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
                
                // 找到所有包含"修改本地缓存"的链接
                const links = Array.from(auxiliarybar.querySelectorAll('a'));
                
                for (const link of links) {
                    const text = link.textContent?.trim();
                    if (text && text.includes('修改本地缓存')) {
                        // 找到了！点击它
                        console.log('Clicking link:', text);
                        link.click();
                        
                        return JSON.stringify({
                            success: true,
                            clickedText: text,
                            href: link.href,
                            className: link.className
                        });
                    }
                }
                
                return JSON.stringify({ error: 'Link not found' });
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
    print("🔬 精确分析历史面板 DOM 结构")
    print("=" * 80)
    print()
    
    # 步骤 1: 打开历史面板
    print("1️⃣  打开历史面板")
    print("-" * 80)
    await open_history_panel()
    await asyncio.sleep(1)
    print("✅ 已打开")
    print()
    
    # 步骤 2: 查找对话列表容器
    print("2️⃣  查找对话列表容器")
    print("-" * 80)
    containers_data = await find_conversation_list_containers()
    
    if 'error' in containers_data:
        print(f"❌ 错误: {containers_data['error']}")
    else:
        containers = containers_data.get('containers', [])
        print(f"✅ 找到 {len(containers)} 个可能的容器:\n")
        
        for idx, container in enumerate(containers[:5], 1):
            print(f"容器 {idx}:")
            print(f"  类型: {container['type']}")
            print(f"  标签: <{container['tag']}>")
            print(f"  类名: {container['className'][:80]}")
            print(f"  子元素数: {container['childrenCount']}")
            
            if container.get('timeText'):
                print(f"  时间文本: {container['timeText']}")
            
            if container.get('children'):
                print(f"  子元素样例:")
                for child in container['children'][:3]:
                    print(f"    - <{child['tag']}> {child['text'][:60]}")
            print()
    
    # 步骤 3: 详细分析一个对话项
    print("3️⃣  详细分析对话项结构")
    print("-" * 80)
    item_data = await analyze_specific_conversation_item()
    
    if 'error' in item_data:
        print(f"❌ 错误: {item_data['error']}")
    else:
        print(f"✅ 找到: {item_data['searchText']}\n")
        chain = item_data.get('elementChain', [])
        
        print(f"元素层级链（从内到外）:\n")
        for element in chain:
            print(f"层级 {element['depth']}: <{element['tag']}>")
            print(f"  类名: {element['className'][:80]}")
            if element['id']:
                print(f"  ID: {element['id']}")
            if element['role']:
                print(f"  Role: {element['role']}")
            if element['hasOnClick']:
                print(f"  ⚡ 有 onClick 事件")
            
            if element['links']:
                print(f"  🔗 包含链接:")
                for link in element['links']:
                    print(f"     - {link['text']}")
                    print(f"       href: {link['href']}")
            
            if element['buttons']:
                print(f"  🔘 包含按钮: {len(element['buttons'])} 个")
            
            if element['directChildren'] and element['depth'] < 3:
                print(f"  子元素:")
                for child in element['directChildren'][:3]:
                    print(f"     - <{child['tag']}> {child['text'][:50]}")
            
            print()
    
    # 步骤 4: 尝试点击另一个对话
    print("4️⃣  尝试点击对话链接")
    print("-" * 80)
    print("🔄 正在点击'修改本地缓存'对话...")
    
    click_result = await click_conversation_link()
    
    if 'error' in click_result:
        print(f"❌ 点击失败: {click_result['error']}")
    else:
        print(f"✅ 已点击!")
        print(f"   文本: {click_result['clickedText']}")
        print(f"   href: {click_result['href']}")
    
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

