#!/usr/bin/env python3
"""测试脚本：检查 Cursor 输入框的内容"""

import asyncio
import websockets
import json

async def check_cursor_input():
    """检查 Cursor 输入框的内容"""
    uri = "ws://localhost:9876"
    
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
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 连接到 Cursor inject: {uri}")
            
            # 直接发送 JavaScript 代码（不是 JSON）
            await websocket.send(js_code)
            print(f"📤 发送读取输入框命令")
            
            # 接收响应
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"\n📨 收到响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success') and 'result' in result:
                # 解析返回的 JSON
                try:
                    input_result = json.loads(result['result'])
                    print(f"\n📝 输入框内容:")
                    print(f"  状态: {'✅ 成功' if input_result.get('success') else '❌ 失败'}")
                    if input_result.get('content'):
                        print(f"  内容: {input_result['content']}")
                        print(f"  元素类型: {input_result.get('element_type', 'unknown')}")
                    else:
                        print(f"  内容: (空)")
                    if input_result.get('error'):
                        print(f"  错误: {input_result['error']}")
                except json.JSONDecodeError:
                    print(f"  原始结果: {result['result']}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(check_cursor_input())

