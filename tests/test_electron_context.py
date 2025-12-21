#!/usr/bin/env python3
"""
测试 inject 的 Electron 上下文，确认能否访问 BrowserWindow
"""

import asyncio
import websockets
import json
import time

async def test_electron_context():
    uri = "ws://localhost:8765"
    
    async with websockets.connect(uri) as websocket:
        # 注册
        register_msg = {
            "type": "register",
            "from": "test-electron-ctx",
            "to": "server",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "client_types": ["command_client"]
            }
        }
        await websocket.send(json.dumps(register_msg))
        response = await websocket.recv()
        print("✅ 注册成功\n")
        
        # 测试 1：能否访问 electron 模块
        print("=" * 60)
        print("测试 1: 检查 electron 模块是否可用")
        print("=" * 60)
        
        test_code = """
        (async function() {
            try {
                const electron = await import('electron');
                return JSON.stringify({
                    success: true,
                    hasElectron: !!electron,
                    hasBrowserWindow: !!electron.BrowserWindow,
                    electronKeys: Object.keys(electron).slice(0, 10)
                });
            } catch (err) {
                return JSON.stringify({
                    success: false,
                    error: err.message,
                    stack: err.stack
                });
            }
        })()
        """
        
        execute_msg = {
            "type": "execute_js",
            "from": "test-electron-ctx",
            "to": "cursor_inject",
            "timestamp": int(time.time() * 1000),
            "payload": {
                "code": test_code,
                "request_id": "test_electron"
            }
        }
        
        await websocket.send(json.dumps(execute_msg))
        
        try:
            result = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            result_data = json.loads(result)
            
            if result_data.get('type') == 'execute_js_result':
                payload = result_data['payload']
                if payload.get('success'):
                    result_obj = json.loads(payload['result'])
                    if result_obj.get('success'):
                        print(f"✅ electron 模块可用")
                        print(f"   BrowserWindow: {result_obj['hasBrowserWindow']}")
                        print(f"   模块keys (前10个): {result_obj['electronKeys']}")
                    else:
                        print(f"❌ 错误: {result_obj.get('error')}")
                        print(f"   Stack: {result_obj.get('stack', '')[:200]}")
                else:
                    print(f"❌ 执行失败: {payload.get('error')}")
        except asyncio.TimeoutError:
            print("⏱️  超时")
        
        await asyncio.sleep(0.5)
        
        # 测试 2: 能否获取窗口列表
        print("\n" + "=" * 60)
        print("测试 2: 获取 BrowserWindow 列表")
        print("=" * 60)
        
        test_code = """
        (async function() {
            try {
                const electron = await import('electron');
                const windows = electron.BrowserWindow.getAllWindows();
                return JSON.stringify({
                    success: true,
                    windowCount: windows.length,
                    windowInfo: windows.map((w, i) => ({
                        index: i,
                        id: w.id,
                        title: w.getTitle(),
                        isVisible: w.isVisible(),
                        isFocused: w.isFocused()
                    }))
                });
            } catch (err) {
                return JSON.stringify({
                    success: false,
                    error: err.message,
                    stack: err.stack
                });
            }
        })()
        """
        
        execute_msg["payload"]["code"] = test_code
        execute_msg["payload"]["request_id"] = "test_windows"
        execute_msg["timestamp"] = int(time.time() * 1000)
        
        await websocket.send(json.dumps(execute_msg))
        
        try:
            result = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            result_data = json.loads(result)
            
            if result_data.get('type') == 'execute_js_result':
                payload = result_data['payload']
                if payload.get('success'):
                    result_obj = json.loads(payload['result'])
                    if result_obj.get('success'):
                        count = result_obj['windowCount']
                        print(f"✅ 找到 {count} 个窗口")
                        for w in result_obj['windowInfo']:
                            print(f"   Window {w['index']}: id={w['id']}, title=\"{w['title']}\", visible={w['isVisible']}, focused={w['isFocused']}")
                    else:
                        print(f"❌ 错误: {result_obj.get('error')}")
                else:
                    print(f"❌ 执行失败: {payload.get('error')}")
        except asyncio.TimeoutError:
            print("⏱️  超时")

if __name__ == "__main__":
    asyncio.run(test_electron_context())




























