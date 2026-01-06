# 自动任务检查故障排除

## 🐛 问题现象

**用户反馈**: Cursor 任务完成后，没有自动输入"继续"提示词

## 🔍 问题诊断

### 1. 事件流程检查 ✅

**Hook → Server**:
```
[00:14:09] ✅ [hook-e595bde3-...] 注册成功
[00:14:09] 📨 aituber_receive_text
[00:14:09] 📨 [AITuber] Hook 消息，conversation_id: e595bde3-...
```
✅ Hook 正常发送消息到服务器

**Server → AITuber**:
```
[00:14:12] 📤 [AITuber] 消息已转发: hook-e595bde3-... → aituber-mivv6ov4beixlyoeo
```
✅ 服务器正常转发消息到 AITuber

**AITuber 接收**:
```javascript
case MessageType.AGENT_COMPLETED:
  console.log('✅ [Ortensia] Agent 任务完成:', message.payload)
  handleAgentCompleted(message)  // ✅ 调用处理函数
```
✅ AITuber 接收到 `agent_completed` 事件

### 2. 处理逻辑检查 ⚠️

**handleAgentCompleted 流程**:

```typescript
const handleAgentCompleted = (message: OrtensiaMessage) => {
  // 1. 提取 conversation_id
  const hookId = message.from  // "hook-e595bde3-ae8a-4754-a3f2-1d38871068e0"
  let convId = hookId.substring(5)  // "e595bde3-ae8a-4754-a3f2-1d38871068e0"
  
  // 2. 检查自动检查开关
  const autoEnabled = conversationStore.getAutoCheckEnabled(convId)
  
  if (!autoEnabled) {
    console.log(`⚠️ [Auto Check] 自动检查未启用`)
    return  // ❌ 在这里返回了！
  }
  
  // 3. 发送检查提示（永远不会执行）
  client.sendCursorInputText(checkPrompt, convId, true)
}
```

### 3. 根本原因 ❌

**conversationStore.ts** (第 42 行):
```typescript
const newConversation: Conversation = {
  id: conversationId,
  title: title || `Conversation ${conversationId.slice(0, 8)}`,
  messages: [],
  autoCheckEnabled: false,  // ❌ 默认关闭！
  lastActivity: Date.now(),
}
```

**问题**: 
- 新创建的对话，`autoCheckEnabled` 默认是 `false`
- 用户需要**手动**在 UI 中启用自动检查开关
- 如果没有启用，`handleAgentCompleted` 会直接返回，不会发送"继续"提示

## ✅ 解决方案

### 方案 1: 手动启用开关（推荐）⭐

**操作步骤**:
1. 打开 AITuber 助手界面（`http://localhost:3000/assistant`）
2. 找到 `e595bde3` 对话的 tab
3. 在输入框上方找到 **"自动任务检查"** 开关
4. 点击开关，确保显示 ✅（启用状态）

**UI 位置**:
```
┌─────────────────────────────────┐
│ [Tab 1] [Tab 2] [e595bde3] ...  │ ← 对话标签
├─────────────────────────────────┤
│ □ 自动任务检查 ⏸️  ← 点击这里！  │
│                                  │
│ [输入框]                         │
└─────────────────────────────────┘
```

启用后：
```
☑ 自动任务检查 ✅  ← 启用成功
```

### 方案 2: 修改默认值（永久解决）

修改 `aituber-kit/src/features/stores/conversationStore.ts`:

```typescript
const newConversation: Conversation = {
  id: conversationId,
  title: title || `Conversation ${conversationId.slice(0, 8)}`,
  messages: [],
  autoCheckEnabled: true,  // ✅ 改为 true
  lastActivity: Date.now(),
}
```

**影响**: 所有新创建的对话都会默认启用自动检查

### 方案 3: 通过 URL 参数启用

修改 `assistant.tsx`，支持通过 URL 参数自动启用：

```typescript
getOrCreateConversation: (conversationId: string, title?: string, autoCheck?: boolean) => {
  const newConversation: Conversation = {
    id: conversationId,
    title: title || `Conversation ${conversationId.slice(0, 8)}`,
    messages: [],
    autoCheckEnabled: autoCheck ?? false,  // 可选参数
    lastActivity: Date.now(),
  }
  // ...
}
```

然后在创建对话时传入：
```typescript
// 从 URL 参数读取
const searchParams = new URLSearchParams(window.location.search)
const autoCheck = searchParams.get('autoCheck') === 'true'

conversationStore.getOrCreateConversation(convId, title, autoCheck)
```

访问: `http://localhost:3000/assistant?autoCheck=true`

## 📊 验证流程

### 启用后的完整流程

```mermaid
graph LR
    A[Cursor 任务完成] --> B[stop.py Hook]
    B --> C[发送 agent_completed]
    C --> D[WebSocket Server]
    D --> E[转发到 AITuber]
    E --> F[handleAgentCompleted]
    F --> G{autoCheckEnabled?}
    G -->|false| H[❌ 返回，不处理]
    G -->|true| I[✅ 检查防抖]
    I --> J[发送检查提示]
    J --> K[Cursor 收到 "继续"]
```

### 测试验证

1. **启用自动检查**：在 UI 中打开开关
2. **触发任务完成**：在 Cursor 中完成一个任务
3. **查看浏览器控制台**：

```javascript
// 应该看到这些日志
🎯 [Auto Check] ============ handleAgentCompleted 被调用 ============
🎯 [Auto Check] Hook ID: hook-e595bde3-...
🎯 [Auto Check] 提取的 Conversation ID: e595bde3-...
🎯 [Auto Check] 当前所有对话 (共 N 个):
  - e595bde3-...: autoCheck=true, title="..."  ← 确保是 true
🎯 [Auto Check] 自动检查状态: true  ← 确保是 true
🎯 [Auto Check] 是否可以触发: true
✅ [Auto Check] 将在 1 秒后发送检查提示
📤 [Auto Check] e595bde3: 发送检查提示 "继续"
```

4. **查看 Cursor**：应该自动收到"继续"输入

## 🎯 快速检查清单

当自动任务检查不工作时，按以下顺序检查：

- [ ] 1. **AITuber 是否收到事件**？
  ```
  查看浏览器控制台，搜索 "Agent 任务完成"
  ```

- [ ] 2. **handleAgentCompleted 是否被调用**？
  ```
  查看浏览器控制台，搜索 "handleAgentCompleted 被调用"
  ```

- [ ] 3. **conversation_id 是否正确提取**？
  ```
  查看日志: "提取的 Conversation ID: e595bde3-..."
  ```

- [ ] 4. **自动检查开关是否启用**？⭐ **最常见问题**
  ```
  查看日志: "自动检查状态: true"
  如果是 false，去 UI 中手动启用！
  ```

- [ ] 5. **防抖检查是否通过**？
  ```
  查看日志: "是否可以触发: true"
  如果是 false，等待 5 秒后再试
  ```

## 💡 常见误区

### 误区 1: 以为自动检查是默认启用的 ❌

**错误认知**: 创建对话后，自动检查应该立即工作

**实际情况**: `autoCheckEnabled` 默认是 `false`，必须手动启用

### 误区 2: 以为看到"任务完成"消息就够了 ❌

**错误认知**: AITuber 说"Agent 任务完成了！太棒了！🎉"，就应该自动继续

**实际情况**: 这只是 TTS 消息，不代表自动检查被触发。需要检查 `autoCheckEnabled` 状态。

### 误区 3: 以为所有对话共享自动检查开关 ❌

**错误认知**: 在一个 tab 启用自动检查，其他 tab 也会启用

**实际情况**: **每个对话独立管理**自动检查开关。需要为每个 tab 单独启用。

## 📝 总结

### 问题根源
- ✅ Hook 正常工作
- ✅ 消息正常传递
- ✅ AITuber 正常接收
- ❌ **自动检查开关未启用**（默认 `false`）

### 解决方法
1. **立即生效**: 在 UI 中手动启用开关 ⭐ **推荐**
2. **永久解决**: 修改代码，将默认值改为 `true`
3. **灵活控制**: 通过 URL 参数控制

### 验证成功标志
- 浏览器控制台显示 `autoCheck=true`
- 浏览器控制台显示 `发送检查提示 "继续"`
- Cursor 自动收到输入

---

**问题**: e595bde3 这个 tab 的自动任务检查是否生效？  
**答案**: Hook 工作正常，但 `autoCheckEnabled` 开关未启用  
**操作**: 在 AITuber UI 中手动启用该 tab 的自动检查开关 ✅
























