#!/usr/bin/env python3
"""诊断 DOM 结构 - 查找实际的按钮和元素"""

import asyncio
import websockets
import json


async def diagnose():
    print('=' * 70)
    print('  🔍 DOM 结构诊断')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 1. 查找所有 button 元素
        print('1. 查找所有 button 元素')
        print('─' * 70)
        
        code1 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const buttons = document.querySelectorAll('button');
                        const buttonInfo = Array.from(buttons).slice(0, 10).map((btn, idx) => ({
                            index: idx,
                            type: btn.type || 'none',
                            className: btn.className,
                            innerText: (btn.innerText || '').substring(0, 50),
                            ariaLabel: btn.getAttribute('aria-label'),
                            disabled: btn.disabled
                        }));
                        return JSON.stringify(buttonInfo, null, 2);
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify([]);
        })()
        '''
        
        await ws.send(code1)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            buttons = json.loads(response['result'])
            print(f'找到 {len(buttons)} 个按钮（显示前 10 个）:\n')
            for btn in buttons:
                print(f"  [{btn['index']}] type=\"{btn['type']}\"")
                print(f"      class=\"{btn['className']}\"")
                print(f"      text=\"{btn['innerText']}\"")
                print(f"      aria-label=\"{btn['ariaLabel']}\"")
                print(f"      disabled={btn['disabled']}")
                print()
        
        # 2. 查找所有包含 "submit" 的元素
        print('2. 查找包含 "submit" 的元素')
        print('─' * 70)
        
        code2 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const selectors = [
                            '[type="submit"]',
                            'button[type="submit"]',
                            '[aria-label*="submit" i]',
                            '[aria-label*="send" i]',
                            '.submit-button',
                            '.send-button'
                        ];
                        
                        const results = {};
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            results[selector] = el ? {
                                found: true,
                                className: el.className,
                                innerText: el.innerText || el.textContent || ''
                            } : { found: false };
                        }
                        
                        return JSON.stringify(results, null, 2);
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify({});
        })()
        '''
        
        await ws.send(code2)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            results = json.loads(response['result'])
            for selector, info in results.items():
                if info['found']:
                    print(f"  ✅ {selector}")
                    print(f"     class: {info['className']}")
                    print(f"     text: {info['innerText'][:50]}")
                else:
                    print(f"  ❌ {selector}")
            print()
        
        # 3. 查找 Composer 容器及其子元素
        print('3. 查找 Composer 容器结构')
        print('─' * 70)
        
        code3 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const selectors = [
                            '.composer',
                            '.ai-panel',
                            '.chat-panel',
                            '[class*="composer" i]',
                            '[class*="chat" i]'
                        ];
                        
                        const results = {};
                        for (const selector of selectors) {
                            const el = document.querySelector(selector);
                            if (el) {
                                results[selector] = {
                                    found: true,
                                    className: el.className,
                                    childrenCount: el.children.length,
                                    hasInput: !!el.querySelector('.aislash-editor-input'),
                                    hasButton: !!el.querySelector('button')
                                };
                            } else {
                                results[selector] = { found: false };
                            }
                        }
                        
                        return JSON.stringify(results, null, 2);
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
            results = json.loads(response['result'])
            for selector, info in results.items():
                if info['found']:
                    print(f"  ✅ {selector}")
                    print(f"     children: {info['childrenCount']}")
                    print(f"     hasInput: {info['hasInput']}")
                    print(f"     hasButton: {info['hasButton']}")
                else:
                    print(f"  ❌ {selector}")
            print()
        
        print('=' * 70)
        print('  ✅ 诊断完成')
        print('=' * 70)


if __name__ == '__main__':
    asyncio.run(diagnose())

