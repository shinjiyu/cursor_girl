# AITuber Web 侧详细设计报告

> 完整的模块加载顺序、启动逻辑和架构设计文档

**版本**: 2.0  
**创建日期**: 2025-12-17  
**最后更新**: 2025-12-17

---

## 📋 目录

1. [系统概览](#系统概览)
2. [完整启动流程](#完整启动流程)
3. [模块加载顺序详解](#模块加载顺序详解)
4. [核心模块设计](#核心模块设计)
5. [状态管理架构](#状态管理架构)
6. [消息流转机制](#消息流转机制)
7. [时序图](#时序图)
8. [关键设计决策](#关键设计决策)
9. [故障排查指南](#故障排查指南)

---

## 系统概览

### 技术栈

- **框架**: Next.js 14.2.28 (React 18)
- **状态管理**: Zustand
- **3D 渲染**: Three.js + @pixiv/three-vrm
- **通信**: WebSocket (ws://localhost:8765)
- **构建工具**: Next.js (Webpack)
- **类型系统**: TypeScript

### 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js 应用层                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  _document.tsx → _app.tsx → assistant.tsx            │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    组件层 (React)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ VrmViewer    │  │ WebSocketMgr │  │ MultiConvChat │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   管理层 (单例模式)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ OrtensiaMgr  │  │ OrtensiaClient│ │ AutoChecker  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   状态层 (Zustand)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ homeStore    │  │ settingsStore│  │ conversationStore│ │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  WebSocket 通信层                            │
│              ws://localhost:8765                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 完整启动流程

### 阶段 1: Next.js 初始化 (T+0ms)

```
1. 浏览器请求 /assistant
   │
   ↓
2. Next.js 服务器处理请求
   ├─→ 执行 getServerSideProps (如果有)
   ├─→ 渲染 _document.tsx
   │   ├─→ 加载 HTML 结构
   │   ├─→ 加载字体 (Google Fonts)
   │   └─→ 设置 <body className="ortensia-theme">
   │
   └─→ 渲染 _app.tsx
       ├─→ 加载全局样式
       │   ├─→ globals.css
       │   ├─→ themes.css
       │   └─→ ortensia-theme.css
       │
       └─→ 执行 _app.tsx useEffect
           ├─→ 检查 userOnboarded
           ├─→ 执行 migrateStore() (首次)
           ├─→ 检测浏览器语言
           ├─→ 设置 i18n 语言
           ├─→ 应用主题 (data-theme)
           └─→ 标记 userOnboarded = true
```

**关键文件**:
- `src/pages/_document.tsx`: HTML 文档结构
- `src/pages/_app.tsx`: 应用级初始化
- `src/styles/globals.css`: 全局样式

**时间**: T+0ms ~ T+200ms

---

### 阶段 2: React 组件渲染 (T+200ms)

```
3. 渲染 assistant.tsx
   │
   ├─→ 创建组件状态
   │   ├─→ isDragging = false
   │   ├─→ showControls = false
   │   ├─→ isLoaded = false
   │   └─→ isMiniMode = false
   │
   ├─→ 初始化 Zustand Stores
   │   ├─→ conversationStore (多对话管理)
   │   └─→ autoChecker (自动任务检查器)
   │
   └─→ 执行 assistant.tsx useEffect (首次)
       ├─→ 设置 isLoaded = true
       ├─→ 初始化 OrtensiaManager
       │   └─→ manager.initialize()
       │       ├─→ 创建 OrtensiaClient (单例)
       │       ├─→ 设置消息分发器 (只订阅一次)
       │       └─→ state.clientReady = true
       │
       ├─→ 设置 settingsStore
       │   ├─→ externalLinkageMode = true
       │   └─→ selectLanguage = 'ja'
       │
       └─→ 启动 VRM 加载重试逻辑
           └─→ setTimeout(loadModel, 3000)
```

**关键文件**:
- `src/pages/assistant.tsx`: 主页面组件
- `src/utils/OrtensiaManager.ts`: 中央协调器

**时间**: T+200ms ~ T+300ms

---

### 阶段 3: 动态组件加载 (T+300ms)

```
4. 动态导入组件 (ssr: false)
   │
   ├─→ VrmViewer (延迟加载)
   │   ├─→ 创建 Three.js 场景
   │   ├─→ 初始化 VRM 引擎
   │   ├─→ 创建 canvas 元素
   │   ├─→ 调用 viewer.setup(canvas)
   │   ├─→ 加载默认模型 (selectedVrmPath)
   │   └─→ 存储 viewer 到 homeStore.viewer
   │
   └─→ WebSocketManager (延迟加载)
       ├─→ 初始化 handleReceiveTextFromWs
       ├─→ 初始化 handleReceiveTextFromRt
       ├─→ 调用 useExternalLinkage()
       │   └─→ 创建 OrtensiaClient (如果不存在)
       │       ├─→ 连接到 ws://localhost:8765
       │       ├─→ 发送 REGISTER 消息
       │       └─→ 等待 REGISTER_ACK
       │
       └─→ 调用 useRealtimeAPI() (可选)
```

**关键文件**:
- `src/components/vrmViewer.tsx`: VRM 渲染器
- `src/components/websocketManager.tsx`: WebSocket 管理器
- `src/components/useExternalLinkage.tsx`: 外部连接 Hook

**时间**: T+300ms ~ T+500ms

---

### 阶段 4: WebSocket 连接建立 (T+500ms)

```
5. WebSocket 连接流程
   │
   ├─→ OrtensiaClient.connect()
   │   ├─→ 创建 WebSocket 实例
   │   ├─→ ws.onopen
   │   │   ├─→ 发送 REGISTER 消息
   │   │   │   {
   │   │   │     type: 'register',
   │   │   │     from: 'aituber-{timestamp}-{random}',
   │   │   │     client_type: 'aituber_client'
   │   │   │   }
   │   │   │
   │   │   └─→ 启动心跳定时器 (30秒)
   │   │
   │   ├─→ ws.onmessage
   │   │   └─→ handleMessage()
   │   │       ├─→ 消息去重检查
   │   │       └─→ 通知订阅者 (OrtensiaManager)
   │   │
   │   └─→ 收到 REGISTER_ACK
   │       └─→ 连接成功
   │
   └─→ 延迟 1.5 秒后发送 GET_CONVERSATION_ID
       └─→ 发现已有对话
```

**关键文件**:
- `src/utils/OrtensiaClient.ts`: WebSocket 客户端

**时间**: T+500ms ~ T+2000ms

---

### 阶段 5: 消息处理器注册 (T+2000ms)

```
6. 注册消息处理器
   │
   └─→ assistant.tsx useEffect (第二个)
       ├─→ 注册 handleAituberReceiveText
       │   └─→ manager.on(MessageType.AITUBER_RECEIVE_TEXT, handler)
       │
       ├─→ 注册 handleAgentCompleted
       │   └─→ manager.on(MessageType.AGENT_COMPLETED, handler)
       │
       ├─→ 注册 handleConversationDiscovered
       │   └─→ manager.on(MessageType.GET_CONVERSATION_ID_RESULT, handler)
       │
       └─→ 标记处理器就绪
           └─→ manager.markHandlersReady()
               ├─→ state.handlersRegistered = true
               └─→ 检查并触发对话发现
                   └─→ client.discoverExistingConversations()
```

**关键文件**:
- `src/pages/assistant.tsx`: 消息处理逻辑

**时间**: T+2000ms ~ T+2500ms

---

### 阶段 6: 对话发现 (T+2500ms)

```
7. 对话发现流程
   │
   ├─→ OrtensiaClient.discoverExistingConversations()
   │   ├─→ 检查 WebSocket 连接状态
   │   ├─→ 发送 GET_CONVERSATION_ID 消息
   │   └─→ 等待响应
   │
   ├─→ 服务器处理
   │   ├─→ 广播 EXECUTE_JS 到所有 cursor_inject 客户端
   │   ├─→ 收集 conversation_id 列表
   │   └─→ 返回 GET_CONVERSATION_ID_RESULT
   │
   └─→ 收到响应
       ├─→ handleConversationDiscovered()
       ├─→ 创建 Conversation tabs
       ├─→ 设置 autoCheckEnabled = true (默认)
       └─→ 添加欢迎消息
```

**时间**: T+2500ms ~ T+3500ms

---

### 阶段 7: VRM 模型加载 (T+3000ms)

```
8. VRM 模型加载 (延迟 3 秒)
   │
   └─→ loadModel() 函数执行
       ├─→ 检查 homeStore.viewer 是否存在
       │
       ├─→ 如果存在
       │   ├─→ 调用 viewer.loadVrm('/vrm/ortensia.vrm')
       │   ├─→ 加载 3D 模型文件
       │   ├─→ 解析 VRM 格式
       │   ├─→ 初始化骨骼、表情、动画
       │   └─→ 开始渲染循环
       │
       └─→ 如果不存在
           ├─→ retryCount++
           ├─→ 等待 1 秒
           └─→ 重试 (最多 10 次)
```

**关键文件**:
- `src/features/vrmViewer/viewer.ts`: VRM 场景管理
- `src/features/vrmViewer/model.ts`: VRM 模型操作

**时间**: T+3000ms ~ T+4000ms

---

### 阶段 8: 系统就绪 (T+4000ms)

```
9. ✅ 系统完全就绪
   │
   ├─→ WebSocket 连接: ✅ 已连接
   ├─→ 消息处理器: ✅ 已注册
   ├─→ 对话发现: ✅ 已完成
   ├─→ VRM 模型: ✅ 已加载
   └─→ 可以接收和处理消息
```

---

## 模块加载顺序详解

### 1. Next.js 层面

| 顺序 | 模块 | 文件 | 时机 | 说明 |
|------|------|------|------|------|
| 1 | Document | `_document.tsx` | 首次请求 | HTML 结构、字体加载 |
| 2 | App | `_app.tsx` | 每次路由 | 全局样式、i18n、主题 |
| 3 | Page | `assistant.tsx` | 路由匹配 | 页面组件渲染 |

### 2. React 组件层面

| 顺序 | 组件 | 文件 | 加载方式 | 时机 |
|------|------|------|----------|------|
| 1 | AssistantPage | `assistant.tsx` | 同步 | 路由匹配时 |
| 2 | VrmViewer | `vrmViewer.tsx` | 动态 (ssr: false) | 组件挂载后 |
| 3 | WebSocketManager | `websocketManager.tsx` | 动态 (ssr: false) | isLoaded = true |
| 4 | MultiConversationChat | `MultiConversationChat.tsx` | 同步 | 正常模式时 |

### 3. 管理器层面

| 顺序 | 管理器 | 文件 | 初始化时机 | 说明 |
|------|--------|------|------------|------|
| 1 | OrtensiaManager | `OrtensiaManager.ts` | assistant.tsx useEffect | 单例，统一消息分发 |
| 2 | OrtensiaClient | `OrtensiaClient.ts` | OrtensiaManager.initialize() | 单例，WebSocket 客户端 |
| 3 | AutoTaskChecker | `AutoTaskChecker.ts` | assistant.tsx useState | 自动任务检查器 |

### 4. 状态管理层面

| 顺序 | Store | 文件 | 初始化时机 | 说明 |
|------|-------|------|------------|------|
| 1 | homeStore | `stores/home.ts` | Next.js 启动 | 全局状态（viewer、chatLog） |
| 2 | settingsStore | `stores/settings.ts` | Next.js 启动 | 应用设置 |
| 3 | conversationStore | `stores/conversationStore.ts` | assistant.tsx | 多对话状态 |

---

## 核心模块设计

### 1. OrtensiaManager (中央协调器)

**职责**: 统一管理消息分发和生命周期

**设计模式**: 单例模式

**核心方法**:

```typescript
class OrtensiaManager {
  // 初始化（幂等）
  initialize(): void
  
  // 注册消息处理器
  on(messageType: MessageType, handler: MessageHandler): () => void
  
  // 标记处理器就绪
  markHandlersReady(): void
  
  // 分发消息（内部）
  private dispatchMessage(message: OrtensiaMessage): void
}
```

**状态机**:

```
[未初始化]
    │
    ↓ initialize()
[客户端创建中]
    │
    ↓ clientReady = true
[等待处理器注册]
    │
    ↓ markHandlersReady()
[处理器就绪]
    │
    ↓ checkAndDiscoverConversations()
[对话发现中]
    │
    ↓ discoveryRequested = true
[系统就绪]
```

**关键特性**:
- ✅ 幂等初始化（多次调用只执行一次）
- ✅ 防止重复订阅（isSubscribed 标记）
- ✅ 状态机管理（确保正确的初始化顺序）
- ✅ React Strict Mode 兼容

---

### 2. OrtensiaClient (WebSocket 客户端)

**职责**: WebSocket 通信和消息管理

**设计模式**: 单例模式

**核心方法**:

```typescript
class OrtensiaClient {
  // 连接到服务器
  connect(url?: string): Promise<void>
  
  // 订阅消息
  subscribe(subscriber: Subscriber): () => void
  
  // 发送消息
  send(message: OrtensiaMessage): void
  
  // 发现已有对话
  discoverExistingConversations(): void
  
  // 发送文本到 Cursor
  sendCursorInputText(text: string, conversationId: string, isAuto?: boolean): void
}
```

**消息去重机制**:

```typescript
private processedMessages: Map<string, number> = new Map()

const messageKey = `${message.type}_${message.from}_${message.timestamp}`
if (this.processedMessages.has(messageKey)) {
  return // 跳过重复消息
}
this.processedMessages.set(messageKey, Date.now())
```

**心跳机制**:

```typescript
private startHeartbeat(): void {
  this.heartbeatTimer = setInterval(() => {
    this.send({
      type: MessageType.HEARTBEAT,
      from: this.clientId,
      timestamp: Date.now()
    })
  }, 30000) // 30 秒
}
```

---

### 3. ConversationStore (多对话状态)

**职责**: 管理多个 Cursor 对话的状态

**数据结构**:

```typescript
interface Conversation {
  id: string
  title: string
  messages: Message[]
  autoCheckEnabled: boolean
  lastActivity: number
}

interface ConversationStore {
  conversations: Map<string, Conversation>
  activeConversationId: string | null
  
  getOrCreateConversation(id: string, title?: string): Conversation
  addMessage(convId: string, message: Message): void
  getAutoCheckEnabled(convId: string): boolean
  setAutoCheckEnabled(convId: string, enabled: boolean): void
}
```

**关键方法**:

```typescript
// 获取或创建对话（默认 autoCheckEnabled = true）
getOrCreateConversation(id: string, title?: string): Conversation {
  if (!this.conversations.has(id)) {
    this.conversations.set(id, {
      id,
      title: title || `对话 ${id.substring(0, 8)}`,
      messages: [],
      autoCheckEnabled: true, // ✅ 默认启用
      lastActivity: Date.now(),
    })
  }
  return this.conversations.get(id)!
}
```

---

### 4. AutoTaskChecker (自动任务检查器)

**职责**: 管理自动任务检查逻辑和防抖

**核心方法**:

```typescript
class AutoTaskChecker {
  private lastCheckTime: Map<string, number> = new Map()
  private debounceTime: number = 5000 // 5 秒防抖
  
  // 检查是否可以触发（防抖）
  canTriggerCheck(conversationId: string): boolean
  
  // 记录检查时间
  recordCheck(conversationId: string): void
  
  // 获取检查提示词
  getCheckPrompt(): string
  
  // 检查是否应该停止
  shouldStop(text: string, eventType?: string): boolean
}
```

**防抖逻辑**:

```typescript
canTriggerCheck(conversationId: string): boolean {
  const lastCheck = this.lastCheckTime.get(conversationId) || 0
  const now = Date.now()
  return now - lastCheck > this.debounceTime
}
```

---

## 状态管理架构

### Store 层次结构

```
┌─────────────────────────────────────────┐
│         Zustand Store 系统               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐  │
│  │  homeStore   │  │ settingsStore│  │
│  │              │  │              │  │
│  │ • viewer     │  │ • language   │  │
│  │ • chatLog    │  │ • theme      │  │
│  │ • messages   │  │ • voice      │  │
│  └──────────────┘  └──────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   conversationStore              │  │
│  │                                  │  │
│  │ • conversations: Map<id, Conv>    │  │
│  │ • activeConversationId           │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### 状态流转

```
用户操作 / 消息接收
    │
    ↓
更新 Store
    │
    ├─→ homeStore (全局状态)
    ├─→ conversationStore (对话状态)
    └─→ settingsStore (设置)
    │
    ↓
触发 React 重新渲染
    │
    ↓
UI 更新
```

---

## 消息流转机制

### 1. 接收消息流程

```
WebSocket 收到消息
    │
    ↓
OrtensiaClient.handleMessage()
    │
    ├─→ 消息去重检查
    │   ├─ 生成唯一 key: `${type}_${from}_${timestamp}`
    │   ├─ 检查 processedMessages Map
    │   └─ 如果重复 → 跳过
    │
    ├─→ 通知所有订阅者
    │   └─→ subscriber(message) (只有 OrtensiaManager)
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

### 3. TTS 音频播放流程

```
收到 aituber_receive_text 消息
    │
    ↓
handleAituberReceiveText()
    │
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

## 时序图

### 完整启动时序

```
时间轴 →
│
├─ T+0ms    │ Next.js 请求处理
│           │ ├─ _document.tsx 渲染
│           │ └─ _app.tsx 渲染
│
├─ T+200ms  │ React 组件渲染
│           │ ├─ assistant.tsx 挂载
│           │ ├─ 创建状态 (isLoaded, isMiniMode)
│           │ └─ 初始化 stores
│
├─ T+300ms  │ OrtensiaManager 初始化
│           │ ├─ manager.initialize()
│           │ ├─ 创建 OrtensiaClient (单例)
│           │ └─ 设置消息分发器
│
├─ T+400ms  │ 动态组件加载
│           │ ├─ VrmViewer (延迟加载)
│           │ │  ├─ 创建 Three.js 场景
│           │ │  └─ 加载默认 VRM 模型
│           │ │
│           │ └─ WebSocketManager (延迟加载)
│           │    └─ useExternalLinkage()
│
├─ T+500ms  │ WebSocket 连接
│           │ ├─ OrtensiaClient.connect()
│           │ ├─ 发送 REGISTER
│           │ └─ 收到 REGISTER_ACK
│
├─ T+2000ms │ 消息处理器注册
│           │ ├─ 注册 handleAituberReceiveText
│           │ ├─ 注册 handleAgentCompleted
│           │ ├─ 注册 handleConversationDiscovered
│           │ └─ manager.markHandlersReady()
│
├─ T+2500ms │ 对话发现
│           │ ├─ client.discoverExistingConversations()
│           │ ├─ 发送 GET_CONVERSATION_ID
│           │ └─ 收到 GET_CONVERSATION_ID_RESULT
│
├─ T+3000ms │ VRM 模型加载
│           │ ├─ loadModel() 执行
│           │ ├─ 检查 viewer 是否存在
│           │ └─ 加载 /vrm/ortensia.vrm
│
└─ T+4000ms │ ✅ 系统就绪
            │ ├─ WebSocket: ✅
            │ ├─ 处理器: ✅
            │ ├─ 对话: ✅
            │ └─ VRM: ✅
```

### React Strict Mode 双重挂载

```
开发模式下的双重挂载：

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

---

## 关键设计决策

### 1. 为什么使用 OrtensiaManager？

**问题**:
- 多个组件需要监听 WebSocket 消息
- React Strict Mode 导致重复订阅
- 消息被处理多次
- 组件间通信复杂

**解决方案**:
- ✅ 单一订阅点（OrtensiaManager）
- ✅ 统一消息分发
- ✅ 状态机管理初始化顺序
- ✅ 防止重复订阅

### 2. 为什么需要消息去重？

**问题**:
- WebSocket 可能重复发送消息
- React 双重挂载可能导致重复处理

**解决方案**:
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

**问题**:
- React Strict Mode 可能导致 WebSocket 连接时序不确定
- 首次调用时 WebSocket 可能还未连接

**解决方案**:
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

**原因**:
- 用户期望自动化工作流
- 手动启用容易被忘记
- 可以随时手动关闭

**实现**:
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

### 5. 为什么 VRM 加载延迟 3 秒？

**原因**:
- VrmViewer 组件是动态加载的（ssr: false）
- 需要等待 Three.js 和 VRM 引擎初始化
- 确保 viewer 实例已创建

**实现**:
```typescript
// assistant.tsx
setTimeout(loadModel, 3000) // 延迟 3 秒

const loadModel = async () => {
  const viewer = homeStore.getState().viewer
  if (viewer) {
    viewer.loadVrm('/vrm/ortensia.vrm')
  } else {
    // 重试逻辑（最多 10 次，每次间隔 1 秒）
  }
}
```

---

## 故障排查指南

### 问题 1: 消息被处理多次

**症状**: 同一条消息触发 4 次处理器

**原因**:
- `OrtensiaManager.initialize()` 被调用多次
- 每次都调用 `client.subscribe()`

**解决**:
```typescript
// OrtensiaManager.ts
private isSubscribed: boolean = false

public initialize() {
  if (!this.isSubscribed) {
    this.client.subscribe(...)
    this.isSubscribed = true
  }
}
```

### 问题 2: 自动检查不触发

**症状**: Agent 完成但没有发送"继续"提示

**可能原因**:
1. `autoCheckEnabled = false` → 检查 conversation store
2. Conversation ID 不匹配 → 使用短 ID 匹配
3. 防抖未通过 → 等待 5 秒

**诊断**:
```typescript
console.log(`🎯 [Auto Check] 当前所有对话:`)
allConvs.forEach(([id, conv]) => {
  console.log(`  - ${id}: autoCheck=${conv.autoCheckEnabled}`)
})
```

### 问题 3: VRM 加载错误

**症状**: `Error: You have to load VRM first`

**原因**: 动画在 VRM 加载前就尝试加载

**解决**:
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

### 问题 4: WebSocket 连接失败

**症状**: 无法连接到 ws://localhost:8765

**检查清单**:
1. ✅ 确认 WebSocket 服务器已启动
   ```bash
   lsof -i :8765
   ```
2. ✅ 检查服务器日志
   ```bash
   tail -f /tmp/ws_server.log
   ```
3. ✅ 确认 ChatTTS 虚拟环境已激活
4. ✅ 检查防火墙设置

### 问题 5: 对话发现失败

**症状**: 没有发现已有的 Cursor 对话

**可能原因**:
1. Cursor Inject 未安装或未运行
2. WebSocket 连接未建立
3. 消息处理器未注册

**诊断**:
```typescript
// 检查连接状态
const client = OrtensiaClient.getInstance()
console.log('WebSocket 状态:', client?.ws?.readyState)

// 检查处理器
const manager = OrtensiaManager.getInstance()
console.log('处理器状态:', manager.getState())
```

---

## 性能优化建议

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

### 2. VRM 模型预加载

```typescript
// 在后台预加载常用模型
async preloadModels() {
  const models = ['/vrm/ortensia.vrm', '/vrm/AvatarSample_A.vrm']
  await Promise.all(
    models.map(url => fetch(url).then(r => r.blob()))
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

### A. 文件结构

```
aituber-kit/src/
├── pages/
│   ├── _document.tsx           # HTML 文档结构
│   ├── _app.tsx                # 应用级初始化
│   └── assistant.tsx           # 主页面组件
│
├── components/
│   ├── vrmViewer.tsx           # VRM 渲染器
│   ├── websocketManager.tsx    # WebSocket 管理器
│   ├── useExternalLinkage.tsx  # 外部连接 Hook
│   └── MultiConversationChat.tsx # 多对话 UI
│
├── utils/
│   ├── OrtensiaManager.ts      # 中央协调器
│   ├── OrtensiaClient.ts       # WebSocket 客户端
│   └── AutoTaskChecker.ts      # 自动检查逻辑
│
├── features/
│   ├── stores/
│   │   ├── home.ts             # 全局状态
│   │   ├── settings.ts         # 应用设置
│   │   └── conversationStore.ts # 对话状态
│   │
│   ├── vrmViewer/
│   │   ├── viewer.ts          # VRM 场景管理
│   │   └── model.ts            # VRM 模型操作
│   │
│   └── emoteController/
│       ├── emoteController.ts # 表情控制器
│       └── animationController.ts # 动画管理
│
└── styles/
    ├── globals.css             # 全局样式
    ├── themes.css              # 主题样式
    └── ortensia-theme.css      # オルテンシア主题
```

### B. 消息类型

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

### C. 配置项

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

// VRM 加载配置
const config = {
  initialDelay: 3000,            // 3 秒
  maxRetries: 10,                // 最多重试 10 次
  retryInterval: 1000,           // 每次重试间隔 1 秒
}
```

---

## 更新日志

- **2025-12-17**: 创建详细设计报告
  - 添加完整的模块加载顺序
  - 添加启动流程详解
  - 添加时序图
  - 添加故障排查指南
  - 添加性能优化建议

---

**文档维护者**: AI Assistant  
**最后更新**: 2025-12-17  
**版本**: 2.0



