#!/usr/bin/env python3
"""测试脚本：手动测试输入文本到 Cursor"""

import asyncio
import websockets
import json
import time

async def manual_input_test():
    """手动测试输入文本"""
    uri = "ws://localhost:8765"
    
    test_text = "【测试】这是通过脚本输入的文本"
    
    # 生成输入文本的 JavaScript 代码（与服务器相同）
    js_code = f"""
(function() {{
    try {{
        // 查找所有可能的输入框
        const selectors = [
            'div[contenteditable="true"][aria-label*="composer"]',
            'div[contenteditable="true"][role="textbox"]',
            'div.composer-input',
            'textarea[placeholder*="Ask"]',
            'div[contenteditable="true"]'
        ];
        
        let inputElement = null;
        let foundWith = null;
        
        for (let selector of selectors) {{
            const elem = document.querySelector(selector);
            if (elem) {{
                inputElement = elem;
                foundWith = selector;
                break;
            }}
        }}
        
        if (!inputElement) {{
            return JSON.stringify({{
                success: false,
                error: '找不到输入框',
                tried: selectors
            }});
        }}
        
        // 设置输入框内容
        const textToSet = {json.dumps(test_text)};
        
        if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {{
            inputElement.value = textToSet;
            inputElement.dispatchEvent(new Event('input', {{ bubbles: true }}));
            inputElement.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }} else if (inputElement.contentEditable === 'true') {{
            // 对于 contenteditable div，尝试多种方式
            inputElement.textContent = textToSet;
            inputElement.innerText = textToSet;
            
            // 触发多个事件
            inputElement.dispatchEvent(new Event('input', {{ bubbles: true }}));
            inputElement.dispatchEvent(new Event('change', {{ bubbles: true }}));
            inputElement.dispatchEvent(new KeyboardEvent('keydown', {{ bubbles: true }}));
            inputElement.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true }}));
        }}
        
        // 聚焦输入框
        inputElement.focus();
        
        // 读取当前内容验证
        let currentContent = '';
        if (inputElement.tagName === 'TEXTAREA' || inputElement.tagName === 'INPUT') {{
            currentContent = inputElement.value;
        }} else {{
            currentContent = inputElement.textContent || inputElement.innerText;
        }}
        
        return JSON.stringify({{
            success: true,
            message: '文本输入操作已完成',
            foundWith: foundWith,
            elementTag: inputElement.tagName,
            elementClass: inputElement.className,
            setContent: textToSet,
            currentContent: currentContent,
            contentMatches: currentContent === textToSet
        }});
    }} catch (error) {{
        return JSON.stringify({{
            success: false,
            error: error.message,
            stack: error.stack
        }});
    }}
}})()
"""
    
    client_id = "test-manual-input-" + str(int(time.time()))
    request_id = "manual_" + str(int(time.time()))
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 连接到中央服务器: {uri}")
            print(f"📝 测试文本: {test_text}\n")
            
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
            response = await websocket.recv()
            print(f"✅ 注册成功\n")
            
            # 2. 发送 execute_js 命令
            execute_msg = {
                "type": "execute_js",
                "from": client_id,
                "to": "inject-54396",
                "timestamp": int(time.time()),
                "payload": {
                    "code": js_code,
                    "request_id": request_id
                }
            }
            await websocket.send(json.dumps(execute_msg))
            print(f"📤 发送输入文本命令...\n")
            
            # 3. 等待执行结果
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get('type') == 'execute_js_result':
                payload = result.get('payload', {})
                if payload.get('success'):
                    input_result = payload.get('result', {})
                    if isinstance(input_result, str):
                        input_result = json.loads(input_result)
                    
                    print(f"📊 执行结果:")
                    print(f"  状态: {'✅ 成功' if input_result.get('success') else '❌ 失败'}")
                    
                    if input_result.get('success'):
                        print(f"  找到输入框: {input_result.get('foundWith')}")
                        print(f"  元素标签: {input_result.get('elementTag')}")
                        print(f"  元素类名: {input_result.get('elementClass', '(无)')[:50]}")
                        print(f"  设置的内容: {input_result.get('setContent', '')[:50]}")
                        print(f"  当前内容: {input_result.get('currentContent', '')[:50]}")
                        print(f"  内容匹配: {'✅ 是' if input_result.get('contentMatches') else '❌ 否'}")
                        
                        if not input_result.get('contentMatches'):
                            print(f"\n⚠️  警告：设置的内容与读取的内容不匹配！")
                            print(f"  这可能是因为 Cursor 使用了复杂的编辑器（如 Lexical）")
                            print(f"  需要使用更高级的 DOM 操作方法")
                    else:
                        print(f"  错误: {input_result.get('error')}")
                        if input_result.get('tried'):
                            print(f"  尝试的选择器: {input_result['tried']}")
                else:
                    print(f"❌ 执行失败: {payload.get('error')}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(manual_input_test())










