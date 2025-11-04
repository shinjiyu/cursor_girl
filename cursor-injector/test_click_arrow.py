#!/usr/bin/env python3
"""测试点击上箭头按钮提交"""

import asyncio
import websockets
import json


async def test_click_arrow():
    print('=' * 70)
    print('  ⬆️  测试点击上箭头按钮')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 步骤 1: 清空并输入新文字
        print('步骤 1: 清空并输入新文字')
        print('─' * 70)
        
        test_text = "用 Python 实现二分查找"
        escaped_text = test_text.replace("'", "\\'")
        
        code1 = f'''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `
                    (function() {{
                        const input = document.querySelector('.aislash-editor-input');
                        if (!input) {{
                            return JSON.stringify({{ success: false, error: '输入框未找到' }});
                        }}
                        
                        input.focus();
                        
                        // 清空
                        const sel = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(input);
                        sel.removeAllRanges();
                        sel.addRange(range);
                        document.execCommand('delete', false, null);
                        
                        // 输入
                        document.execCommand('insertText', false, '{escaped_text}');
                        input.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                        
                        return JSON.stringify({{ success: true, text: '{escaped_text}' }});
                    }})()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }}
            return JSON.stringify({{ success: false }});
        }})()
        '''
        
        await ws.send(code1)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            if result['success']:
                print(f"✅ 文字已输入: \"{result['text']}\"")
            else:
                print(f"❌ {result['error']}")
                return
        
        print()
        print('⏳ 等待 0.5 秒...')
        await asyncio.sleep(0.5)
        print()
        
        # 步骤 2: 点击上箭头按钮
        print('步骤 2: 点击上箭头按钮 (.send-with-mode)')
        print('─' * 70)
        
        code2 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        // 尝试点击 send-with-mode
                        const sendButton = document.querySelector('.send-with-mode');
                        if (sendButton) {
                            sendButton.click();
                            return JSON.stringify({ 
                                success: true, 
                                message: '已点击 .send-with-mode',
                                className: sendButton.className
                            });
                        }
                        
                        // 备选：点击箭头图标
                        const arrow = document.querySelector('.codicon-arrow-up-two');
                        if (arrow) {
                            arrow.click();
                            return JSON.stringify({ 
                                success: true, 
                                message: '已点击 .codicon-arrow-up-two' 
                            });
                        }
                        
                        return JSON.stringify({ success: false, error: '未找到上箭头按钮' });
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify({ success: false });
        })()
        '''
        
        await ws.send(code2)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['error']}")
                return
        
        print()
        print('⏳ 等待 2 秒观察变化...')
        await asyncio.sleep(2)
        print()
        
        # 步骤 3: 检查提交结果
        print('步骤 3: 检查提交结果')
        print('─' * 70)
        
        code3 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const input = document.querySelector('.aislash-editor-input');
                        const loading = document.querySelector('[class*="loading" i]');
                        const spinner = document.querySelector('.spinner');
                        
                        return JSON.stringify({
                            inputContent: input ? (input.innerText || '').substring(0, 50) : null,
                            inputEmpty: input ? (input.innerText || '').trim().length === 0 : false,
                            hasLoading: !!loading && loading.offsetParent !== null,
                            hasSpinner: !!spinner && spinner.offsetParent !== null
                        });
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify({});
        })()
        '''
        
        await ws.send(code3)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            
            print('📊 检查结果:')
            print(f"   输入框内容: \"{result.get('inputContent', '')}\"")
            print(f"   输入框已清空: {result.get('inputEmpty')}")
            print(f"   有 loading 指示器: {result.get('hasLoading')}")
            print(f"   有 spinner: {result.get('hasSpinner')}")
            print()
            
            if result.get('inputEmpty') or result.get('hasLoading') or result.get('hasSpinner'):
                print('✅ 提交成功！Agent 正在工作！')
            else:
                print('⚠️  提交可能失败，或执行太快已完成')
        
        print()
        print('=' * 70)
        print('  ✅ 测试完成')
        print('=' * 70)


if __name__ == '__main__':
    asyncio.run(test_click_arrow())

