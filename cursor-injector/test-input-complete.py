#!/usr/bin/env python3
"""
完整测试：输入文字并验证
"""

import asyncio
import json
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge', 'venv', 'lib', 'python3.13', 'site-packages'))

import websockets


async def test_input(text: str):
    """测试输入并验证"""
    
    print('🔗 连接到 Cursor...')
    ws = await websockets.connect('ws://localhost:9876')
    print('✅ 已连接\n')
    
    print('=' * 80)
    print(f'  🧪 测试输入: "{text}"')
    print('=' * 80)
    print()
    
    # 转义
    escaped = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    
    # 步骤 1: 输入文字
    print('步骤 1: 输入文字...')
    input_code = f'''
    (async () => {{
        const {{ BrowserWindow }} = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {{
            const code = `
                (function() {{
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({{ success: false }});
                    
                    input.focus();
                    
                    // 选中所有内容
                    const sel = window.getSelection();
                    const range = document.createRange();
                    range.selectNodeContents(input);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    
                    // 删除旧内容
                    document.execCommand('delete', false, null);
                    
                    // 插入新文字
                    document.execCommand('insertText', false, '{escaped}');
                    
                    // 触发事件
                    input.dispatchEvent(new InputEvent('input', {{ 
                        bubbles: true,
                        cancelable: true
                    }}));
                    
                    return JSON.stringify({{ success: true }});
                }})()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }}
        return JSON.stringify({{ success: false }});
    }})()
    '''
    
    await ws.send(input_code)
    response = await ws.recv()
    result = json.loads(response)
    
    if result.get('success'):
        info = json.loads(result['result'])
        if info.get('success'):
            print('✅ 输入命令执行成功')
        else:
            print('❌ 输入失败')
            await ws.close()
            return
    else:
        print(f'❌ 失败: {result.get("error")}')
        await ws.close()
        return
    
    # 步骤 2: 等待一会儿让编辑器更新
    print('步骤 2: 等待编辑器更新...')
    await asyncio.sleep(0.5)
    print('✅ 等待完成')
    
    # 步骤 3: 读取当前内容
    print('步骤 3: 验证内容...')
    verify_code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({ found: false });
                    
                    return JSON.stringify({
                        found: true,
                        innerText: input.innerText,
                        textContent: input.textContent,
                        innerHTML: input.innerHTML,
                        childNodes: input.childNodes.length,
                        firstChildHTML: input.firstChild ? input.firstChild.innerHTML : null
                    });
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return JSON.stringify({ found: false });
    })()
    '''
    
    await ws.send(verify_code)
    response = await ws.recv()
    result = json.loads(response)
    
    if result.get('success'):
        info = json.loads(result['result'])
        if info.get('found'):
            print('✅ 输入框状态:')
            print(f'   innerText: "{info.get("innerText", "")}"')
            print(f'   textContent: "{info.get("textContent", "")}"')
            print(f'   innerHTML: {info.get("innerHTML", "")}')
            print(f'   childNodes: {info.get("childNodes")}')
            if info.get('firstChildHTML'):
                print(f'   第一个子节点: {info.get("firstChildHTML")}')
            print()
            
            # 判断是否成功
            content = info.get('innerText') or info.get('textContent') or ''
            if text in content or content.strip() == text.strip():
                print('   ✅ 内容匹配！输入成功！')
            elif info.get('firstChildHTML') and text in info.get('firstChildHTML'):
                print('   ✅ 内容在 HTML 中找到！输入成功！')
            else:
                print('   ⚠️  内容不完全匹配')
                print(f'   期望: "{text}"')
                print(f'   实际: "{content}"')
        else:
            print('❌ 未找到输入框')
    else:
        print(f'❌ 验证失败: {result.get("error")}')
    
    print()
    print('=' * 80)
    print('💡 请在 Cursor 窗口中目视确认输入框是否显示了文字')
    print('=' * 80)
    print()
    
    await ws.close()
    print('👋 断开连接')


async def main():
    """主函数"""
    
    if len(sys.argv) < 2:
        # 默认测试文字
        text = "Hello from Ortensia! 🚀"
    else:
        text = ' '.join(sys.argv[1:])
    
    await test_input(text)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  测试被中断')
        sys.exit(0)

