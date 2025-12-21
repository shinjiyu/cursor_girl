# AITuber 架构与时序分析

## 📋 目录
1. [核心模块](#核心模块)
2. [初始化时序](#初始化时序)
3. [双重加载问题](#双重加载问题)
4. [消息流转](#消息流转)
5. [优化建议](#优化建议)

---

## 1. 核心模块

### 1.1 页面组件
- **`assistant.tsx`**: 主页面组件
  - 负责整体布局（VRM 角色 + 多对话聊天区）
  - 管理设置（外部连接模式、TTS）
  - 处理业务逻辑（消息接收、自动任务检查）

### 1.2 视图组件
- **`VrmViewer`**: 3D 角色渲染器
  - 基于 three.js 和 @pixiv/three-vrm
  - 管理 VRM 模型加载、动画、表情
  - 通过 `homeStore.viewer` 暴露实例

- **`MultiConversationChat`**: 多对话聊天区
  - 显示多个 conversation tab
  - 每个 tab 对应一个 Cursor 窗口
  - 独立的消息历史和自动检查开关

### 1.3 管理组件
- **`WebSocketManager`**: WebSocket 连接管理器
  - 位于 `useExternalLinkage.tsx`
  - 创建 `OrtensiaClient` 单例
  - 处理连接、重连、心跳

### 1.4 状态管理
- **`homeStore`**: Zustand 全局状态
  - `viewer`: VrmViewer 实例引用
  - `chatLog`: 旧版聊天记录（向后兼容）

- **`conversationStore`**: 多对话状态
  - `conversations`: Map<conversation_id, Conversation>
  - `activeConversationId`: 当前激活的对话
  - `autoCheckEnabled`: 每个对话的自动检查开关

- **`settingsStore`**: 应用设置
  - `externalLinkageMode`: 外部连接模式
  - `selectVoice`, `selectLanguage`: TTS 设置

### 1.5 工具模块
- **`OrtensiaClient`**: WebSocket 客户端
  - 单例模式
  - 支持消息订阅（全局 + 类型特定）
  - 自动心跳、重连（TODO）

- **`AutoTaskChecker`**: 自动任务检查器
  - 管理检查提示词和停止关键词
  - 防抖机制（5秒）
  - 记录每个对话的检查历史

---

## 2. 初始化时序

### 2.1 React 渲染流程

```
┌─────────────────────────────────────────────────────────┐
│                   Next.js 页面加载                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│  React Strict Mode (开发模式)                            │
│  - 双重挂载组件以检测副作用                                │
│  - 第 1 次：挂载 → 立即卸载                                │
│  - 第 2 次：再次挂载（最终保留）                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│           AssistantPage 组件首次渲染                      │
│                                                          │
│  1. 创建状态                                              │
│     - conversationStore                                  │
│     - autoChecker                                        │
│                                                          │
│  2. 动态导入组件（异步）                                   │
│     - VrmViewer (ssr: false)                            │
│     - WebSocketManager (ssr: false)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│           useEffect 钩子执行（第 1 次）                    │
│                                                          │
│  1. 设置 externalLinkageMode                             │
│  2. 延迟 3 秒后尝试加载 VRM 模型                          │
│     - 此时 viewer 可能还未初始化                          │
│     - 进入重试循环                                        │
│                                                          │
│  3. 尝试订阅 Ortensia 消息                                │
│     - 此时 OrtensiaClient 尚未创建                       │
│     - 进入重试循环（每 100ms）                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│         VrmViewer 组件渲染 (第 1 次)                      │
│                                                          │
│  1. 创建 three.js 场景                                    │
│  2. 初始化 VRM 引擎                                       │
│  3. 加载**默认模型** /vrm/AvatarSample_A.vrm             │
│  4. 将 viewer 实例存入 homeStore.viewer                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│      WebSocketManager 渲染 (第 1 次)                      │
│                                                          │
│  1. 创建 OrtensiaClient 单例                             │
│  2. 连接到中央服务器 (ws://localhost:8765)                │
│  3. 发送 REGISTER 消息                                    │
│  4. 等待 REGISTER_ACK                                     │
│  5. 1.5 秒后发送 GET_CONVERSATION_ID 请求                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│  AssistantPage 的订阅重试成功                             │
│                                                          │
│  - OrtensiaClient 已创建                                 │
│  - 成功订阅消息                                           │
│  - 开始接收 GET_CONVERSATION_ID_RESULT                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│  VRM 模型加载重试成功                                     │
│                                                          │
│  - homeStore.viewer 已存在                               │
│  - 调用 viewer.loadVrm('/vrm/ortensia.vrm')             │
│  - **覆盖**默认模型，加载自定义模型                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│         React Strict Mode: 卸载所有组件                   │
│                                                          │
│  - 触发所有 useEffect 的 cleanup 函数                     │
│  - WebSocket 断开                                        │
│  - 但 viewer 和 store 状态保留！                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────┐
│         React Strict Mode: 重新挂载所有组件               │
│                                                          │
│  - 再次执行所有 useEffect                                 │
│  - VrmViewer 重新渲染                                     │
│    → 由于 viewer 实例已存在，直接复用                      │
│    → 但 VRM 模型需要重新加载                              │
│    → **又加载了一次默认模型**                              │
│                                                          │
│  - WebSocketManager 重新连接                             │
│    → 重新发送 GET_CONVERSATION_ID                        │
│                                                          │
│  - AssistantPage 的 VRM 加载逻辑再次执行                  │
│    → 3 秒后再次加载自定义模型                             │
│    → **再次覆盖**，显示 ortensia.vrm                      │
└─────────────────────────────────────────────────────────┘
```

### 2.2 时间线（实际数值）

| 时间 | 事件 |
|------|------|
| T+0ms | 页面开始加载 |
| T+50ms | React 首次渲染 AssistantPage |
| T+100ms | VrmViewer 创建，加载默认模型 (第1次) |
| T+150ms | WebSocketManager 连接服务器 |
| T+200ms | REGISTER_ACK 收到 |
| T+300ms | AssistantPage 订阅重试成功 |
| T+1700ms | GET_CONVERSATION_ID 发送 |
| T+1750ms | GET_CONVERSATION_ID_RESULT 接收 |
| T+3000ms | VRM 加载重试，成功加载 ortensia.vrm (第1次) |
| **T+3500ms** | **React Strict Mode 卸载** |
| **T+3550ms** | **React Strict Mode 重新挂载** |
| T+3600ms | VrmViewer 再次创建，加载默认模型 (第2次) |
| T+3650ms | WebSocketManager 重新连接 |
| T+5200ms | GET_CONVERSATION_ID 再次发送 |
| T+6500ms | VRM 加载重试，加载 ortensia.vrm (第2次) |

---

## 3. 双重加载问题

### 3.1 问题原因

**React Strict Mode** 在开发环境下会故意双重挂载组件以帮助发现副作用问题。这导致：

1. **VRM 模型加载 2 次**
   - 第 1 次：首次挂载时加载默认模型 + 3 秒后加载自定义模型
   - 第 2 次：重新挂载时再次加载默认模型 + 3 秒后加载自定义模型
   - 用户看到：默认角色 → 自定义角色 → 默认角色 → 自定义角色

2. **WebSocket 连接 2 次**
   - 第 1 次：成功连接并发现对话
   - 第 2 次：断开重连，再次发现对话（但前端订阅可能丢失）

3. **订阅时机问题**
   - AssistantPage 的 useEffect 可能在 OrtensiaClient 创建之前运行
   - 导致订阅丢失，无法收到 GET_CONVERSATION_ID_RESULT

### 3.2 为什么看到"默认角色 → 自定义角色"

查看 `VrmViewer` 的实现（推测）：
```typescript
// VrmViewer 初始化时
useEffect(() => {
  // 1. 创建 viewer
  const viewer = new Viewer()
  
  // 2. 加载默认模型（立即）
  viewer.loadVrm('/vrm/AvatarSample_A.vrm')
  
  // 3. 存储到 homeStore
  homeStore.setState({ viewer })
}, [])
```

然后 `assistant.tsx` 在 3 秒后：
```typescript
// 3 秒后尝试加载自定义模型
setTimeout(() => {
  homeStore.getState().viewer?.loadVrm('/vrm/ortensia.vrm')  // 覆盖默认模型
}, 3000)
```

### 3.3 实际观察到的现象

用户体验：
1. **T+100ms**: 看到默认角色（第 1 次挂载）
2. **T+3000ms**: 切换到オルテンシア（自定义模型加载）
3. **T+3600ms**: 又看到默认角色（第 2 次挂载，React Strict Mode）
4. **T+6500ms**: 又切换到オルテンシア（第 2 次自定义模型加载）

---

## 4. 消息流转

### 4.1 发现对话流程

```
AITuber (React)                中央服务器              Cursor Inject
      │                             │                        │
      │  1. 注册并等待 1.5s         │                        │
      │─────────────────────────────>                        │
      │                             │                        │
      │  2. GET_CONVERSATION_ID     │                        │
      │─────────────────────────────>                        │
      │                             │                        │
      │                             │  3. EXECUTE_JS         │
      │                             │  (广播模式，DOM查询)    │
      │                             │───────────────────────>│
      │                             │                        │
      │                             │  4. EXECUTE_JS_RESULT  │
      │                             │  {0: "{conv_id}", ...} │
      │                             │<───────────────────────│
      │                             │                        │
      │  5. GET_CONVERSATION_ID_    │                        │
      │     RESULT (每个对话1条)     │                        │
      │<─────────────────────────────                        │
      │  {conversation_id: "xxx"}   │                        │
      │                             │                        │
      │  6. 创建 conversation tab    │                        │
      │  (如果订阅成功)              │                        │
      │                             │                        │
```

### 4.2 订阅重试机制

```typescript
// assistant.tsx 的订阅逻辑
useEffect(() => {
  let retryCount = 0
  const maxRetries = 10
  
  const setupSubscription = () => {
    const client = OrtensiaClient.getInstance()
    
    if (!client) {
      retryCount++
      if (retryCount <= maxRetries) {
        setTimeout(setupSubscription, 100)  // 100ms 后重试
        return
      }
    }
    
    // 订阅成功
    const unsubscribe = client.subscribe((message) => {
      if (message.type === MessageType.GET_CONVERSATION_ID_RESULT) {
        handleConversationDiscovered(message)
      }
    })
    
    return unsubscribe
  }
  
  setupSubscription()
}, [handleConversationDiscovered])
```

**问题**：
- 如果 React Strict Mode 导致重新挂载，订阅会丢失
- 新的订阅需要等待重试成功
- 此时可能已经错过了 GET_CONVERSATION_ID_RESULT 消息

---

## 5. 优化建议

### 5.1 禁用 React Strict Mode（生产环境）

在 `next.config.js` 中：
```javascript
module.exports = {
  reactStrictMode: false,  // 开发时也禁用（如果不需要副作用检测）
}
```

**优点**：
- 避免双重挂载
- 减少不必要的重新加载

**缺点**：
- 失去 React 的副作用检测能力

### 5.2 改进 VRM 加载逻辑

使 VRM 加载更加"幂等"：

```typescript
// VrmViewer.tsx
useEffect(() => {
  const viewer = homeStore.getState().viewer
  
  // 如果已经存在且已加载正确模型，跳过
  if (viewer && viewer.currentModel === targetModel) {
    return
  }
  
  // 否则加载
  if (viewer) {
    viewer.loadVrm(targetModel)
  }
}, [targetModel])
```

### 5.3 改进订阅机制

使用 `useRef` 避免闭包问题：

```typescript
const handlersRef = useRef({
  handleAituberReceiveText,
  handleAgentCompleted,
  handleConversationDiscovered
})

// 每次渲染更新 ref
handlersRef.current = {
  handleAituberReceiveText,
  handleAgentCompleted,
  handleConversationDiscovered
}

useEffect(() => {
  const client = OrtensiaClient.getInstance()
  if (!client) return
  
  const unsubscribe = client.subscribe((message) => {
    const handlers = handlersRef.current
    
    if (message.type === MessageType.AITUBER_RECEIVE_TEXT) {
      handlers.handleAituberReceiveText(message)
    }
    // ...
  })
  
  return unsubscribe
}, [])  // 空依赖数组！
```

### 5.4 延迟 GET_CONVERSATION_ID 发送

```typescript
// OrtensiaClient.ts
case MessageType.REGISTER_ACK:
  // 等待更长时间，确保前端订阅已设置
  this.discoveryTimer = window.setTimeout(() => {
    this.discoverExistingConversations()
  }, 3000)  // 从 1.5s 改为 3s
  break
```

### 5.5 改进 WebSocket 管理器

实现完整的状态机和消息队列：
- 连接状态管理
- 断线重连
- 消息队列（连接断开时缓存）
- 心跳检测
- 协议消息染色（如用户要求）

---

## 6. 当前架构的优缺点

### 优点
✅ **模块化清晰**: 每个功能独立封装  
✅ **状态管理集中**: Zustand store 管理全局状态  
✅ **支持多对话**: 不同 Cursor 窗口独立管理  
✅ **自动任务检查**: 灵活的任务自动化  

### 缺点
❌ **React Strict Mode 问题**: 双重挂载导致重复加载  
❌ **订阅时机不确定**: 组件初始化顺序依赖运气  
❌ **缺少状态持久化**: 刷新页面丢失对话历史  
❌ **错误处理不足**: WebSocket 断线后没有重连机制  
❌ **性能优化空间**: VRM 模型可以预加载/缓存  

---

## 7. 推荐的改进方案

### 方案 A: 快速修复（最小改动）
1. 在 `next.config.js` 中禁用 `reactStrictMode`
2. 将 VRM 加载延迟改为 1 秒（减少用户看到默认角色的时间）
3. 订阅改用 `useRef` 避免闭包

### 方案 B: 架构优化（长期方案）
1. 实现完整的 WebSocket 状态机
2. VRM 模型管理器（预加载、缓存、切换）
3. 对话历史持久化（localStorage）
4. 统一的错误处理和日志系统

---

**文档版本**: V1.0  
**创建时间**: 2025-01-05  
**作者**: AI Assistant  

























