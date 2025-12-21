# 功能：对话发现 (Conversation Discovery)

> 发现已存在的 Cursor 对话，创建对应的 Tab

## 📍 代码位置

| 组件 | 文件 | 行号 | 函数/方法 |
|-----|------|-----|----------|
| 发起请求 | `aituber-kit/src/utils/OrtensiaClient.ts` | 428-465 | `discoverExistingConversations()` |
| 服务器处理 | `bridge/websocket_server.py` | 560-610 | `handle_get_conversation_id()` |
| 结果处理 | `bridge/websocket_server.py` | 610-750 | `handle_execute_js_result_for_discovery()` |
| 前端处理 | `aituber-kit/src/pages/assistant.tsx` | 230-266 | `handleConversationDiscovered()` |

## 🔄 工作流程

```
┌─────────────────┐
│  AITuber 前端    │
│  OrtensiaClient │
└────────┬────────┘
         │ GET_CONVERSATION_ID
         ▼
┌─────────────────┐
│  中央服务器      │
│  websocket_server│
└────────┬────────┘
         │ 生成 JavaScript 代码
         │ EXECUTE_JS
         ▼
┌─────────────────┐
│  Cursor Inject   │
│  (渲染进程)      │
└────────┬────────┘
         │ 执行 JS 查询 DOM
         │ 查找 [id^="composer-bottom-add-context-"]
         │
         │ EXECUTE_JS_RESULT
         ▼
┌─────────────────┐
│  中央服务器      │
│  解析结果        │
└────────┬────────┘
         │ GET_CONVERSATION_ID_RESULT
         ▼
┌─────────────────┐
│  AITuber 前端    │
│  创建对话 Tab    │
└─────────────────┘
```

## 💡 关键实现细节

### 1. 为什么不直接转发 GET_CONVERSATION_ID 给 inject？

**原因**：inject 不知道如何处理 `GET_CONVERSATION_ID` 消息类型

**解决**：中央服务器负责生成 JavaScript 代码，通过 `EXECUTE_JS` 发送给 inject

### 2. DOM 查询的 JavaScript 代码

```javascript
(() => {
    const el = document.querySelector('[id^="composer-bottom-add-context-"]');
    if (!el) {
        return JSON.stringify({ found: false, conversationId: null, title: null });
    }
    
    const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/);
    const conversationId = match ? match[1] : null;
    
    // 获取窗口标题...
    
    return JSON.stringify({ 
        found: true, 
        conversationId: conversationId,
        title: title
    });
})()
```

### 3. 重试机制

- 位置：`OrtensiaClient.ts:428`
- 重试次数：3 次
- 延迟：2s, 4s, 6s（递增）
- 原因：WebSocket 连接可能尚未稳定

### 4. 结果解析

服务器收到 `EXECUTE_JS_RESULT` 后：
1. 检查 `request_id` 是否以 `get_conv_id_` 开头
2. 从 `pending_requests` 中获取原始请求者信息
3. 解析广播模式结果：`{0: result0, 1: result1, ...}`
4. 为每个有效的 conversation_id 发送 `GET_CONVERSATION_ID_RESULT`

## ⚠️ 常见问题

### 问题：未知消息类型 get_conversation_id

**原因**：`handle_new_protocol_message()` 中缺少对应的处理分支

**解决**：添加：
```python
elif msg_type == MessageType.GET_CONVERSATION_ID:
    await handle_get_conversation_id(client_info, message)
```

### 问题：对话发现成功但没有结果

**可能原因**：
1. Cursor 窗口没有打开 Composer
2. DOM 元素不存在
3. inject 未正确返回结果

**诊断**：查看服务器日志中的 `[Discovery]` 信息

## 📅 更新历史

| 日期 | 变更 | 相关 commit |
|-----|------|------------|
| 2025-12-21 | 修复 GET_CONVERSATION_ID 未处理的问题 | - |
| 2025-12-08 | 添加重试机制 | AITUBER_DISCOVERY_FIX.md |
| 2025-11 | 初始实现 | V10 |

