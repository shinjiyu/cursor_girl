#!/usr/bin/env python3
"""
从 Cursor DOM 中可靠提取 conversation_id

基于发现：conversation_id 存在于 markdown section 的 ID 中
格式：markdown-section-{UUID}-{index}
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
                // 查找所有 markdown section
                const sections = document.querySelectorAll('[id^="markdown-section-"]');
                
                if (sections.length === 0) {
                    return JSON.stringify({ error: 'No markdown sections found' });
                }
                
                // 获取第一个 section（所有 section 的 conversation_id 应该相同）
                const firstSection = sections[0];
                
                // 提取 UUID
                // 格式: markdown-section-{UUID}-{index}
                // 移除最后的 -数字 部分，剩下的就是 conversation_id
                const idParts = firstSection.id.split('-');
                
                // markdown-section-{8chars}-{4chars}-{4chars}-{4chars}-{12chars}-{index}
                // 移除 'markdown', 'section', 和最后的 index
                if (idParts.length >= 7) {
                    // 重新组合 UUID 部分
                    const uuid = idParts.slice(2, 7).join('-');
                    
                    return JSON.stringify({
                        conversation_id: uuid,
                        total_sections: sections.length,
                        first_section_id: firstSection.id,
                        last_section_id: sections[sections.length - 1].id,
                        parsed: {
                            all_parts: idParts,
                            uuid_parts: idParts.slice(2, 7)
                        }
                    });
                }
                
                return JSON.stringify({
                    error: 'Could not extract UUID',
                    sample_id: firstSection.id,
                    parts: idParts
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
    print("🔍 提取 Cursor conversation_id")
    print("=" * 80)
    print()
    
    result = await get_conversation_id()
    
    if 'error' in result:
        print(f"❌ 错误: {result['error']}")
    elif 'conversation_id' in result:
        print(f"✅ 成功提取 conversation_id!")
        print()
        print(f"📋 Conversation ID: {result['conversation_id']}")
        print(f"📊 总共 {result['total_sections']} 个 markdown section")
        print()
        print("示例:")
        print(f"  第一个: {result['first_section_id']}")
        print(f"  最后一个: {result['last_section_id']}")
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

