#!/usr/bin/env python3
"""测试脚本：通过中央服务器读取 Cursor 输入框内容"""

import asyncio
import websockets
import json
import time

async def read_cursor_input():
    """通过中央服务器读取 Cursor 输入框内容"""
    uri = "ws://localhost:8765"
    
    # 生成读取输入框内容的 JavaScript 代码
    js_code = """(function() {
    try {
        var inputSelectors = [
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]'
        ];
        
        var inputElement = null;
        for (var i = 0; i < inputSelectors.length; i++) {
            var elem = document.querySelector(inputSelectors[i]);
            if (elem) {
                inputElement = elem;
                break;
            }
        }
        
        if (!inputElement) {
            return '{"success":false,"error":"找不到输入框"}';
        }
        
        var content = '';
        if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {
            content = inputElement.value;
        } else {
            content = inputElement.textContent || '';
        }
        
        return '{"success":true,"content":"' + content.replace(/"/g, '\\\\"').replace(/\\n/g, '\\\\n') + '","tag":"' + inputElement.tagName + '"}';
    } catch (error) {
        return '{"success":false,"error":"' + error.message + '"}';
    }
})()"""
    
    client_id = "test-read-input-" + str(int(time.time()))
    request_id = "read_" + str(int(time.time()))
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 连接到中央服务器: {uri}")
            
            # 1. 注册客户端
            register_msg = {
                "type": "register",
                "from": client_id,
                "to": "server",
                "timestamp": int(time.time()),
                "payload": {
                    "client_type": "command_client",
                    "platform": "test",
                    "pid": 0,
                    "version": "1.0.0"
                }
            }
            await websocket.send(json.dumps(register_msg))
            print(f"📤 发送注册消息")
            
            # 等待注册响应
            response = await websocket.recv()
            register_result = json.loads(response)
            print(f"📨 注册响应: {register_result.get('type')}")
            
            # 2. 发送 execute_js 命令
            execute_msg = {
                "type": "execute_js",
                "from": client_id,
                "to": "inject-54396",  # 从日志中获取的 inject ID
                "timestamp": int(time.time()),
                "payload": {
                    "code": js_code,
                    "request_id": request_id
                }
            }
            await websocket.send(json.dumps(execute_msg))
            print(f"📤 发送 execute_js 命令")
            
            # 3. 等待执行结果
            print(f"⏳ 等待执行结果...")
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"\n📨 收到响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('type') == 'execute_js_result':
                payload = result.get('payload', {})
                if payload.get('success'):
                    # 解析返回的 JSON
                    try:
                        input_result = json.loads(payload.get('result', '{}'))
                        print(f"\n📝 输入框内容:")
                        print(f"  状态: {'✅ 成功' if input_result.get('success') else '❌ 失败'}")
                        if input_result.get('content'):
                            print(f"  内容: {input_result['content']}")
                            print(f"  元素标签: {input_result.get('tag', 'unknown')}")
                        else:
                            print(f"  内容: (空)")
                        if input_result.get('error'):
                            print(f"  错误: {input_result['error']}")
                    except json.JSONDecodeError as e:
                        print(f"  原始结果: {payload.get('result')}")
                        print(f"  解析错误: {e}")
                else:
                    print(f"\n❌ 执行失败: {payload.get('error')}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(read_cursor_input())










