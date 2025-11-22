#!/usr/bin/env python3
"""
正确提取 Cursor conversation_id

从 composer-bottom-add-context-{UUID} 元素中提取
这是 Composer 底部的"添加上下文"按钮
"""

import asyncio
import json
import re
import websockets


async def get_conversation_id():
    """提取当前 Cursor 对话的 conversation_id"""
    
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return JSON.stringify({ error: 'No windows' });
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                // 查找 composer-bottom-add-context-{UUID} 元素
                const allElements = document.querySelectorAll('[id^="composer-bottom-add-context-"]');
                
                if (allElements.length === 0) {
                    return JSON.stringify({ error: 'No composer-bottom-add-context found' });
                }
                
                const results = [];
                
                allElements.forEach((el) => {
                    // 提取 UUID
                    // 格式: composer-bottom-add-context-{UUID}
                    const match = el.id.match(/composer-bottom-add-context-([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
                    
                    if (match && match[1]) {
                        results.push({
                            conversation_id: match[1],
                            element_id: el.id,
                            tag: el.tagName.toLowerCase(),
                            className: el.className
                        });
                    }
                });
                
                if (results.length > 0) {
                    // 返回第一个（应该只有一个当前活跃的对话）
                    return JSON.stringify({
                        conversation_id: results[0].conversation_id,
                        total_found: results.length,
                        all_conversations: results
                    });
                }
                
                return JSON.stringify({
                    error: 'Could not extract UUID',
                    found_elements: allElements.length
                });
            })()
        `);
        
        return result;
    })()
    """
    
    try:
        async with websockets.connect('ws://localhost:9876', open_timeout=5) as ws:
            await ws.send(code)
            response = await ws.recv()
            result = json.loads(response)
            
            if result.get('success'):
                data = json.loads(result.get('result', '{}'))
                return data
            else:
                return {"error": result.get('error', 'Unknown error')}
    except Exception as e:
        return {"error": str(e)}


async def main():
    print("=" * 80)
    print("🔍 提取 Cursor conversation_id (正确方法)")
    print("=" * 80)
    print()
    print("方法: 从 composer-bottom-add-context-{UUID} 元素提取")
    print()
    
    result = await get_conversation_id()
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
    elif 'conversation_id' in result:
        print(f"✅ 成功提取 conversation_id!")
        print()
        print(f"📋 Conversation ID: {result['conversation_id']}")
        print(f"📊 找到 {result['total_found']} 个 composer 元素")
        print()
        
        if result.get('all_conversations'):
            print("所有找到的对话:")
            for conv in result['all_conversations']:
                print(f"  🔑 {conv['conversation_id']}")
                print(f"     Element: {conv['element_id']}")
                print(f"     Tag: {conv['tag']}")
                print()
    else:
        print("⚠️  未找到 conversation_id")
        print(f"返回: {json.dumps(result, indent=2)}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

