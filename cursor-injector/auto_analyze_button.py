#!/usr/bin/env python3
"""
自动分析 .send-with-mode 按钮结构
自动清空/输入文字，对比两种状态
"""

import asyncio
import websockets
import json


async def clear_input(ws):
    """清空输入框"""
    code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({ success: false });
                    
                    input.focus();
                    const sel = window.getSelection();
                    const range = document.createRange();
                    range.selectNodeContents(input);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    document.execCommand('delete', false, null);
                    
                    return JSON.stringify({ success: true });
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return JSON.stringify({ success: false });
    })()
    '''
    
    await ws.send(code)
    response_str = await ws.recv()
    response = json.loads(response_str)
    
    if response['success']:
        result = json.loads(response['result'])
        return result['success']
    return False


async def input_text(ws, text):
    """输入文字"""
    escaped_text = text.replace("'", "\\'")
    
    code = f'''
    (async () => {{
        const {{ BrowserWindow }} = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {{
            const code = `
                (function() {{
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({{ success: false }});
                    
                    input.focus();
                    document.execCommand('insertText', false, '{escaped_text}');
                    input.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                    
                    return JSON.stringify({{ success: true }});
                }})()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }}
        return JSON.stringify({{ success: false }});
    }})()
    '''
    
    await ws.send(code)
    response_str = await ws.recv()
    response = json.loads(response_str)
    
    if response['success']:
        result = json.loads(response['result'])
        return result['success']
    return False


async def get_button_info(ws):
    """获取按钮详细信息"""
    code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const button = document.querySelector('.send-with-mode');
                    
                    if (!button) {
                        return JSON.stringify({ found: false });
                    }
                    
                    // 获取所有属性
                    const attributes = {};
                    for (let attr of button.attributes) {
                        attributes[attr.name] = attr.value;
                    }
                    
                    // 获取子元素信息
                    const children = [];
                    button.querySelectorAll('*').forEach((el, index) => {
                        const style = window.getComputedStyle(el);
                        children.push({
                            index: index,
                            tagName: el.tagName,
                            className: el.className,
                            id: el.id,
                            cursor: style.cursor,
                            pointerEvents: style.pointerEvents,
                            display: style.display,
                            opacity: style.opacity,
                            hasOnClick: el.onclick !== null,
                            role: el.getAttribute('role'),
                            ariaLabel: el.getAttribute('aria-label')
                        });
                    });
                    
                    const style = window.getComputedStyle(button);
                    
                    return JSON.stringify({
                        found: true,
                        tagName: button.tagName,
                        className: button.className,
                        id: button.id,
                        attributes: attributes,
                        visible: button.offsetParent !== null,
                        disabled: button.disabled,
                        innerHTML: button.innerHTML,
                        outerHTML: button.outerHTML.substring(0, 800),
                        computedStyle: {
                            display: style.display,
                            cursor: style.cursor,
                            pointerEvents: style.pointerEvents,
                            opacity: style.opacity,
                            visibility: style.visibility
                        },
                        children: children,
                        childElementCount: button.childElementCount
                    });
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return JSON.stringify({ found: false });
    })()
    '''
    
    await ws.send(code)
    response_str = await ws.recv()
    response = json.loads(response_str)
    
    if response['success']:
        return json.loads(response['result'])
    return {'found': False}


def print_button_info(info, label):
    """打印按钮信息"""
    print(f'\n{label}')
    print('─' * 70)
    
    if not info['found']:
        print('❌ 按钮未找到')
        return
    
    print(f"✅ 按钮已找到")
    print(f"  标签: {info['tagName']}")
    print(f"  类名: {info['className']}")
    print(f"  ID: {info['id'] or '(无)'}")
    print(f"  可见: {info['visible']}")
    print(f"  子元素数: {info['childElementCount']}")
    
    print(f"\n  计算样式:")
    for key, val in info['computedStyle'].items():
        print(f"    {key}: {val}")
    
    print(f"\n  属性:")
    for key, val in info['attributes'].items():
        print(f"    {key}: {val}")
    
    print(f"\n  outerHTML (前 800 字符):")
    print(f"    {info['outerHTML']}")
    
    if info['children']:
        print(f"\n  子元素 ({len(info['children'])} 个):")
        for i, child in enumerate(info['children'][:5]):  # 只显示前 5 个
            print(f"    [{i}] {child['tagName']}.{child['className'][:30]}")
            print(f"        cursor: {child['cursor']}, pointer-events: {child['pointerEvents']}")
            if child['ariaLabel']:
                print(f"        aria-label: {child['ariaLabel']}")


def compare_states(state1, state2):
    """对比两个状态的差异"""
    print('\n' + '=' * 70)
    print('  🔍 差异分析')
    print('=' * 70)
    
    if not state1['found'] or not state2['found']:
        print('❌ 无法对比，有状态缺失')
        return
    
    print('\n1️⃣  类名变化:')
    if state1['className'] != state2['className']:
        print(f"  ❗ 变化:")
        print(f"    空: {state1['className']}")
        print(f"    有: {state2['className']}")
    else:
        print(f"  ✓ 无变化: {state1['className']}")
    
    print('\n2️⃣  样式变化:')
    changed = False
    for key in state1['computedStyle'].keys():
        val1 = state1['computedStyle'][key]
        val2 = state2['computedStyle'][key]
        if val1 != val2:
            print(f"  ❗ {key}: {val1} → {val2}")
            changed = True
    if not changed:
        print("  ✓ 无变化")
    
    print('\n3️⃣  子元素数量:')
    print(f"  空: {len(state1['children'])} 个")
    print(f"  有: {len(state2['children'])} 个")
    
    print('\n4️⃣  innerHTML 变化:')
    if state1['innerHTML'] != state2['innerHTML']:
        print("  ❗ 发生了变化")
        print(f"\n  空输入时 (前 200 字符):")
        print(f"    {state1['innerHTML'][:200]}")
        print(f"\n  有文字时 (前 200 字符):")
        print(f"    {state2['innerHTML'][:200]}")
    else:
        print("  ✓ 无变化")
    
    print('\n5️⃣  可交互的子元素 (有文字时):')
    clickable = [c for c in state2['children'] if c['cursor'] == 'pointer' or c['pointerEvents'] != 'none']
    if clickable:
        print(f"  找到 {len(clickable)} 个可能可点击的子元素:")
        for i, child in enumerate(clickable):
            selector = f"{child['tagName'].lower()}"
            if child['className']:
                selector += f".{child['className'].split()[0]}"
            print(f"    {i+1}. {selector}")
            print(f"       cursor: {child['cursor']}, pointer-events: {child['pointerEvents']}")
            if child['ariaLabel']:
                print(f"       aria-label: {child['ariaLabel']}")
    else:
        print("  ❌ 未找到明显可点击的子元素")


async def auto_analyze():
    print('=' * 70)
    print('  🤖 自动分析 .send-with-mode 按钮')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 状态 1: 清空输入
        print('📍 步骤 1: 清空输入框...')
        if await clear_input(ws):
            print('✅ 输入框已清空')
        else:
            print('❌ 清空失败')
            return
        
        await asyncio.sleep(0.5)
        
        print('\n📍 步骤 2: 获取空输入状态...')
        state1 = await get_button_info(ws)
        print_button_info(state1, '【空输入状态】')
        
        # 状态 2: 输入文字
        print('\n\n📍 步骤 3: 输入测试文字...')
        test_text = "测试按钮分析"
        if await input_text(ws, test_text):
            print(f'✅ 已输入: "{test_text}"')
        else:
            print('❌ 输入失败')
            return
        
        await asyncio.sleep(1)  # 等待 UI 更新
        
        print('\n📍 步骤 4: 获取有文字状态...')
        state2 = await get_button_info(ws)
        print_button_info(state2, '【有文字状态】')
        
        # 对比差异
        compare_states(state1, state2)
        
        # 保存完整数据
        data = {
            'empty_state': state1,
            'with_text_state': state2
        }
        
        with open('/tmp/send_button_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print('\n' + '=' * 70)
        print('✅ 分析完成！')
        print('完整数据已保存到: /tmp/send_button_analysis.json')
        print('=' * 70)
        
        # 点击建议
        print('\n【🎯 点击建议】')
        print('─' * 70)
        
        if state2['found']:
            print('\n基于分析，建议尝试点击:')
            print('1. .send-with-mode 本身')
            
            clickable = [c for c in state2['children'] if c['cursor'] == 'pointer']
            if clickable:
                for i, child in enumerate(clickable, 2):
                    selector = f".send-with-mode > {child['tagName'].lower()}"
                    if child['className']:
                        selector += f".{child['className'].split()[0]}"
                    print(f"{i}. {selector}")
            
            print('\n使用 test_custom_selector.py 测试这些选择器')


if __name__ == '__main__':
    try:
        asyncio.run(auto_analyze())
    except KeyboardInterrupt:
        print('\n\n⚠️  已取消')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()

