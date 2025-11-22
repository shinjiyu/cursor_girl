# Cursor conversation_id 正确提取方法

## 📋 总结

✅ **正确方法**: 从 `composer-bottom-add-context-{UUID}` 元素中提取 conversation_id

❌ **错误方法**: 从 markdown section ID 中提取（那些是消息/回复的 ID，不是 conversation ID）

## 🎯 正确位置

conversation_id 存在于 **Composer 底部的"添加上下文"按钮** 的 ID 中。

### 格式

```html
<div id="composer-bottom-add-context-{CONVERSATION_ID}">
```

### 实例

```html
<div id="composer-bottom-add-context-2d8f9386-9864-4a51-b089-a7342029bb41">
```

提取到的 conversation_id: `2d8f9386-9864-4a51-b089-a7342029bb41`

## 🔧 提取方法

### Python 脚本

```python
import asyncio
import json
import websockets

async def get_conversation_id():
    code = """
    (async () => {
        const electron = await import('electron');
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) return JSON.stringify({ error: 'No windows' });
        
        const result = await windows[0].webContents.executeJavaScript(`
            (() => {
                const elements = document.querySelectorAll('[id^="composer-bottom-add-context-"]');
                
                if (elements.length === 0) {
                    return JSON.stringify({ error: 'No composer found' });
                }
                
                const match = elements[0].id.match(/composer-bottom-add-context-([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/i);
                
                if (match && match[1]) {
                    return JSON.stringify({ conversation_id: match[1] });
                }
                
                return JSON.stringify({ error: 'Could not extract' });
            })()
        `);
        
        return result;
    })()
    """
    
    async with websockets.connect('ws://localhost:9876') as ws:
        await ws.send(code)
        response = await ws.recv()
        result = json.loads(response)
        return json.loads(result['result'])

# 使用
result = await get_conversation_id()
print(result['conversation_id'])  # 2d8f9386-9864-4a51-b089-a7342029bb41
```

### 在 inject 中直接获取

也可以在 `install-v9.sh` 的 inject 代码中添加：

```javascript
function getCurrentConversationId() {
    // 在主进程中执行
    const windows = BrowserWindow.getAllWindows();
    if (windows.length === 0) return null;
    
    return windows[0].webContents.executeJavaScript(`
        (() => {
            const el = document.querySelector('[id^="composer-bottom-add-context-"]');
            if (!el) return null;
            
            const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
            return match ? match[1] : null;
        })()
    `);
}
```

## 📊 实际测试结果

```bash
$ python3 get_conversation_id_correct.py

================================================================================
🔍 提取 Cursor conversation_id (正确方法)
================================================================================

方法: 从 composer-bottom-add-context-{UUID} 元素提取

✅ 成功提取 conversation_id!

📋 Conversation ID: 2d8f9386-9864-4a51-b089-a7342029bb41
📊 找到 1 个 composer 元素
```

## 🔍 错误方法分析

之前我从 markdown section 提取的 UUID (如 `d9f4cdb8-91cf-4a65-aea2-da4f85d91ea8`) 其实是：
- 单个消息/回复的 ID
- 可能会有多个不同的 UUID（不同消息）
- **不是** conversation_id

正确的 conversation_id：
- 唯一标识整个对话
- 在 composer 元素中
- 在当前对话中保持不变

## ⚠️ 注意事项

1. **唯一性**: 每个 Cursor 对话（tab）有一个唯一的 conversation_id

2. **持久性**: conversation_id 在整个对话过程中保持不变

3. **可靠性**: 只要 Composer 可见，就能提取到 conversation_id

4. **多对话**: 如果有多个对话 tab 打开，每个都有自己的 conversation_id

## 🎯 应用场景

### 1. 在 Agent Hooks 中获取正确的 conversation_id

现在我们知道了正确的位置，可以：

```python
# 方法1: 从 Cursor 提供的输入数据（推荐）
conversation_id = self.input_data.get('conversation_id', 'default')

# 方法2: 从 DOM 提取（备用/验证）
conversation_id = extract_from_composer_element()
```

### 2. 在 inject 中自动获取并传递

在 `install-v9.sh` 中添加功能：
1. 定期（或在需要时）从 DOM 提取 conversation_id
2. 设置为环境变量 `ORTENSIA_CONVERSATION_ID`
3. Agent Hooks 可以直接读取

### 3. 验证一致性

可以比对：
- Cursor 传递的 `conversation_id`
- DOM 中提取的 `conversation_id`

确保数据一致性。

## 📁 相关文件

- ✅ `get_conversation_id_correct.py` - **正确的提取脚本**
- ✅ `find_conversation_tab.py` - 搜索并定位目标 UUID
- ❌ `get_conversation_id.py` - 错误的方法（从 markdown section）
- ❌ `explore_conversation_id.py` - 初始探索（方向错误）
- ❌ `extract_conversation_id.py` - 详细探索（方向错误）

## 🚀 下一步

1. ✅ 找到 conversation_id 的正确位置
2. ✅ 创建正确的提取脚本
3. ⬜ 在 inject 中添加自动提取功能
4. ⬜ 通过环境变量传递给 Agent Hooks
5. ⬜ 在 Agent Hooks 中验证 conversation_id 的一致性

## 🎉 结论

**成功找到 conversation_id 的正确位置！**

位置：`composer-bottom-add-context-{UUID}` 元素的 ID  
格式：`composer-bottom-add-context-{CONVERSATION_ID}`  
提取方法：通过 inject 的 JS 执行接口查询 DOM

感谢用户的纠正，现在我们有了正确的提取方法！🙏

