#!/usr/bin/env python3
"""
精确定位并点击历史面板中的对话

策略：
1. 从截图看，历史面板包含：
   - Search... 输入框
   - Today, 2w ago 等时间分组
   - 每个分组下有对话列表
2. 我们需要找到这些时间分组下的对话项
3. 排除当前对话的内容区域
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


async def analyze_time_groups():
    """分析时间分组下的对话列表结构"""
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
                
                const groups = [];
                
                // 查找 "2w ago" 这个时间标签
                const timeTexts = ['Today', '2w ago', '3w ago', '1w ago'];
                
                timeTexts.forEach(timeText => {
                    auxiliarybar.querySelectorAll('*').forEach(el => {
                        const text = el.textContent?.trim();
                        
                        // 找到恰好是时间文本的元素
                        if (text === timeText) {
                            console.log('Found time header:', timeText);
                            
                            // 获取这个时间标签的父容器
                            let container = el.parentElement;
                            let attempts = 0;
                            
                            while (container && attempts < 5) {
                                // 查找这个容器的兄弟元素或子元素中的对话列表
                                const siblings = Array.from(container.parentElement?.children || []);
                                const currentIndex = siblings.indexOf(container);
                                
                                // 检查后面的兄弟元素
                                for (let i = currentIndex + 1; i < siblings.length; i++) {
                                    const sibling = siblings[i];
                                    const siblingText = sibling.textContent?.trim();
                                    
                                    // 如果这个兄弟元素包含多个子项，可能就是对话列表
                                    if (sibling.children.length > 0) {
                                        const items = [];
                                        
                                        // 查找所有可能的对话项
                                        Array.from(sibling.querySelectorAll('*')).forEach(item => {
                                            const itemText = item.textContent?.trim();
                                            
                                            // 对话项特征：
                                            // 1. 有一定长度的文本
                                            // 2. 文本长度适中（10-100字符）
                                            // 3. 不包含时间标签本身
                                            if (itemText && 
                                                itemText.length > 10 && 
                                                itemText.length < 150 &&
                                                !timeTexts.some(t => itemText === t) &&
                                                !itemText.includes('Search')) {
                                                
                                                // 检查是否是重复的（子元素的文本可能重复）
                                                if (!items.some(existing => existing.text === itemText)) {
                                                    items.push({
                                                        text: itemText,
                                                        tag: item.tagName.toLowerCase(),
                                                        className: item.className.substring(0, 150),
                                                        hasHover: item.className.includes('hover'),
                                                        hasClick: item.onclick !== null,
                                                        htmlPreview: item.outerHTML.substring(0, 300)
                                                    });
                                                }
                                            }
                                        });
                                        
                                        if (items.length > 0) {
                                            groups.push({
                                                timeText: timeText,
                                                containerTag: sibling.tagName.toLowerCase(),
                                                containerClassName: sibling.className.substring(0, 150),
                                                itemsCount: items.length,
                                                items: items.slice(0, 5) // 只保留前 5 个
                                            });
                                        }
                                    }
                                    
                                    // 如果遇到下一个时间标签，停止
                                    if (timeTexts.some(t => sibling.textContent?.trim() === t)) {
                                        break;
                                    }
                                }
                                
                                container = container.parentElement;
                                attempts++;
                            }
                        }
                    });
                });
                
                return JSON.stringify({
                    totalGroups: groups.length,
                    groups: groups
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


async def click_conversation_by_exact_text(conversation_text):
    """通过精确文本点击对话（限制在时间分组区域内）"""
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const searchText = '{conversation_text}';
                const auxiliarybar = document.getElementById('workbench.parts.auxiliarybar');
                
                if (!auxiliarybar) {{
                    return JSON.stringify({{ error: 'auxiliarybar not found' }});
                }}
                
                // 首先找到 "2w ago" 区域
                let timeGroup2w = null;
                auxiliarybar.querySelectorAll('*').forEach(el => {{
                    if (el.textContent?.trim() === '2w ago') {{
                        timeGroup2w = el;
                    }}
                }});
                
                if (!timeGroup2w) {{
                    return JSON.stringify({{ error: '2w ago group not found' }});
                }}
                
                console.log('Found 2w ago group');
                
                // 从这个时间标签开始，查找包含搜索文本的元素
                // 限制搜索范围：时间标签的父容器及其兄弟元素
                let searchRoot = timeGroup2w;
                for (let i = 0; i < 3; i++) {{
                    if (searchRoot.parentElement) {{
                        searchRoot = searchRoot.parentElement;
                    }}
                }}
                
                console.log('Search root:', searchRoot.className);
                
                // 在这个范围内查找
                const candidates = [];
                searchRoot.querySelectorAll('*').forEach(el => {{
                    const text = el.textContent?.trim();
                    
                    // 精确匹配或包含搜索文本，且长度适中
                    if (text && text.includes(searchText) && text.length < 200) {{
                        // 排除包含代码、文件名等的元素
                        if (!text.includes('.py') && 
                            !text.includes('#!/') &&
                            !text.includes('async def') &&
                            !text.includes('import ')) {{
                            candidates.push(el);
                        }}
                    }}
                }});
                
                console.log('Found candidates:', candidates.length);
                
                // 尝试点击每个候选
                for (const candidate of candidates) {{
                    console.log('Trying:', candidate.textContent.substring(0, 50));
                    
                    // 查找可点击的父元素
                    let clickTarget = candidate;
                    let depth = 0;
                    
                    while (clickTarget && depth < 10) {{
                        if (clickTarget.tagName === 'A' ||
                            clickTarget.tagName === 'BUTTON' ||
                            clickTarget.onclick ||
                            clickTarget.className.includes('clickable') ||
                            clickTarget.className.includes('item') ||
                            clickTarget.className.includes('row')) {{
                            
                            console.log('Clicking:', clickTarget.tagName, clickTarget.className);
                            clickTarget.click();
                            
                            return JSON.stringify({{
                                success: true,
                                text: candidate.textContent.substring(0, 100),
                                clickedTag: clickTarget.tagName.toLowerCase(),
                                clickedClass: clickTarget.className.substring(0, 150)
                            }});
                        }}
                        
                        clickTarget = clickTarget.parentElement;
                        depth++;
                        
                        if (clickTarget === auxiliarybar) break;
                    }}
                }}
                
                return JSON.stringify({{
                    error: 'No clickable element found',
                    candidatesFound: candidates.length
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
    print("🎯 精确定位并点击历史对话")
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
    
    # 步骤 3: 分析时间分组
    print("3️⃣  分析时间分组结构")
    print("-" * 80)
    groups_data = await analyze_time_groups()
    
    if 'error' in groups_data:
        print(f"❌ 错误: {groups_data['error']}")
    else:
        groups = groups_data.get('groups', [])
        print(f"✅ 找到 {len(groups)} 个时间分组:\n")
        
        for group in groups:
            print(f"📅 {group['timeText']}")
            print(f"   对话数: {group['itemsCount']}")
            print(f"   对话列表:")
            for item in group.get('items', []):
                print(f"     - {item['text'][:60]}")
            print()
    
    # 步骤 4: 点击对话
    print("4️⃣  点击对话")
    print("-" * 80)
    
    click_result = await click_conversation_by_exact_text("修改本地缓存的git账号密码")
    
    if 'error' in click_result:
        print(f"❌ 失败: {click_result['error']}")
        if click_result.get('candidatesFound'):
            print(f"   找到候选项: {click_result['candidatesFound']} 个")
    else:
        print(f"✅ 已点击!")
        print(f"   文本: {click_result['text'][:80]}")
        print(f"   元素: <{click_result['clickedTag']}> {click_result['clickedClass'][:80]}")
    
    print()
    print("⏳ 等待切换...")
    await asyncio.sleep(2)
    print()
    
    # 步骤 5: 验证
    print("5️⃣  验证切换")
    print("-" * 80)
    new_current = await get_current_conversation_id()
    new_id = new_current.get('conversation_id')
    print(f"新对话: {new_id}")
    
    if new_id != current_id:
        print(f"\n🎉 成功切换！")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    else:
        print(f"\n⚠️  未切换")
    
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

