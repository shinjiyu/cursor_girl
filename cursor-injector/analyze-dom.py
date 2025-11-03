#!/usr/bin/env python3
"""
分析 Cursor 的 DOM 结构，查找 AI 输入框
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
    """分析 DOM 并查找输入框"""
    
    print('🔗 连接到 Cursor...')
    try:
        ws = await websockets.connect('ws://localhost:9876')
        print('✅ 已连接\n')
    except Exception as e:
        print(f'❌ 连接失败: {e}')
        return
    
    print('=' * 80)
    print('  🔍 DOM 结构分析')
    print('=' * 80)
    print()
    
    # 1. 查找包含 "Plan, @ for context" 的元素
    print('📝 步骤 1: 查找包含提示文字的输入框...')
    search_code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const allElements = Array.from(document.querySelectorAll('*'));
                    const found = [];
                    
                    allElements.forEach(el => {
                        const text = el.textContent || el.placeholder || el.value || '';
                        if (text.includes('Plan') || text.includes('@ for context')) {
                            found.push({
                                tag: el.tagName,
                                type: el.type || null,
                                id: el.id || null,
                                className: el.className || null,
                                placeholder: el.placeholder || null,
                                value: el.value || null,
                                contentEditable: el.contentEditable || null,
                                role: el.getAttribute('role') || null,
                                ariaLabel: el.getAttribute('aria-label') || null,
                                textContent: text.substring(0, 100)
                            });
                        }
                    });
                    
                    return JSON.stringify(found, null, 2);
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return "[]";
    })()
    '''
    
    try:
        await ws.send(search_code)
        response = await ws.recv()
        result = json.loads(response)
        
        if result.get('success'):
            elements = json.loads(result['result'])
            print(f'✅ 找到 {len(elements)} 个相关元素:\n')
            
            for i, el in enumerate(elements, 1):
                print(f'  [{i}] {el["tag"]}')
                if el.get('id'):
                    print(f'      ID: {el["id"]}')
                if el.get('className'):
                    print(f'      Class: {el["className"][:100]}')
                if el.get('placeholder'):
                    print(f'      Placeholder: {el["placeholder"]}')
                if el.get('role'):
                    print(f'      Role: {el["role"]}')
                if el.get('ariaLabel'):
                    print(f'      Aria-Label: {el["ariaLabel"]}')
                if el.get('contentEditable'):
                    print(f'      ContentEditable: {el["contentEditable"]}')
                print()
        else:
            print(f'❌ 查询失败: {result.get("error")}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    # 2. 查找所有 input 和 textarea
    print('\n📝 步骤 2: 查找所有输入元素...')
    input_code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const inputs = Array.from(document.querySelectorAll('input, textarea'));
                    const result = inputs.map(el => ({
                        tag: el.tagName,
                        type: el.type || null,
                        id: el.id || null,
                        className: el.className || null,
                        placeholder: el.placeholder || null,
                        name: el.name || null,
                        ariaLabel: el.getAttribute('aria-label') || null,
                        value: el.value ? '(有值)' : '(空)'
                    }));
                    return JSON.stringify(result, null, 2);
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return "[]";
    })()
    '''
    
    try:
        await ws.send(input_code)
        response = await ws.recv()
        result = json.loads(response)
        
        if result.get('success'):
            inputs = json.loads(result['result'])
            print(f'✅ 找到 {len(inputs)} 个输入元素:\n')
            
            for i, el in enumerate(inputs, 1):
                print(f'  [{i}] {el["tag"]} (type={el.get("type", "N/A")})')
                if el.get('id'):
                    print(f'      ID: {el["id"]}')
                if el.get('className'):
                    print(f'      Class: {el["className"][:100]}')
                if el.get('placeholder'):
                    print(f'      Placeholder: {el["placeholder"]}')
                if el.get('ariaLabel'):
                    print(f'      Aria-Label: {el["ariaLabel"]}')
                print()
        else:
            print(f'❌ 查询失败: {result.get("error")}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    # 3. 查找所有 contentEditable 元素
    print('\n📝 步骤 3: 查找所有可编辑元素 (contentEditable)...')
    editable_code = '''
    (async () => {
        const { BrowserWindow } = await import("electron");
        const windows = BrowserWindow.getAllWindows();
        if (windows.length > 0) {
            const code = `
                (function() {
                    const allElements = Array.from(document.querySelectorAll('[contenteditable="true"], [contenteditable="plaintext-only"]'));
                    const result = allElements.map(el => ({
                        tag: el.tagName,
                        id: el.id || null,
                        className: el.className || null,
                        contentEditable: el.contentEditable || null,
                        role: el.getAttribute('role') || null,
                        ariaLabel: el.getAttribute('aria-label') || null,
                        placeholder: el.getAttribute('data-placeholder') || el.getAttribute('placeholder') || null,
                        textContent: (el.textContent || '').substring(0, 100)
                    }));
                    return JSON.stringify(result, null, 2);
                })()
            `;
            return await windows[0].webContents.executeJavaScript(code);
        }
        return "[]";
    })()
    '''
    
    try:
        await ws.send(editable_code)
        response = await ws.recv()
        result = json.loads(response)
        
        if result.get('success'):
            editables = json.loads(result['result'])
            print(f'✅ 找到 {len(editables)} 个可编辑元素:\n')
            
            for i, el in enumerate(editables, 1):
                print(f'  [{i}] {el["tag"]}')
                if el.get('id'):
                    print(f'      ID: {el["id"]}')
                if el.get('className'):
                    print(f'      Class: {el["className"][:100]}')
                if el.get('role'):
                    print(f'      Role: {el["role"]}')
                if el.get('ariaLabel'):
                    print(f'      Aria-Label: {el["ariaLabel"]}')
                if el.get('placeholder'):
                    print(f'      Placeholder: {el["placeholder"]}')
                if el.get('contentEditable'):
                    print(f'      ContentEditable: {el["contentEditable"]}')
                if el.get('textContent') and el['textContent'].strip():
                    print(f'      内容: {el["textContent"][:50]}...')
                print()
        else:
            print(f'❌ 查询失败: {result.get("error")}')
    except Exception as e:
        print(f'❌ 异常: {e}')
    
    print('=' * 80)
    print()
    
    await ws.close()
    print('👋 断开连接')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n\n⚠️  分析被中断')
        sys.exit(0)

