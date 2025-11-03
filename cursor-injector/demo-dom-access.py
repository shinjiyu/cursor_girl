#!/usr/bin/env python3
"""
演示通过主进程访问渲染进程 DOM 的能力
"""

import asyncio
import json
import sys
import os

# 添加路径以导入客户端
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge', 'venv', 'lib', 'python3.13', 'site-packages'))

import websockets


async def main():
    """演示 DOM 访问"""
    
    print('🔗 连接到 Cursor...')
    try:
        ws = await websockets.connect('ws://localhost:9876')
        print('✅ 已连接\n')
    except Exception as e:
        print(f'❌ 连接失败: {e}')
        print('💡 请确保 Cursor 已启动且注入器已安装')
        return
    
    # 演示脚本列表
    demos = [
        ('📄 获取当前文件名', '''
            (async () => {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    return await windows[0].webContents.executeJavaScript("document.title");
                }
                return "no windows";
            })()
        '''),
        
        ('🔢 统计 DOM 元素数量', '''
            (async () => {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    return await windows[0].webContents.executeJavaScript(
                        "document.querySelectorAll('*').length"
                    );
                }
                return 0;
            })()
        '''),
        
        ('🎨 获取页面背景色', '''
            (async () => {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    return await windows[0].webContents.executeJavaScript(
                        "getComputedStyle(document.body).backgroundColor"
                    );
                }
                return "unknown";
            })()
        '''),
        
        ('📊 检查 VSCode API', '''
            (async () => {
                const electron = await import("electron");
                const windows = electron.BrowserWindow.getAllWindows();
                if (windows.length > 0) {
                    const hasVscode = await windows[0].webContents.executeJavaScript(
                        "typeof vscode !== 'undefined'"
                    );
                    return hasVscode ? '✅ VSCode API 可用' : '❌ VSCode API 不可用';
                }
                return "no windows";
            })()
        '''),
    ]
    
    print('=' * 70)
    print('  🧪 DOM 访问演示')
    print('=' * 70)
    print()
    
    for name, code in demos:
        print(f'{name}')
        try:
            await ws.send(code)
            response = await ws.recv()
            result = json.loads(response)
            
            if result.get('success'):
                print(f'  ➜ {result["result"]}\n')
            else:
                print(f'  ❌ 错误: {result.get("error")}\n')
        except Exception as e:
            print(f'  ❌ 异常: {e}\n')
    
    print('=' * 70)
    
    await ws.close()
    print('👋 断开连接')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  演示被中断')
        sys.exit(0)

