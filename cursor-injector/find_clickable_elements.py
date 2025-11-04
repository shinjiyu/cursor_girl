#!/usr/bin/env python3
"""查找所有可点击的元素，不仅仅是 button"""

import asyncio
import websockets
import json


async def find_clickable():
    print('=' * 70)
    print('  🔍 查找所有可点击元素')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        code = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const result = {
                            inputInfo: null,
                            clickableElements: []
                        };
                        
                        // 获取输入框信息和位置
                        const input = document.querySelector('.aislash-editor-input');
                        if (input) {
                            const rect = input.getBoundingClientRect();
                            result.inputInfo = {
                                content: (input.innerText || '').substring(0, 50),
                                length: (input.innerText || '').length,
                                position: {
                                    top: Math.round(rect.top),
                                    left: Math.round(rect.left),
                                    right: Math.round(rect.right),
                                    bottom: Math.round(rect.bottom),
                                    width: Math.round(rect.width),
                                    height: Math.round(rect.height)
                                }
                            };
                        }
                        
                        // 查找所有可能可点击的元素
                        const selectors = [
                            'button',
                            '[role="button"]',
                            '[onclick]',
                            'a',
                            '[class*="button" i]',
                            '[class*="btn" i]',
                            '[class*="clickable" i]',
                            '[class*="arrow" i]',
                            '[class*="send" i]',
                            '[class*="submit" i]'
                        ];
                        
                        const seen = new Set();
                        
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(el => {
                                if (el.offsetParent === null) return; // 跳过不可见的
                                
                                const key = el.tagName + el.className + (el.getAttribute('aria-label') || '');
                                if (seen.has(key)) return;
                                seen.add(key);
                                
                                const rect = el.getBoundingClientRect();
                                const svg = el.querySelector('svg');
                                
                                // 计算与输入框的距离
                                let distanceToInput = null;
                                if (input) {
                                    const inputRect = input.getBoundingClientRect();
                                    distanceToInput = Math.sqrt(
                                        Math.pow(rect.left - inputRect.right, 2) +
                                        Math.pow(rect.top - inputRect.top, 2)
                                    );
                                }
                                
                                result.clickableElements.push({
                                    tagName: el.tagName,
                                    className: el.className.substring(0, 100),
                                    innerText: (el.innerText || el.textContent || '').trim().substring(0, 50),
                                    ariaLabel: el.getAttribute('aria-label'),
                                    role: el.getAttribute('role'),
                                    hasSVG: !!svg,
                                    svgContent: svg ? svg.innerHTML.substring(0, 150) : null,
                                    position: {
                                        top: Math.round(rect.top),
                                        left: Math.round(rect.left),
                                        right: Math.round(rect.right),
                                        bottom: Math.round(rect.bottom),
                                        width: Math.round(rect.width),
                                        height: Math.round(rect.height)
                                    },
                                    distanceToInput: distanceToInput ? Math.round(distanceToInput) : null
                                });
                            });
                        }
                        
                        // 按距离排序
                        result.clickableElements.sort((a, b) => {
                            if (a.distanceToInput === null) return 1;
                            if (b.distanceToInput === null) return -1;
                            return a.distanceToInput - b.distanceToInput;
                        });
                        
                        return JSON.stringify(result, null, 2);
                    })()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }
            return JSON.stringify({});
        })()
        '''
        
        await ws.send(code)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            
            # 输入框
            if result.get('inputInfo'):
                info = result['inputInfo']
                print('📝 输入框:')
                print(f"   内容: \"{info['content']}\"")
                print(f"   位置: ({info['position']['left']}, {info['position']['top']}) → ({info['position']['right']}, {info['position']['bottom']})")
                print(f"   大小: {info['position']['width']} x {info['position']['height']}")
                print()
            
            # 可点击元素
            elements = result.get('clickableElements', [])
            print(f'🔘 找到 {len(elements)} 个可点击元素')
            print()
            print('按距离输入框排序（最近的最可能是提交按钮）:')
            print()
            
            for idx, el in enumerate(elements[:15]):  # 显示前15个
                marker = '⭐⭐⭐' if el['hasSVG'] else '   '
                print(f"{marker} [{idx}] <{el['tagName']}> {el['innerText'] or '(无文字)'}")
                print(f"       class=\"{el['className']}\"")
                if el['ariaLabel']:
                    print(f"       aria-label=\"{el['ariaLabel']}\"")
                if el['role']:
                    print(f"       role=\"{el['role']}\"")
                print(f"       位置=({el['position']['left']}, {el['position']['top']}) 大小={el['position']['width']}x{el['position']['height']}")
                if el['distanceToInput'] is not None:
                    print(f"       距离输入框: {el['distanceToInput']}px")
                if el['hasSVG']:
                    print(f"       ✅ 有 SVG: \"{el['svgContent'][:80]}...\"")
                print()
        
        print('=' * 70)
        print('  ✅ 查找完成')
        print('=' * 70)


if __name__ == '__main__':
    asyncio.run(find_clickable())

