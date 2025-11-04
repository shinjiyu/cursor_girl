#!/usr/bin/env python3
"""使用 Cmd+I 唤出 Composer 并查找上箭头按钮"""

import asyncio
import websockets
import json


async def invoke_and_test():
    print('=' * 70)
    print('  ⌨️  使用 Cmd+I 唤出 Composer')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 步骤 1: 确保在 Editor tab
        print('步骤 1: 确保在 Editor tab')
        print('─' * 70)
        
        code1 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const buttons = document.querySelectorAll('.segmented-tab');
                        for (const btn of buttons) {
                            if (btn.innerText === 'Editor') {
                                if (!btn.classList.contains('active')) {
                                    btn.click();
                                    return JSON.stringify({ success: true, message: '已切换到 Editor' });
                                }
                                return JSON.stringify({ success: true, message: '已在 Editor' });
                            }
                        }
                        return JSON.stringify({ success: false, error: '未找到 Editor tab' });
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify({ success: false });
        })()
        '''
        
        await ws.send(code1)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            print(f"✅ {result.get('message', 'OK')}")
        
        print()
        await asyncio.sleep(0.5)
        
        # 步骤 2: 发送 Cmd+I
        print('步骤 2: 发送 Cmd+I 唤出 Composer')
        print('─' * 70)
        
        code2 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        // 聚焦窗口
                        window.focus();
                        
                        // 模拟 Cmd+I
                        const event = new KeyboardEvent('keydown', {
                            key: 'i',
                            code: 'KeyI',
                            keyCode: 73,
                            which: 73,
                            metaKey: true,  // macOS Cmd 键
                            bubbles: true,
                            cancelable: true
                        });
                        
                        document.dispatchEvent(event);
                        
                        return JSON.stringify({ success: true, message: '已发送 Cmd+I' });
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
            print(f"✅ {result.get('message', 'OK')}")
        
        print()
        print('⏳ 等待 2 秒让 Composer 出现...')
        await asyncio.sleep(2)
        print()
        
        # 步骤 3: 检查 Composer 是否出现
        print('步骤 3: 检查 Composer 和输入框')
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
                            composer: null,
                            buttons: []
                        };
                        
                        // 查找输入框
                        const input = document.querySelector('.aislash-editor-input');
                        if (input) {
                            result.input = {
                                found: true,
                                visible: input.offsetParent !== null,
                                isEmpty: (input.innerText || '').trim().length === 0,
                                focused: document.activeElement === input
                            };
                        }
                        
                        // 查找 composer 容器
                        const composerSelectors = ['.composer', '[class*="composer" i]'];
                        for (const selector of composerSelectors) {
                            const el = document.querySelector(selector);
                            if (el && el.offsetParent !== null) {
                                result.composer = {
                                    found: true,
                                    selector: selector,
                                    className: el.className
                                };
                                break;
                            }
                        }
                        
                        // 查找所有可见按钮
                        const allButtons = document.querySelectorAll('button');
                        allButtons.forEach(btn => {
                            if (btn.offsetParent !== null) {
                                const hasSVG = !!btn.querySelector('svg');
                                result.buttons.push({
                                    className: btn.className.substring(0, 80),
                                    innerText: (btn.innerText || btn.textContent || '').substring(0, 30),
                                    ariaLabel: btn.getAttribute('aria-label'),
                                    disabled: btn.disabled,
                                    hasSVG: hasSVG
                                });
                            }
                        });
                        
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
            
            # 输入框
            if result.get('input'):
                inp = result['input']
                print(f"✅ 输入框:")
                print(f"   可见: {inp['visible']}")
                print(f"   为空: {inp['isEmpty']}")
                print(f"   聚焦: {inp['focused']}")
            else:
                print(f"❌ 输入框: 未找到")
            
            print()
            
            # Composer
            if result.get('composer'):
                comp = result['composer']
                print(f"✅ Composer:")
                print(f"   选择器: {comp['selector']}")
                print(f"   class: {comp['className'][:50]}")
            else:
                print(f"❌ Composer: 未找到")
            
            print()
            
            # 按钮
            print(f"🔘 找到 {len(result.get('buttons', []))} 个可见按钮:")
            print()
            for idx, btn in enumerate(result.get('buttons', [])[:10]):  # 只显示前10个
                if btn['hasSVG']:  # 重点关注有 SVG 的按钮
                    print(f"  [{idx}] ⭐ {btn['innerText'] or '(无文字)'}")
                    print(f"      class=\"{btn['className']}\"")
                    print(f"      aria-label=\"{btn['ariaLabel']}\"")
                    print(f"      disabled={btn['disabled']}")
                    print(f"      has SVG=True")
                    print()
        
        print('=' * 70)
        print('  ✅ 检查完成')
        print('=' * 70)


if __name__ == '__main__':
    asyncio.run(invoke_and_test())

