#!/usr/bin/env python3
"""
使用自定义选择器测试点击

使用方法：
1. 在 Cursor 中打开 DevTools (Help → Toggle Developer Tools)
2. 输入一些文字到 Composer
3. 使用元素选择器找到提交按钮
4. 复制它的选择器（右键 → Copy → Copy selector）
5. 运行这个脚本并输入选择器
"""

import asyncio
import websockets
import json
import sys


async def test_selector(selector):
    """测试指定的选择器"""
    print('=' * 70)
    print(f'  测试选择器: {selector}')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 步骤 1: 查找元素
        print('步骤 1: 查找元素')
        print('─' * 70)
        
        # 转义选择器中的特殊字符
        escaped_selector = selector.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        
        code1 = f'''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `
                    (function() {{
                        const element = document.querySelector(\`{escaped_selector}\`);
                        
                        if (!element) {{
                            return JSON.stringify({{ 
                                found: false,
                                error: '元素未找到'
                            }});
                        }}
                        
                        return JSON.stringify({{ 
                            found: true,
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id,
                            text: (element.innerText || element.textContent || '').substring(0, 50),
                            visible: element.offsetParent !== null,
                            disabled: element.disabled,
                            type: element.type || 'N/A'
                        }});
                    }})()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }}
            return JSON.stringify({{ found: false }});
        }})()
        '''
        
        await ws.send(code1)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if not response['success']:
            print(f"❌ WebSocket 错误: {response.get('error')}")
            return False
        
        result = json.loads(response['result'])
        
        if not result['found']:
            print(f"❌ {result.get('error')}")
            return False
        
        print('✅ 元素已找到:')
        print(f"   标签: {result['tagName']}")
        print(f"   类名: {result['className']}")
        print(f"   ID: {result['id'] or '(无)'}")
        print(f"   文本: {result['text']}")
        print(f"   可见: {result['visible']}")
        print(f"   禁用: {result.get('disabled', 'N/A')}")
        print(f"   类型: {result.get('type', 'N/A')}")
        print()
        
        if not result['visible']:
            print('⚠️  警告: 元素不可见！')
            print()
        
        # 步骤 2: 点击元素
        print('步骤 2: 点击元素')
        print('─' * 70)
        
        code2 = f'''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `
                    (function() {{
                        const element = document.querySelector(\`{escaped_selector}\`);
                        
                        if (!element) {{
                            return JSON.stringify({{ success: false, error: '元素未找到' }});
                        }}
                        
                        console.log('准备点击:', element);
                        element.click();
                        console.log('已点击');
                        
                        return JSON.stringify({{ 
                            success: true,
                            message: '已点击元素'
                        }});
                    }})()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }}
            return JSON.stringify({{ success: false }});
        }})()
        '''
        
        await ws.send(code2)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if not response['success']:
            print(f"❌ WebSocket 错误: {response.get('error')}")
            return False
        
        result = json.loads(response['result'])
        
        if result['success']:
            print('✅ 点击成功')
        else:
            print(f"❌ 点击失败: {result.get('error')}")
            return False
        
        print()
        
        # 步骤 3: 等待并检查状态
        print('步骤 3: 检查 Agent 状态')
        print('─' * 70)
        print('等待 2 秒...')
        await asyncio.sleep(2)
        
        code3 = '''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `
                    (function() {{
                        // 检查多种可能的 loading 指示器
                        const selectors = [
                            '[class*="loading" i]',
                            '[class*="thinking" i]',
                            '[class*="working" i]',
                            '.spinner',
                            '[aria-busy="true"]'
                        ];
                        
                        let foundElements = [];
                        for (const sel of selectors) {{
                            const elements = document.querySelectorAll(sel);
                            elements.forEach(el => {{
                                if (el.offsetParent !== null) {{
                                    foundElements.push({{
                                        selector: sel,
                                        className: el.className,
                                        visible: true
                                    }});
                                }}
                            }});
                        }}
                        
                        return JSON.stringify({{ 
                            isWorking: foundElements.length > 0,
                            foundCount: foundElements.length,
                            elements: foundElements
                        }});
                    }})()
                `;
                return await windows[0].webContents.executeJavaScript(code);
            }}
            return JSON.stringify({{ isWorking: false }});
        }})()
        '''
        
        await ws.send(code3)
        response_str = await ws.recv()
        response = json.loads(response_str)
        
        if response['success']:
            result = json.loads(response['result'])
            if result['isWorking']:
                print(f"✅ Agent 正在工作！（找到 {result['foundCount']} 个指示器）")
                print('   详情:')
                for el in result['elements'][:3]:  # 只显示前 3 个
                    print(f"   - {el['selector']}: {el['className'][:50]}")
            else:
                print(f"❌ Agent 未开始工作")
        
        print()
        print('=' * 70)
        return result['isWorking'] if response['success'] else False


async def main():
    if len(sys.argv) > 1:
        # 从命令行参数获取选择器
        selector = sys.argv[1]
        await test_selector(selector)
    else:
        # 交互式输入
        print()
        print('=' * 70)
        print('  自定义选择器测试工具')
        print('=' * 70)
        print()
        print('使用步骤:')
        print('1. 在 Cursor 中打开 DevTools (Help → Toggle Developer Tools)')
        print('2. 在 Composer 中输入一些文字')
        print('3. 使用元素选择器 (⬆️ 图标) 找到提交按钮')
        print('4. 右键点击元素 → Copy → Copy selector')
        print('5. 粘贴到下面')
        print()
        print('─' * 70)
        print()
        
        selector = input('请输入选择器: ').strip()
        
        if not selector:
            print('❌ 选择器不能为空')
            return
        
        print()
        await test_selector(selector)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  已取消')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()

