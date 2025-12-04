#!/usr/bin/env python3
"""验证命令是否在 Cursor 中执行"""

import asyncio
import websockets
import json
import time

async def verify_execution():
    """检查 Cursor 中是否有 Agent 响应"""
    uri = "ws://localhost:8765"
    
    # 生成读取 Agent 响应区域的 JavaScript 代码
    js_code = """
(function() {
    try {
        // 查找 Agent 响应区域
        const selectors = [
            '.composer-response',
            '[class*="response"]',
            '[class*="message"]',
            '[role="log"]',
            '.chat-message'
        ];
        
        let responseArea = null;
        for (let selector of selectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                responseArea = Array.from(elements);
                break;
            }
        }
        
        if (!responseArea || responseArea.length === 0) {
            return JSON.stringify({
                success: false,
                error: '找不到响应区域'
            });
        }
        
        // 获取最后几条响应的文本
        const lastResponses = responseArea.slice(-3).map(el => ({
            text: el.textContent.substring(0, 200),
            className: el.className
        }));
        
        return JSON.stringify({
            success: true,
            responseCount: responseArea.length,
            lastResponses: lastResponses
        });
    } catch (error) {
        return JSON.stringify({
            success: false,
            error: error.message
        });
    }
})()
"""
    
    client_id = "test-verify-" + str(int(time.time()))
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ 连接到中央服务器: {uri}\n")
            
            # 1. 注册
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
            
            # 2. 发送 execute_js
            execute_msg = {
                "type": "execute_js",
                "from": client_id,
                "to": "inject-54396",
                "timestamp": int(time.time()),
                "payload": {
                    "code": js_code,
                    "request_id": "verify_" + str(int(time.time()))
                }
            }
            await websocket.send(json.dumps(execute_msg))
            print(f"📤 发送查询命令...\n")
            
            # 3. 等待结果
            response = await websocket.recv()
            result = json.loads(response)
            
            if result.get('type') == 'execute_js_result':
                payload = result.get('payload', {})
                if payload.get('success'):
                    exec_result = payload.get('result', {})
                    if isinstance(exec_result, str):
                        exec_result = json.loads(exec_result)
                    
                    print(f"📊 Cursor 响应区域查询结果:")
                    print(f"  状态: {'✅ 成功' if exec_result.get('success') else '❌ 失败'}")
                    
                    if exec_result.get('success'):
                        print(f"  响应数量: {exec_result.get('responseCount', 0)}")
                        print(f"\n  最近的响应:")
                        for i, resp in enumerate(exec_result.get('lastResponses', []), 1):
                            print(f"\n  [{i}] {resp['text'][:100]}...")
                    else:
                        print(f"  错误: {exec_result.get('error')}")
                else:
                    print(f"❌ 执行失败: {payload.get('error')}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_execution())










