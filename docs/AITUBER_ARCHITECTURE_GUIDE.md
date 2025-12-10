# AITuber 架构与时序详解

> 完整的 AITuber 系统架构、模块说明和消息流转时序

## 📋 目录

1. [系统概览](#系统概览)
2. [核心模块](#核心模块)
3. [初始化时序](#初始化时序)
4. [消息流转](#消息流转)
5. [自动任务检查](#自动任务检查)
6. [关键设计决策](#关键设计决策)

---

## 系统概览

AITuber Kit 是一个基于 Next.js + React 的虚拟角色系统，通过 WebSocket 与 Ortensia 中央服务器通信，实现与 Cursor IDE 的集成。

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     AITuber Kit (Next.js)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           assistant.tsx (主页面)                      │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │ VRM Viewer  │  │ Chat UI      │  │ TTS Player  │ │  │
│  │  └─────────────┘  └──────────────┘  └─────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         OrtensiaManager (中央协调器)                  │  │
│  │  • 管理 WebSocket 连接                                │  │
│  │  • 统一消息分发                                       │  │
│  │  • 处理器注册与生命周期                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         OrtensiaClient (WebSocket 客户端)            │  │
│  │  • WebSocket 连接管理                                │  │
│  │  • 消息去重                                          │  │
│  │  • 心跳保持                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │ WebSocket
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Ortensia Central Server (Python)               │
│  • WebSocket 服务器 (websocket_server.py)                  │
│  • 消息路由与广播                                           │
│  • TTS 生成 (ChatTTS)                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    ↓               ↓
         ┌──────────────┐  ┌──────────────┐
         │ Cursor Inject│  │ Agent Hooks  │
         │ (Electron)   │  │ (Python)     │
         └──────────────┘  └──────────────┘
```

---

## 核心模块

### 1. OrtensiaManager

**职责**：中央协调器，统一管理消息分发和生命周期

**位置**：`aituber-kit/src/utils/OrtensiaManager.ts`

**核心功能**：

```typescript
class OrtensiaManager {
  // 单例模式
  private static instance: OrtensiaManager
  
  // WebSocket 客户端
  private client: OrtensiaClient | null
  
  // 消息处理器注册表
  private handlers: Map<MessageType, Set<MessageHandler>>
  
  // 状态管理
  private state: {
    clientReady: boolean          // 客户端是否就绪
    handlersRegistered: boolean   // 处理器是否注册完成
    discoveryRequested: boolean   // 是否已发送发现请求
  }
  
  // 关键方法
  initialize()          // 初始化客户端（幂等）
  on()                  // 注册消息处理器
  off()                 // 取消处理器
  markHandlersReady()   // 标记处理器就绪，触发对话发现
  dispatchMessage()     // 分发消息到注册的处理器
}
```

**设计亮点**：

1. **幂等初始化**：多次调用 `initialize()` 只创建一次客户端
2. **统一订阅**：只订阅一次 WebSocket，避免重复
3. **状态机管理**：确保正确的初始化顺序
4. **React Strict Mode 兼容**：完美支持开发模式的双重挂载

---

### 2. OrtensiaClient

**职责**：WebSocket 客户端，处理底层通信

**位置**：`aituber-kit/src/utils/OrtensiaClient.ts`

**核心功能**：

```typescript
class OrtensiaClient {
  // 单例实例
  private static instance: OrtensiaClient | null
  
  // WebSocket 连接
  private ws: WebSocket | null
  
  // 订阅者管理
  private globalSubscribers: Set<Subscriber>
  
  // 消息去重
  private processedMessages: Map<string, number>
  
  // 对话发现重试
  private discoveryRetryCount: number
  private maxDiscoveryRetries: number = 3
  
  // 关键方法
  connect()                      // 连接到服务器
  subscribe()                    // 订阅消息
  send()                         // 发送消息
  discoverExistingConversations() // 发现已有对话（带重试）
  sendCursorInputText()          // 发送文本到 Cursor
}
```

**关键特性**：

1. **消息去重**：使用 `processedMessages` Map 避免重复处理
2. **自动重连**：断线后自动重新连接
3. **心跳机制**：每 30 秒发送心跳保持连接
4. **对话发现重试**：初始化时自动重试获取已有对话

---

### 3. Conversation Store

**职责**：管理多对话状态

**位置**：`aituber-kit/src/features/stores/conversationStore.ts`

**数据结构**：

```typescript
interface Conversation {
  id: string                    // 对话 ID
  title: string                 // 标题
  messages: Message[]           // 消息列表
  autoCheckEnabled: boolean     // 是否启用自动检查（默认 true）
  lastActivity: number          // 最后活动时间
}

interface ConversationStore {
  conversations: Map<string, Conversation>
  activeConversationId: string | null
  
  // 方法
  getOrCreateConversation(id: string, title?: string): Conversation
  addMessage(convId: string, message: Message): void
  getAutoCheckEnabled(convId: string): boolean
  setAutoCheckEnabled(convId: string, enabled: boolean): void
}
```

---

### 4. AutoTaskChecker

**职责**：管理自动任务检查逻辑

**位置**：`aituber-kit/src/utils/AutoTaskChecker.ts`

**核心功能**：

```typescript
class AutoTaskChecker {
  private lastCheckTime: Map<string, number>  // 上次检查时间
  private debounceTime: number = 5000         // 防抖时间 5 秒
  
  // 检查是否可以触发（防抖）
  canTriggerCheck(conversationId: string): boolean
  
  // 记录检查时间
  recordCheck(conversationId: string): void
  
  // 获取检查提示词
  getCheckPrompt(): string
}
```

---

## 初始化时序

### 完整启动流程

```
1. React 组件挂载
   assistant.tsx useEffect() 执行
   │
   ↓
2. OrtensiaManager 初始化
   manager.initialize()
   ├─→ 创建 OrtensiaClient（单例）
   ├─→ 设置统一消息分发器（只订阅一次）
   └─→ state.clientReady = true
   │
   ↓
3. 注册消息处理器
   manager.on('aituber_receive_text', handleAituberReceiveText)
   manager.on('agent_completed', handleAgentCompleted)
   manager.on('get_conversation_id_result', handleConversationDiscovered)
   │
   ↓
4. 标记处理器就绪
   manager.markHandlersReady()
   ├─→ state.handlersRegistered = true
   └─→ 检查所有条件是否满足
   │
   ↓
5. 触发对话发现（如果条件满足）
   如果 clientReady && handlersRegistered && !discoveryRequested:
   ├─→ client.discoverExistingConversations()
   ├─→ 发送 GET_CONVERSATION_ID 消息
   └─→ state.discoveryRequested = true
   │
   ↓
6. WebSocket 连接
   client.connect()
   ├─→ 建立 WebSocket 连接
   ├─→ 发送 REGISTER 消息
   └─→ 收到 REGISTER_ACK
   │
   ↓
7. 对话发现响应
   收到 GET_CONVERSATION_ID_RESULT
   ├─→ 创建 Conversation tabs
   ├─→ 设置 autoCheckEnabled = true（默认）
   └─→ 准备接收消息
   │
   ↓
8. VRM 模型加载
   viewer.loadVRM()
   ├─→ 加载 3D 模型
   ├─→ 初始化 AnimationController
   └─→ 预加载动画文件
   │
   ↓
9. ✅ 系统就绪
   可以接收和处理消息
```

### React Strict Mode 处理

开发模式下，React 会双重挂载组件：

```
Mount 1:
├─→ OrtensiaManager.initialize() → 创建 client
├─→ 订阅消息 → isSubscribed = true
├─→ 注册处理器
└─→ Cleanup → 取消处理器，但 isSubscribed 仍为 true

Mount 2:
├─→ OrtensiaManager.initialize() → 跳过（client 已存在）
├─→ 订阅消息 → 跳过（isSubscribed = true）✅
├─→ 注册处理器 → 重新注册 ✅
└─→ 正常运行
```

**关键点**：
- `isSubscribed` 标记防止重复订阅
- 处理器可以重新注册（通过 `Map<MessageType, Set<Handler>>`）
- 保证只有 1 个订阅者

---

## 消息流转

### 1. 接收消息流程

```
WebSocket 收到消息
│
↓
OrtensiaClient.handleMessage()
├─→ 消息去重检查
│   ├─ 生成唯一 key: `${type}_${from}_${timestamp}`
│   ├─ 检查 processedMessages Map
│   └─ 如果重复 → 跳过
│
├─→ 通知所有订阅者（只有 OrtensiaManager 一个）
│   └─→ subscriber(message)
│
└─→ OrtensiaManager.dispatchMessage()
    ├─→ 查找注册的处理器
    │   handlers.get(message.type)
    │
    └─→ 调用所有匹配的处理器
        ├─→ handleAituberReceiveText(message)
        ├─→ handleAgentCompleted(message)
        └─→ handleConversationDiscovered(message)
```

### 2. 发送消息流程

```
组件调用
│
↓
OrtensiaClient.sendCursorInputText(text, conversationId)
│
├─→ 构造消息对象
│   {
│     type: 'cursor_input_text',
│     from: clientId,
│     to: 'cursor_inject',
│     payload: { text, conversation_id }
│   }
│
└─→ OrtensiaClient.send(message)
    ├─→ 检查 WebSocket 连接状态
    ├─→ JSON.stringify(message)
    └─→ websocket.send(jsonString)
```

### 3. TTS 流程

```
收到 aituber_receive_text 消息
│
↓
handleAituberReceiveText()
├─→ 提取 text, audio_file, conversation_id
├─→ 添加消息到 conversation store
│
└─→ 播放音频
    ├─→ 获取音频文件路径
    ├─→ fetch('/api/tts-audio/${filename}')
    ├─→ speakCharacter(buffer, emotion)
    │   ├─→ model.speak() → 播放音频 + 口型同步
    │   └─→ emoteController.playEmotion() → 播放表情动画
    └─→ 播放完成回调
```

---

## 自动任务检查

### 完整流程

```
1. Agent 任务完成
   cursor-hooks/hooks/stop.py 触发
   │
   ↓
2. 发送 AGENT_COMPLETED 事件
   {
     type: 'agent_completed',
     from: 'hook-{conversation_id}',
     payload: {
       agent_id: 'default',
       result: 'success'
     }
   }
   │
   ↓
3. AITuber 接收事件
   OrtensiaManager 分发到 handleAgentCompleted()
   │
   ↓
4. 提取 Conversation ID
   从 message.from 提取：
   'hook-e595bde3-bcc4-4bb4-9ebc-0cadf0cbd6da'
   → conversation_id = 'e595bde3-bcc4-4bb4-9ebc-0cadf0cbd6da'
   │
   ↓
5. 短 ID 匹配
   短 ID: 'e595bde3'（前 8 个字符）
   │
   在 conversations 中查找匹配：
   ├─→ 'e595bde3-ae8a-4754-a3f2-1d38871068e0' ✅ 匹配
   └─→ '008b07be-69b9-446a-b05c-8906fe93453b' ✗ 不匹配
   │
   ↓
6. 检查自动检查开关
   conversationStore.getAutoCheckEnabled(matchedId)
   → 返回 true
   │
   ↓
7. 防抖检查
   autoChecker.canTriggerCheck(matchedId)
   检查距离上次检查是否超过 5 秒
   → 返回 true
   │
   ↓
8. 延迟 1 秒后发送检查提示
   setTimeout(() => {
     const prompt = "请检查是否还有计划中的任务可以完成..."
     
     // 添加到 conversation
     conversationStore.addMessage(matchedId, {
       role: 'user',
       content: prompt
     })
     
     // 发送到 Cursor（使用原始 conversation_id）
     client.sendCursorInputText(prompt, originalConvId, true)
     
     // 记录检查时间
     autoChecker.recordCheck(matchedId)
   }, 1000)
```

### 短 ID 匹配机制

**为什么需要短 ID 匹配？**

不同来源的 conversation_id 可能不一致：
- **Hook**：从环境变量 `CURSOR_CONVERSATION_ID` 获取
- **Inject**：从 DOM 元素 `#composer-bottom-add-context-{id}` 提取

这两个 ID 可能不同，但前 8 个字符相同。

**实现**：

```typescript
const shortConvId = convId.substring(0, 8)  // 'e595bde3'
const matchedConv = allConvs.find(([id]) => id.startsWith(shortConvId))
```

---

## 关键设计决策

### 1. 为什么使用 OrtensiaManager？

**问题**：
- 多个组件需要监听 WebSocket 消息
- React Strict Mode 导致重复订阅
- 消息被处理多次
- 组件间通信复杂

**解决方案**：
- 单一订阅点（OrtensiaManager）
- 统一消息分发
- 状态机管理初始化顺序
- 防止重复订阅

### 2. 为什么需要消息去重？

**问题**：
- WebSocket 可能重复发送消息
- React 双重挂载可能导致重复处理

**解决方案**：
```typescript
// OrtensiaClient 中
private processedMessages: Map<string, number> = new Map()

const messageKey = `${message.type}_${message.from}_${message.timestamp}`
if (this.processedMessages.has(messageKey)) {
  console.log('🔕 跳过重复消息')
  return
}
this.processedMessages.set(messageKey, Date.now())
```

### 3. 为什么需要对话发现重试？

**问题**：
- React Strict Mode 可能导致 WebSocket 连接时序不确定
- 首次调用时 WebSocket 可能还未连接

**解决方案**：
```typescript
private discoveryRetryCount: number = 0
private maxDiscoveryRetries: number = 3

public discoverExistingConversations() {
  if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
    if (this.discoveryRetryCount < this.maxDiscoveryRetries) {
      this.discoveryRetryCount++
      const delay = this.discoveryRetryCount * 2000  // 2s, 4s, 6s
      setTimeout(() => {
        this.discoverExistingConversations()
      }, delay)
    }
    return
  }
  // 发送请求
}
```

### 4. 为什么 autoCheckEnabled 默认为 true？

**原因**：
- 用户期望自动化工作流
- 手动启用容易被忘记
- 可以随时手动关闭

**实现**：
```typescript
// conversationStore.ts
getOrCreateConversation(id: string, title?: string): Conversation {
  if (!this.conversations.has(id)) {
    this.conversations.set(id, {
      id,
      title: title || `对话 ${id.substring(0, 8)}`,
      messages: [],
      autoCheckEnabled: true,  // ✅ 默认启用
      lastActivity: Date.now(),
    })
  }
  return this.conversations.get(id)!
}
```

---

## 故障排查指南

### 问题 1：消息被处理多次

**症状**：同一条消息触发 4 次处理器

**原因**：
- `OrtensiaManager.initialize()` 被调用多次
- 每次都调用 `client.subscribe()`

**解决**：
```typescript
private isSubscribed: boolean = false

public initialize() {
  if (!this.isSubscribed) {
    this.client.subscribe(...)
    this.isSubscribed = true
  }
}
```

### 问题 2：自动检查不触发

**症状**：Agent 完成但没有发送"继续"提示

**可能原因**：
1. `autoCheckEnabled = false` → 检查 conversation store
2. Conversation ID 不匹配 → 使用短 ID 匹配
3. 防抖未通过 → 等待 5 秒

**诊断**：
```typescript
console.log(`🎯 [Auto Check] 当前所有对话:`)
allConvs.forEach(([id, conv]) => {
  console.log(`  - ${id}: autoCheck=${conv.autoCheckEnabled}`)
})
```

### 问题 3：VRM 加载错误

**症状**：`Error: You have to load VRM first`

**原因**：动画在 VRM 加载前就尝试加载

**解决**：
```typescript
// viewer.ts
const vrma = await loadVRMAnimation(url)
if (vrma && this.model.vrm) {  // ✅ 确保 VRM 已加载
  this.model.loadAnimation(vrma)
}

// model.ts
if (vrm == null || mixer == null) {
  console.warn('VRM not loaded yet, skipping animation')
  return  // ✅ 返回而不是抛出错误
}
```

---

## 最佳实践

### 1. 消息处理器

```typescript
// ✅ 好：使用 useCallback 避免重新注册
const handleMessage = useCallback((message: OrtensiaMessage) => {
  // 处理逻辑
}, [依赖项])

// ❌ 坏：每次渲染都创建新函数
const handleMessage = (message: OrtensiaMessage) => {
  // 处理逻辑
}
```

### 2. Cleanup

```typescript
useEffect(() => {
  // 注册
  const unsubscribe = manager.on('message_type', handler)
  
  return () => {
    // ✅ 好：清理订阅
    manager.off('message_type', handler)
  }
}, [])
```

### 3. 日志

```typescript
// ✅ 好：使用结构化日志
console.log('🎯 [Auto Check] 找到匹配:', shortId, '→', matchedId)

// ❌ 坏：无上下文的日志
console.log('found', matchedId)
```

---

## 性能优化

### 1. 消息去重清理

```typescript
// 定期清理旧消息（超过 5 分钟）
setInterval(() => {
  const now = Date.now()
  for (const [key, timestamp] of this.processedMessages.entries()) {
    if (now - timestamp > 5 * 60 * 1000) {
      this.processedMessages.delete(key)
    }
  }
}, 60000)  // 每分钟清理一次
```

### 2. 动画预加载

```typescript
// animationController.ts
async preloadAnimations() {
  const animations = [
    { name: 'idle', url: '/idle_loop.vrma' },
    // 预加载常用动画
  ]
  
  await Promise.all(
    animations.map(anim => this.loadAnimation(anim.name, anim.url))
  )
}
```

### 3. 防抖和节流

```typescript
// AutoTaskChecker
private debounceTime: number = 5000  // 5 秒防抖

canTriggerCheck(conversationId: string): boolean {
  const lastCheck = this.lastCheckTime.get(conversationId) || 0
  const now = Date.now()
  return now - lastCheck > this.debounceTime
}
```

---

## 附录

### A. 消息类型

```typescript
type MessageType =
  | 'register'                  // 客户端注册
  | 'register_ack'              // 注册确认
  | 'aituber_receive_text'      // 接收文本（带 TTS）
  | 'agent_completed'           // Agent 任务完成
  | 'get_conversation_id'       // 请求对话 ID
  | 'get_conversation_id_result'// 对话 ID 响应
  | 'cursor_input_text'         // 发送文本到 Cursor
  | 'heartbeat'                 // 心跳
  | 'heartbeat_ack'             // 心跳响应
```

### B. 配置项

```typescript
// OrtensiaClient 配置
const config = {
  wsUrl: 'ws://localhost:8765',
  heartbeatInterval: 30000,      // 30 秒
  reconnectDelay: 3000,          // 3 秒
  maxReconnectAttempts: 5,
}

// AutoTaskChecker 配置
const config = {
  debounceTime: 5000,            // 5 秒
  checkPrompt: '请检查是否还有计划中的任务可以完成...',
}
```

### C. 文件结构

```
aituber-kit/src/
├── pages/
│   └── assistant.tsx           # 主页面，协调所有模块
├── utils/
│   ├── OrtensiaManager.ts     # 中央协调器
│   ├── OrtensiaClient.ts      # WebSocket 客户端
│   └── AutoTaskChecker.ts     # 自动检查逻辑
├── features/
│   ├── stores/
│   │   └── conversationStore.ts  # 对话状态管理
│   ├── vrmViewer/
│   │   ├── viewer.ts          # VRM 场景管理
│   │   └── model.ts           # VRM 模型操作
│   └── emoteController/
│       ├── emoteController.ts # 表情控制器
│       ├── expressionController.ts  # 表情管理
│       └── animationController.ts   # 动画管理
└── components/
    ├── useExternalLinkage.tsx # 外部连接 Hook
    └── MultiConversationChat.tsx  # 多对话 UI
```

---

## 更新日志

- **2025-12-08**: 创建文档
  - 添加完整架构说明
  - 添加时序图和流程图
  - 添加故障排查指南
  - 添加最佳实践和性能优化建议

---

**文档维护者**: AI Assistant  
**最后更新**: 2025-12-08  
**版本**: 1.0.0







