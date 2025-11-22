#!/usr/bin/env python3
"""
在历史面板中精确点击对话

策略：
1. 打开历史面板
2. 在 auxiliarybar 中精确定位对话列表
3. 找到包含特定文本的对话项
4. 点击它
5. 验证切换
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


async def find_and_click_conversation(conversation_text):
    """在 auxiliarybar 中查找并点击对话"""
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
                
                console.log('Searching in auxiliarybar for:', searchText);
                
                // 在 auxiliarybar 中查找所有可能的对话项
                // 排除 Tab 区域（composite-bar）
                const compositeBars = auxiliarybar.querySelectorAll('.composite-bar');
                const excludeElements = new Set(compositeBars);
                
                // 查找所有包含文本的小元素（< 200 字符）
                const candidates = [];
                auxiliarybar.querySelectorAll('*').forEach(el => {{
                    // 跳过 Tab 区域
                    let isInTabArea = false;
                    excludeElements.forEach(exclude => {{
                        if (exclude.contains(el)) {{
                            isInTabArea = true;
                        }}
                    }});
                    
                    if (isInTabArea) return;
                    
                    const text = el.textContent?.trim();
                    if (!text || !text.includes(searchText)) return;
                    
                    // 只要恰好包含搜索文本的元素
                    if (text.length > 10 && text.length < 200) {{
                        candidates.push(el);
                    }}
                }});
                
                console.log('Found candidates:', candidates.length);
                
                // 尝试点击每个候选元素或其父元素
                for (const candidate of candidates) {{
                    console.log('Trying candidate:', candidate.textContent.substring(0, 50));
                    
                    // 检查这个元素或其父元素是否可点击
                    let clickTarget = null;
                    let current = candidate;
                    let depth = 0;
                    
                    while (current && depth < 15) {{
                        // 检查是否是可点击元素
                        if (current.tagName === 'A' ||
                            current.tagName === 'BUTTON' ||
                            current.onclick ||
                            current.getAttribute('role') === 'button' ||
                            current.getAttribute('role') === 'option' ||
                            current.className.includes('clickable') ||
                            current.className.includes('item')) {{
                            clickTarget = current;
                            break;
                        }}
                        
                        current = current.parentElement;
                        depth++;
                        
                        // 不要超出 auxiliarybar
                        if (current === auxiliarybar) break;
                    }}
                    
                    if (clickTarget) {{
                        console.log('Found click target:', clickTarget.tagName, clickTarget.className);
                        clickTarget.click();
                        
                        return JSON.stringify({{
                            success: true,
                            foundText: candidate.textContent.substring(0, 100),
                            clickedElement: {{
                                tag: clickTarget.tagName.toLowerCase(),
                                className: clickTarget.className.substring(0, 200),
                                id: clickTarget.id,
                                depth: depth
                            }}
                        }});
                    }}
                }}
                
                // 如果都没找到，尝试直接触发事件
                if (candidates.length > 0) {{
                    console.log('No clickable element found, dispatching event');
                    const candidate = candidates[0];
                    
                    // 尝试多种事件
                    candidate.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));
                    candidate.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true }}));
                    candidate.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true }}));
                    
                    return JSON.stringify({{
                        success: true,
                        method: 'event-dispatch',
                        foundText: candidate.textContent.substring(0, 100)
                    }});
                }}
                
                return JSON.stringify({{
                    error: 'Conversation not found',
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
    print("🎯 在历史面板中点击对话")
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
    
    # 步骤 2: 打开历史面板
    print("2️⃣  打开历史面板")
    print("-" * 80)
    await open_history_panel()
    await asyncio.sleep(1)
    print("✅ 已打开")
    print()
    
    # 步骤 3: 查找并点击对话
    print("3️⃣  查找并点击对话")
    print("-" * 80)
    
    conversation_texts = [
        "修改本地缓存的git账号密码",
        "审查设计可行性",
        "查找开源本地TTS实现"
    ]
    
    clicked = False
    for conv_text in conversation_texts:
        print(f"\n🔎 尝试点击: '{conv_text}'")
        
        click_result = await find_and_click_conversation(conv_text)
        
        if 'error' in click_result:
            print(f"   ❌ 失败: {click_result['error']}")
            if click_result.get('candidatesFound') is not None:
                print(f"   找到候选项: {click_result['candidatesFound']} 个")
            continue
        
        print(f"   ✅ 已点击!")
        print(f"   文本: {click_result.get('foundText', '')[:80]}")
        
        if click_result.get('clickedElement'):
            elem = click_result['clickedElement']
            print(f"   元素: <{elem['tag']}> {elem['className'][:80]}")
        
        clicked = True
        break
    
    if not clicked:
        print("\n⚠️  所有尝试都失败了")
        return
    
    # 等待切换
    print("\n⏳ 等待切换完成...")
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
    print(f"新对话 ID: {new_id}")
    print()
    
    if new_id != current_id:
        print("🎉 切换成功！")
        print(f"   从: {current_id}")
        print(f"   到: {new_id}")
    else:
        print("⚠️  对话 ID 未改变")
        print(f"   当前: {new_id}")
    
    print()
    print("=" * 80)
    print("✅ 完成")
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

