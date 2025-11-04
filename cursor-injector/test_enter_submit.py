#!/usr/bin/env python3
"""测试通过 Enter 键提交"""

import asyncio
import websockets
import json
import time


async def test_enter_submit():
    print('=' * 70)
    print('  ⌨️  测试 Enter 键提交')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 步骤 1: 清空并输入新文字
        print('步骤 1: 清空并输入测试文字')
        print('─' * 70)
        
        test_text = "解释一下什么是装饰器模式"
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
                        
                        // 聚焦
                        input.focus();
                        
                        // 选中所有内容
                        const sel = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(input);
                        sel.removeAllRanges();
                        sel.addRange(range);
                        
                        // 删除
                        document.execCommand('delete', false, null);
                        
                        // 输入新文字
                        document.execCommand('insertText', false, '{escaped_text}');
                        
                        // 触发事件
                        input.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                        
                        return JSON.stringify({{ 
                            success: true, 
                            text: input.innerText || ''
                        }});
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
                print(f"✅ 文字已输入")
                print(f"   内容: \"{result['text']}\"")
            else:
                print(f"❌ {result['error']}")
                return
        
        print()
        print('⏳ 等待 0.5 秒...')
        await asyncio.sleep(0.5)
        print()
        
        # 步骤 2: 按下 Enter 键
        print('步骤 2: 按下 Enter 键')
        print('─' * 70)
        
        code2 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const input = document.querySelector('.aislash-editor-input');
                        if (!input) {
                            return JSON.stringify({ success: false, error: '输入框未找到' });
                        }
                        
                        input.focus();
                        
                        // 模拟按下 Enter 键
                        const enterEvent = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true
                        });
                        
                        input.dispatchEvent(enterEvent);
                        
                        return JSON.stringify({ success: true, message: '已发送 Enter 键' });
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
        
        print()
        print('⏳ 等待 2 秒观察 DOM 变化...')
        await asyncio.sleep(2)
        print()
        
        # 步骤 3: 检查提交后的状态
        print('步骤 3: 检查提交后的状态')
        print('─' * 70)
        
        code3 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const result = {
                            input: null,
                            thinkingIndicators: [],
                            stopButton: null,
                            isWorking: false
                        };
                        
                        // 检查输入框
                        const input = document.querySelector('.aislash-editor-input');
                        if (input) {
                            result.input = {
                                content: input.innerText || '',
                                length: (input.innerText || '').length,
                                isEmpty: (input.innerText || '').trim().length === 0
                            };
                        }
                        
                        // 检查思考中指示器
                        const thinkingSelectors = [
                            '.cursor-thinking',
                            '.agent-working',
                            '.thinking-indicator',
                            '[data-status="thinking"]',
                            '.loading',
                            '.spinner',
                            '[class*="loading" i]',
                            '[class*="thinking" i]'
                        ];
                        
                        for (const selector of thinkingSelectors) {
                            const el = document.querySelector(selector);
                            if (el) {
                                result.thinkingIndicators.push({
                                    selector: selector,
                                    visible: el.offsetParent !== null,
                                    className: el.className
                                });
                                if (el.offsetParent !== null) {
                                    result.isWorking = true;
                                }
                            }
                        }
                        
                        // 检查停止按钮
                        const stopSelectors = [
                            '.stop-generation-button',
                            '[aria-label="Stop generating"]',
                            '[aria-label*="stop" i]'
                        ];
                        
                        for (const selector of stopSelectors) {
                            const el = document.querySelector(selector);
                            if (el && !el.disabled && el.offsetParent !== null) {
                                result.stopButton = {
                                    selector: selector,
                                    className: el.className
                                };
                                result.isWorking = true;
                                break;
                            }
                        }
                        
                        return JSON.stringify(result, null, 2);
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
            
            print(f"📝 输入框:")
            if result['input']:
                print(f"   内容: \"{result['input']['content'][:50]}...\"" if len(result['input']['content']) > 50 else f"   内容: \"{result['input']['content']}\"")
                print(f"   为空: {result['input']['isEmpty']}")
            
            print()
            print(f"⚡ Agent 状态:")
            print(f"   正在工作: {result['isWorking']}")
            
            if result['thinkingIndicators']:
                print(f"\n   思考中指示器: {len(result['thinkingIndicators'])} 个")
                for ind in result['thinkingIndicators']:
                    if ind['visible']:
                        print(f"     ✅ {ind['selector']}")
            
            if result['stopButton']:
                print(f"\n   ✅ 停止按钮可用: {result['stopButton']['selector']}")
        
        print()
        print('=' * 70)
        if result.get('isWorking'):
            print('  ✅ 提交成功！Agent 正在工作！')
        else:
            print('  ⚠️  提交可能失败，或执行太快已完成')
        print('=' * 70)


if __name__ == '__main__':
    asyncio.run(test_enter_submit())

