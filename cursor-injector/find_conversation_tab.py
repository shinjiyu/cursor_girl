#!/usr/bin/env python3
"""
查找 conversation_id 在 tab 标签中的位置
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


async def main():
    target_uuid = "2d8f9386-9864-4a51-b089-a7342029bb41"
    
    print("=" * 80)
    print(f"🔍 查找 conversation_id: {target_uuid}")
    print("=" * 80)
    print()
    
    # ============================================================
    # 1. 在整个文档中搜索这个特定的 UUID
    # ============================================================
    print("1️⃣  搜索目标 UUID 在文档中的所有位置")
    print("-" * 80)
    
    code = f"""
    (async () => {{
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {{
                const targetUuid = '{target_uuid}';
                const found = [];
                
                // 遍历所有元素
                const allElements = document.querySelectorAll('*');
                
                allElements.forEach((el) => {{
                    // 检查 ID
                    if (el.id && el.id.includes(targetUuid)) {{
                        found.push({{
                            type: 'id',
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            class: el.className.substring(0, 100),
                            text: el.textContent?.substring(0, 100) || ''
                        }});
                    }}
                    
                    // 检查所有属性
                    for (const attr of el.attributes) {{
                        if (attr.value.includes(targetUuid)) {{
                            found.push({{
                                type: 'attribute',
                                tag: el.tagName.toLowerCase(),
                                attrName: attr.name,
                                attrValue: attr.value.substring(0, 200),
                                class: el.className.substring(0, 100),
                                id: el.id,
                                text: el.textContent?.substring(0, 100) || ''
                            }});
                        }}
                    }}
                    
                    // 检查 data-* 属性
                    if (el.dataset) {{
                        for (const key in el.dataset) {{
                            if (el.dataset[key].includes(targetUuid)) {{
                                found.push({{
                                    type: 'dataset',
                                    tag: el.tagName.toLowerCase(),
                                    dataKey: key,
                                    dataValue: el.dataset[key].substring(0, 200),
                                    class: el.className.substring(0, 100),
                                    id: el.id,
                                    text: el.textContent?.substring(0, 100) || ''
                                }});
                            }}
                        }}
                    }}
                }});
                
                return JSON.stringify(found, null, 2);
            }})()
        `);
        
        return result;
    }})()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        found = json.loads(result.get('result', '[]'))
        if found:
            print(f"找到 {len(found)} 个匹配项:\n")
            for item in found:
                print(f"类型: {item['type']}")
                print(f"标签: {item['tag']}")
                if item['type'] == 'id':
                    print(f"ID: {item['id']}")
                elif item['type'] == 'attribute':
                    print(f"属性: {item['attrName']} = {item['attrValue']}")
                elif item['type'] == 'dataset':
                    print(f"Data: {item['dataKey']} = {item['dataValue']}")
                print(f"Class: {item['class']}")
                print(f"文本预览: {item['text']}")
                print()
        else:
            print("未找到匹配项")
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 2. 专门查找所有 tab 相关的元素
    # ============================================================
    print("2️⃣  查找所有 tab 相关元素")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const selectors = [
                    '[role="tab"]',
                    '[role="tablist"]',
                    '[role="tabpanel"]',
                    '.tab',
                    '[class*="tab"]',
                    '[class*="conversation"]',
                    '[id*="tab"]',
                    '[data-tab]',
                    '[aria-selected]'
                ];
                
                const found = [];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, idx) => {
                        if (idx < 10) {  // 限制每个选择器最多 10 个
                            // 获取所有属性
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value.substring(0, 200);
                            }
                            
                            // 获取所有 data-* 属性
                            const dataset = {};
                            if (el.dataset) {
                                for (const key in el.dataset) {
                                    dataset[key] = el.dataset[key].substring(0, 200);
                                }
                            }
                            
                            found.push({
                                selector: selector,
                                tag: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className.substring(0, 100),
                                attributes: attrs,
                                dataset: dataset,
                                text: el.textContent?.substring(0, 100) || '',
                                ariaLabel: el.getAttribute('aria-label'),
                                ariaSelected: el.getAttribute('aria-selected')
                            });
                        }
                    });
                }
                
                return JSON.stringify(found, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        tabs = json.loads(result.get('result', '[]'))
        print(f"找到 {len(tabs)} 个 tab 相关元素:\n")
        
        for tab in tabs:
            print(f"选择器: {tab['selector']}")
            print(f"标签: {tab['tag']} | ID: {tab['id']}")
            print(f"Class: {tab['className']}")
            if tab.get('ariaLabel'):
                print(f"Aria Label: {tab['ariaLabel']}")
            if tab.get('ariaSelected'):
                print(f"Aria Selected: {tab['ariaSelected']}")
            
            # 检查是否包含我们的 UUID
            all_text = json.dumps(tab)
            if target_uuid in all_text:
                print(f"🎯 包含目标 UUID!")
            
            print(f"属性: {json.dumps(tab['attributes'], indent=2)}")
            if tab['dataset']:
                print(f"Dataset: {json.dumps(tab['dataset'], indent=2)}")
            print(f"文本: {tab['text']}")
            print("-" * 40)
            print()
    else:
        print(f"❌ 失败: {result.get('error')}")
    print()
    
    # ============================================================
    # 3. 查找对话列表/历史记录
    # ============================================================
    print("3️⃣  查找对话列表相关元素")
    print("-" * 80)
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return 'No windows';
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const selectors = [
                    '.conversations',
                    '[class*="conversation-list"]',
                    '[class*="history"]',
                    '[class*="sidebar"]',
                    '[id*="conversation"]'
                ];
                
                const found = [];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach((el, idx) => {
                        if (idx < 5) {
                            // 查找子元素中可能包含 conversation ID 的内容
                            const children = el.querySelectorAll('*');
                            const childrenWithUuid = [];
                            
                            children.forEach((child, childIdx) => {
                                if (childIdx < 20) {
                                    // 检查是否有类似 UUID 的内容
                                    const idAttr = child.id;
                                    const dataAttrs = {};
                                    if (child.dataset) {
                                        for (const key in child.dataset) {
                                            dataAttrs[key] = child.dataset[key].substring(0, 200);
                                        }
                                    }
                                    
                                    const hasUuidPattern = /[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/i;
                                    
                                    if (hasUuidPattern.test(idAttr) || hasUuidPattern.test(JSON.stringify(dataAttrs))) {
                                        childrenWithUuid.push({
                                            tag: child.tagName.toLowerCase(),
                                            id: idAttr,
                                            class: child.className.substring(0, 100),
                                            dataset: dataAttrs,
                                            text: child.textContent?.substring(0, 50) || ''
                                        });
                                    }
                                }
                            });
                            
                            if (childrenWithUuid.length > 0) {
                                found.push({
                                    selector: selector,
                                    tag: el.tagName.toLowerCase(),
                                    id: el.id,
                                    className: el.className.substring(0, 100),
                                    childrenWithUuid: childrenWithUuid
                                });
                            }
                        }
                    });
                }
                
                return JSON.stringify(found, null, 2);
            })()
        `);
        
        return result;
    })()
    """
    
    result = await execute_js(code)
    if result.get('success'):
        lists = json.loads(result.get('result', '[]'))
        if lists:
            print(f"找到 {len(lists)} 个对话列表:\n")
            for lst in lists:
                print(f"选择器: {lst['selector']}")
                print(f"容器: {lst['tag']} | ID: {lst['id']}")
                print(f"Class: {lst['className']}")
                print(f"包含 UUID 的子元素数量: {len(lst['childrenWithUuid'])}")
                print()
                for child in lst['childrenWithUuid'][:5]:  # 只显示前 5 个
                    print(f"  - {child['tag']} | ID: {child['id']}")
                    print(f"    Class: {child['class']}")
                    if child['dataset']:
                        print(f"    Dataset: {json.dumps(child['dataset'])}")
                    print(f"    Text: {child['text']}")
                    
                    # 检查是否是我们的目标 UUID
                    if target_uuid in json.dumps(child):
                        print(f"    🎯 这就是目标 conversation_id!")
                    print()
                print("-" * 40)
        else:
            print("未找到对话列表")
    else:
        print(f"❌ 失败: {result.get('error')}")
    
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

