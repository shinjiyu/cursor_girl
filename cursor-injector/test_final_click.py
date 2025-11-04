#!/usr/bin/env python3
"""
最终测试：点击正确的子元素并验证 Agent 是否启动
"""

import asyncio
import websockets
import json


async def test_final():
    print('=' * 70)
    print('  🎯 最终点击测试')
    print('=' * 70)
    print()
    
    ws_url = 'ws://localhost:9876'
    
    async with websockets.connect(ws_url) as ws:
        print('✅ 已连接\n')
        
        # 步骤 1: 清空并输入新文字
        print('步骤 1: 清空并输入新文字')
        print('─' * 70)
        
        test_text = "用 Python 实现冒泡排序"
        
        code1 = f'''
        (async () => {{
            const {{ BrowserWindow }} = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {{
                const code = `
                    (function() {{
                        const input = document.querySelector('.aislash-editor-input');
                        if (!input) return JSON.stringify({{ success: false }});
                        
                        input.focus();
                        
                        // 清空
                        const sel = window.getSelection();
                        const range = document.createRange();
                        range.selectNodeContents(input);
                        sel.removeAllRanges();
                        sel.addRange(range);
                        document.execCommand('delete', false, null);
                        
                        // 输入
                        document.execCommand('insertText', false, '{test_text}');
                        input.dispatchEvent(new InputEvent('input', {{ bubbles: true }}));
                        
                        return JSON.stringify({{ success: true, text: '{test_text}' }});
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
                print(f'✅ 已输入: "{result["text"]}"')
            else:
                print('❌ 输入失败')
                return
        else:
            print(f'❌ WebSocket 错误: {response.get("error")}')
            return
        
        print()
        print('⏳ 等待 1.5 秒让上箭头按钮出现...')
        await asyncio.sleep(1.5)
        print()
        
        # 步骤 2: 点击子元素 .anysphere-icon-button
        print('步骤 2: 点击 .anysphere-icon-button 子元素')
        print('─' * 70)
        
        code2 = '''
        (async () => {
            const { BrowserWindow } = await import("electron");
            const windows = BrowserWindow.getAllWindows();
            if (windows.length > 0) {
                const code = `
                    (function() {
                        const button = document.querySelector('.send-with-mode > .anysphere-icon-button');
                        
                        if (!button) {
                            return JSON.stringify({ 
                                success: false, 
                                error: '子元素未找到' 
                            });
                        }
                        
                        // 获取按钮信息
                        const icon = button.querySelector('.codicon');
                        const iconClass = icon ? icon.className : 'unknown';
                        
                        console.log('准备点击子元素:', button.className);
                        console.log('图标类:', iconClass);
                        
                        button.click();
                        
                        console.log('已点击');
                        
                        return JSON.stringify({ 
                            success: true,
                            buttonClass: button.className,
                            iconClass: iconClass
                        });
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
                print('✅ 点击成功')
                print(f"   按钮类: {result['buttonClass'][:50]}...")
                print(f"   图标类: {result['iconClass']}")
            else:
                print(f'❌ 点击失败: {result.get("error")}')
                return
        else:
            print(f'❌ WebSocket 错误: {response.get("error")}')
            return
        
        print()
        
        # 步骤 3: 立即检查状态（点击后）
        print('步骤 3: 立即检查 Agent 状态')
        print('─' * 70)
        
        for i in range(5):
            await asyncio.sleep(1)
            print(f'\n检查 #{i+1} ({i+1} 秒后)...')
            
            code3 = '''
            (async () => {
                const { BrowserWindow } = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const code = `
                        (function() {
                            // 检查输入框内容（如果清空了说明提交成功）
                            const input = document.querySelector('.aislash-editor-input');
                            const inputContent = input ? (input.innerText || input.textContent || '').trim() : '';
                            
                            // 检查 loading 指示器
                            const loadingElements = document.querySelectorAll('[class*="loading" i]');
                            const visibleLoading = Array.from(loadingElements).filter(el => el.offsetParent !== null);
                            
                            // 检查是否有 Agent 响应
                            const responseElements = document.querySelectorAll('[class*="response" i], [class*="message" i], [class*="answer" i]');
                            const visibleResponses = Array.from(responseElements).filter(el => el.offsetParent !== null);
                            
                            return JSON.stringify({ 
                                inputCleared: inputContent.length === 0,
                                inputContent: inputContent.substring(0, 50),
                                loadingCount: visibleLoading.length,
                                responseCount: visibleResponses.length,
                                isWorking: visibleLoading.length > 0
                            });
                        })()
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }
                return JSON.stringify({ isWorking: false });
            })()
            '''
            
            await ws.send(code3)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                result = json.loads(response['result'])
                print(f"  输入框已清空: {result['inputCleared']}")
                if not result['inputCleared']:
                    print(f"  输入框内容: '{result['inputContent']}'")
                print(f"  Loading 指示器: {result['loadingCount']} 个")
                print(f"  响应元素: {result['responseCount']} 个")
                print(f"  Agent 工作中: {result['isWorking']}")
                
                if result['isWorking']:
                    print('\n✅ Agent 已开始工作！')
                    break
                elif result['inputCleared']:
                    print('\n✅ 输入框已清空（提交成功），但暂未检测到 loading...')
            
            if i == 4:
                print('\n❓ 5 秒后仍未检测到明显的工作状态')
        
        print()
        print('=' * 70)


if __name__ == '__main__':
    try:
        asyncio.run(test_final())
    except KeyboardInterrupt:
        print('\n\n⚠️  已取消')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()

