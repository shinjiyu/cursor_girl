# Cursor 事件广播方案

## 🎯 目标

让 AITuber Kit 能够接收 Cursor 的状态更新和事件，实现实时联动。

## 📊 当前问题

### 现状

```
Command Client → Server → Cursor Hook
                            ↓
                  (只返回结果给 Command Client)
                            ↓
                 AITuber ❌ 收不到任何消息
```

### 原因

1. **Cursor Hook 只发送结果消息**
   - `composer_send_prompt_result` - 通过 `route_message` 点对点路由
   - 只发给原始请求者（`to: fromId`）

2. **没有发送状态事件**
   - 不发送 `AGENT_STATUS_CHANGED`
   - 不发送 `AGENT_COMPLETED`
   - 不发送 `AGENT_ERROR`

3. **服务器路由差异**
   - `route_message` - 点对点，不广播
   - `broadcast_event` - 广播给所有客户端

## ✅ 解决方案

### 方案 1：Cursor Hook 发送状态事件（推荐）

在 Cursor Hook 执行操作时，**额外发送状态事件**：

```javascript
// 1. 发送"开始"事件
const startEvent = {
    type: 'agent_status_changed',
    from: cursorId,
    to: 'broadcast',  // 广播给所有客户端
    timestamp: Date.now(),
    payload: {
        agent_id: agent_id,
        status: 'working',
        message: '正在执行提示词...'
    }
};
sendToCentral(startEvent);

// 2. 执行操作
await handleComposerSendPrompt(fromId, payload);

// 3. 发送"完成"事件
const completeEvent = {
    type: 'agent_completed',
    from: cursorId,
    to: 'broadcast',
    timestamp: Date.now(),
    payload: {
        agent_id: agent_id,
        result: 'success',
        message: '提示词已提交'
    }
};
sendToCentral(completeEvent);

// 4. 发送结果（仍然点对点）
const resultMessage = {
    type: 'composer_send_prompt_result',
    from: cursorId,
    to: fromId,  // 只发给原请求者
    // ...
};
sendToCentral(resultMessage);
```

**优点**：
- ✅ AITuber 可以收到实时状态更新
- ✅ 不影响现有的结果返回机制
- ✅ 符合 Ortensia 协议设计

**缺点**：
- ⚠️ 需要修改 Cursor Hook

### 方案 2：中央服务器转发结果（不推荐）

修改服务器，将结果消息也广播：

```python
elif msg_type == MessageType.COMPOSER_SEND_PROMPT_RESULT:
    await route_message(message)  # 发给原请求者
    await broadcast_event(message)  # 同时广播给所有人
```

**优点**：
- ✅ 不需要修改 Cursor Hook

**缺点**：
- ❌ 破坏点对点通信语义
- ❌ 所有客户端都会收到无关消息
- ❌ 不符合协议设计原则

### 方案 3：订阅机制（复杂）

添加客户端订阅机制，允许 AITuber 订阅 Cursor 事件：

```python
class ClientInfo:
    def __init__(self):
        self.subscriptions = []  # 订阅的事件类型或客户端

# AITuber 订阅 Cursor 事件
aituber.subscriptions.append('cursor-*')
```

**优点**：
- ✅ 灵活的订阅机制
- ✅ 避免无关消息泛滥

**缺点**：
- ❌ 需要大量重构
- ❌ 增加系统复杂度

## 🎯 推荐实现：方案 1

### 步骤 1：添加 Cursor Hook 状态事件

修改 `cursor-injector/install-v9.sh`：

```javascript
async function handleComposerSendPrompt(fromId, payload) {
    const { agent_id, prompt } = payload;
    
    try {
        // ====== 新增：发送开始事件 ======
        sendStatusEvent('working', agent_id, '正在执行提示词...');
        
        // ... 原有代码 ...
        
        // ====== 新增：发送完成事件 ======
        sendStatusEvent('completed', agent_id, '提示词已提交');
        
        // 发送结果（保持不变）
        const resultMessage = { /* ... */ };
        sendToCentral(resultMessage);
        
    } catch (error) {
        // ====== 新增：发送错误事件 ======
        sendErrorEvent(agent_id, error.message);
        
        // 发送错误结果（保持不变）
        const errorMessage = { /* ... */ };
        sendToCentral(errorMessage);
    }
}

// ====== 新增：辅助函数 ======
function sendStatusEvent(status, agentId, message) {
    const event = {
        type: 'agent_status_changed',
        from: cursorId,
        to: 'broadcast',
        timestamp: Math.floor(Date.now() / 1000),
        payload: {
            agent_id: agentId,
            status: status,
            message: message
        }
    };
    sendToCentral(event);
}

function sendErrorEvent(agentId, errorMessage) {
    const event = {
        type: 'agent_error',
        from: cursorId,
        to: 'broadcast',
        timestamp: Math.floor(Date.now() / 1000),
        payload: {
            agent_id: agentId,
            error: errorMessage
        }
    };
    sendToCentral(event);
}
```

### 步骤 2：AITuber 监听事件

AITuber 已经可以接收广播事件，只需添加处理器：

```typescript
// aituber-kit/src/components/useExternalLinkage.tsx
client.on(MessageType.AGENT_STATUS_CHANGED, (msg: OrtensiaMessage) => {
  console.log('📊 [Ortensia] Cursor 状态变化:', msg.payload)
  
  // 显示状态提示
  if (msg.payload.status === 'working') {
    // 显示 "Cursor 正在工作..." 提示
  } else if (msg.payload.status === 'completed') {
    // 显示 "Cursor 已完成" 提示
  }
})

client.on(MessageType.AGENT_COMPLETED, (msg: OrtensiaMessage) => {
  console.log('✅ [Ortensia] Cursor 完成:', msg.payload)
  // 播放完成音效或动画
})

client.on(MessageType.AGENT_ERROR, (msg: OrtensiaMessage) => {
  console.error('❌ [Ortensia] Cursor 错误:', msg.payload)
  // 显示错误提示
})
```

## 📈 预期效果

```
Command Client 发送: composer_send_prompt
    ↓
Central Server 路由 → Cursor Hook
    ↓
Cursor Hook 发送:
    1. agent_status_changed (广播) → ✅ AITuber 收到
    2. agent_completed (广播)       → ✅ AITuber 收到
    3. composer_send_prompt_result  → ✅ Command Client 收到
```

## 🔄 消息流对比

### 修改前
```
Command → Server → Cursor
                     ↓
            (只返回结果)
                     ↓
                 Command ✅
                 AITuber ❌
```

### 修改后
```
Command → Server → Cursor
                     ↓
         ┌──────────┼──────────┐
         ↓          ↓          ↓
    (状态事件)  (完成事件)  (结果消息)
         ↓          ↓          ↓
    广播给所有  广播给所有  发给原请求者
         ↓          ↓          ↓
     AITuber ✅  AITuber ✅  Command ✅
     Command ✅  Command ✅
```

## 📋 实施清单

- [ ] 修改 `cursor-injector/install-v9.sh` 添加状态事件发送
- [ ] 修改 `cursor-injector/install-v8.sh` 添加状态事件发送
- [ ] 更新 AITuber 添加事件监听器
- [ ] 测试消息广播是否正常工作
- [ ] 更新文档说明事件类型

## 🧪 测试方案

1. 启动中央服务器
2. 启动 AITuber Kit（打开控制台）
3. 使用 Command Client 发送提示词
4. 验证 AITuber 控制台显示：
   - `📊 Cursor 状态变化: working`
   - `✅ Cursor 完成`
5. 验证 Command Client 收到结果

## 📚 相关文件

- `cursor-injector/install-v9.sh` - Cursor Hook 主文件
- `bridge/websocket_server.py` - 中央服务器路由逻辑
- `bridge/protocol.py` - 协议定义
- `aituber-kit/src/components/useExternalLinkage.tsx` - AITuber 事件处理

