#!/usr/bin/env python3
"""
检查 AI 输入框的详细结构
"""

import asyncio
import json
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bridge', 'venv', 'lib', 'python3.13', 'site-packages'))

import websockets


async def inspect():
    """检查输入框"""
    
    print('🔗 连接到 Cursor...')
    ws = await websockets.connect('ws://localhost:9876')
    print('✅ 已连接\n')
    
    code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const input = document.querySelector('.aislash-editor-input');
                    if (!input) return JSON.stringify({ error: 'Not found' });
                    
                    return JSON.stringify({
                        tagName: input.tagName,
                        contentEditable: input.contentEditable,
                        innerHTML: input.innerHTML,
                        outerHTML: input.outerHTML.substring(0, 500),
                        innerText: input.innerText,
                        textContent: input.textContent,
                        childNodes: input.childNodes.length,
                        firstChild: input.firstChild ? {
                            nodeType: input.firstChild.nodeType,
                            nodeName: input.firstChild.nodeName,
                            nodeValue: input.firstChild.nodeValue,
                            innerHTML: input.firstChild.innerHTML
                        } : null,
                        attributes: Array.from(input.attributes).map(attr => ({
                            name: attr.name,
                            value: attr.value
                        })),
                        classList: Array.from(input.classList)
                    }, null, 2);
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return JSON.stringify({ error: 'No windows' });
    })()
    '''
    
    await ws.send(code)
    response = await ws.recv()
    result = json.loads(response)
    
    if result.get('success'):
        info = json.loads(result['result'])
        print('=' * 80)
        print('  📋 输入框详细信息')
        print('=' * 80)
        print()
        print(json.dumps(info, indent=2, ensure_ascii=False))
        print()
        print('=' * 80)
    else:
        print(f'❌ 失败: {result.get("error")}')
    
    await ws.close()


if __name__ == '__main__':
    asyncio.run(inspect())

