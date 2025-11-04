#!/usr/bin/env python3
"""
测试 Cursor DOM 操作封装

这个脚本验证 cursor_dom_operations.js 的功能
"""

import asyncio
import websockets
import json
import sys


async def test_dom_operations():
    """测试 DOM 操作封装"""
    
    print('=' * 70)
    print('  🧪 测试 Cursor DOM 操作封装')
    print('=' * 70)
    print()
    
    server_url = 'ws://localhost:9876'
    
    print(f'🔗 连接到 Cursor Hook: {server_url}')
    
    try:
        async with websockets.connect(server_url) as ws:
            print('✅ 已连接\n')
            
            # 测试 1: 加载 DOM 操作模块
            print('━' * 70)
            print('  测试 1: 加载 DOM 操作模块')
            print('━' * 70)
            
            # 读取 cursor_dom_operations.js
            with open('cursor_dom_operations.js', 'r') as f:
                dom_ops_code = f.read()
            
            load_code = f'''
            (async () => {{
                const {{ BrowserWindow }} = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {{
                    const code = `
                        {dom_ops_code}
                        
                        // 返回版本信息
                        JSON.stringify(window.CursorDOM.getVersion());
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }}
                return JSON.stringify({{ error: "没有窗口" }});
            }})()
            '''
            
            await ws.send(load_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                version_info = json.loads(response['result'])
                print(f'✅ DOM 操作模块已加载')
                print(f'   版本: {version_info["version"]}')
                print(f'   日期: {version_info["date"]}')
                print(f'   功能: {version_info["operations"]}')
            else:
                print(f'❌ 加载失败: {response.get("error")}')
                return False
            
            print()
            
            # 测试 2: 测试选择器
            print('━' * 70)
            print('  测试 2: 测试选择器')
            print('━' * 70)
            
            test_selectors_code = '''
            (async () => {
                const { BrowserWindow } = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const code = `
                        JSON.stringify(window.CursorDOM.testSelectors());
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }
                return JSON.stringify({ error: "没有窗口" });
            })()
            '''
            
            await ws.send(test_selectors_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                selectors = json.loads(response['result'])
                
                print('📊 Composer 选择器:')
                for key, info in selectors['composer'].items():
                    status = '✅' if info['found'] else '❌'
                    print(f'   {status} {key}: {info["selector"]}')
                
                print()
            else:
                print(f'❌ 测试失败: {response.get("error")}')
            
            print()
            
            # 测试 3: 查找输入框
            print('━' * 70)
            print('  测试 3: 查找输入框')
            print('━' * 70)
            
            find_input_code = '''
            (async () => {
                const { BrowserWindow } = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const code = `
                        JSON.stringify(window.CursorDOM.composer.findInputElement());
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }
                return JSON.stringify({ error: "没有窗口" });
            })()
            '''
            
            await ws.send(find_input_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                result = json.loads(response['result'])
                if result['success']:
                    print(f'✅ 输入框已找到')
                else:
                    print(f'❌ 输入框未找到: {result.get("error")}')
                    print(f'   提示: {result.get("message", "")}')
            
            print()
            
            # 测试 4: 输入文字
            print('━' * 70)
            print('  测试 4: 输入文字')
            print('━' * 70)
            
            test_text = "测试 DOM 操作封装 🚀"
            input_code = f'''
            (async () => {{
                const {{ BrowserWindow }} = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {{
                    const code = `
                        JSON.stringify(window.CursorDOM.composer.inputText({json.dumps(test_text)}));
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }}
                return JSON.stringify({{ error: "没有窗口" }});
            }})()
            '''
            
            await ws.send(input_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                result = json.loads(response['result'])
                if result['success']:
                    print(f'✅ 文字输入成功')
                    print(f'   消息: {result.get("message")}')
                    print(f'   数据: {result.get("data")}')
                else:
                    print(f'❌ 输入失败: {result.get("error")}')
            
            print()
            
            # 测试 5: 获取输入框内容
            print('━' * 70)
            print('  测试 5: 获取输入框内容')
            print('━' * 70)
            
            await asyncio.sleep(0.5)  # 等待 UI 更新
            
            get_content_code = '''
            (async () => {
                const { BrowserWindow } = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const code = `
                        JSON.stringify(window.CursorDOM.composer.getInputContent());
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }
                return JSON.stringify({ error: "没有窗口" });
            })()
            '''
            
            await ws.send(get_content_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                result = json.loads(response['result'])
                if result['success']:
                    data = result['data']
                    print(f'✅ 内容获取成功')
                    print(f'   innerText: "{data["innerText"]}"')
                    print(f'   长度: {data["length"]}')
                    print(f'   是否为空: {data["isEmpty"]}')
                    
                    # 验证内容
                    if data['innerText'] == test_text:
                        print(f'   ✅ 内容匹配！')
                    else:
                        print(f'   ⚠️  内容不匹配')
                        print(f'      期望: {test_text}')
                        print(f'      实际: {data["innerText"]}')
                else:
                    print(f'❌ 获取失败: {result.get("error")}')
            
            print()
            
            # 测试 6: 清空输入框
            print('━' * 70)
            print('  测试 6: 清空输入框')
            print('━' * 70)
            
            clear_code = '''
            (async () => {
                const { BrowserWindow } = await import("electron");
                const windows = BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const code = `
                        JSON.stringify(window.CursorDOM.composer.clearInput());
                    `;
                    return await windows[0].webContents.executeJavaScript(code);
                }
                return JSON.stringify({ error: "没有窗口" });
            })()
            '''
            
            await ws.send(clear_code)
            response_str = await ws.recv()
            response = json.loads(response_str)
            
            if response['success']:
                result = json.loads(response['result'])
                if result['success']:
                    print(f'✅ {result.get("message")}')
                else:
                    print(f'❌ 清空失败: {result.get("error")}')
            
            print()
            
            # 测试完成
            print('=' * 70)
            print('  ✅ 所有测试完成！')
            print('=' * 70)
            print()
            
            return True
    
    except ConnectionRefusedError:
        print('❌ 连接被拒绝')
        print('💡 请确保:')
        print('   1. Cursor Hook V8 已安装并重启 Cursor')
        print('   2. 本地 Server (9876) 正在运行')
        return False
    
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_dom_operations()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  测试被中断')
        sys.exit(1)

