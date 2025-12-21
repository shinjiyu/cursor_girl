# OrtensiaManager：统一事件管理方案

## 🎯 问题根源

之前的实现存在多个问题：

1. **时序问题**：组件创建、WebSocket 连接、事件订阅的顺序不确定
2. **竞争条件**：消息可能在订阅者注册之前到达
3. **React Strict Mode**：开发模式下组件双重挂载导致重复订阅和清理
4. **职责分散**：创建、连接、订阅逻辑分散在多个组件中

## ✅ 解决方案：OrtensiaManager

创建一个**中央管理器**，统一协调所有 Ortensia 相关的操作。

### 核心设计

```typescript
class OrtensiaManager {
  // 单例模式
  private static instance: OrtensiaManager
  
  // 状态管理
  private state: {
    clientReady: boolean          // 客户端是否就绪
    handlersRegistered: boolean   // 处理器是否注册完成
    discoveryRequested: boolean   // 是否已发送发现请求
  }
  
  // 统一消息分发
  private handlers: Map<MessageType, Set<Handler>>
  
  // 关键方法
  initialize()          // 初始化客户端（只执行一次）
  on()                  // 注册消息处理器
  markHandlersReady()   // 标记处理器就绪，触发发现对话
}
```

### 工作流程

```
1. 组件加载
   ↓
2. manager.initialize()  → 创建 OrtensiaClient（只一次）
   ↓
3. manager.on(...)       → 注册各类消息处理器
   ↓
4. manager.markHandlersReady()  → 检查条件
   ↓
5. 如果 clientReady && handlersRegistered
   ↓
6. 自动发送 discoverExistingConversations()
   ↓
7. 消息到达 → 统一分发到已注册的处理器
```

## 📝 使用示例

### 在 assistant.tsx 中

```typescript
import OrtensiaManager from '@/utils/OrtensiaManager'

export default function AssistantPage() {
  useEffect(() => {
    // 1. 初始化管理器
    const manager = OrtensiaManager
    manager.initialize()
  }, [])
  
  useEffect(() => {
    const manager = OrtensiaManager
    
    // 2. 注册消息处理器
    const unsubscribe1 = manager.on(MessageType.AITUBER_RECEIVE_TEXT, (message) => {
      handleAituberReceiveText(message)
    })
    
    const unsubscribe2 = manager.on(MessageType.AGENT_COMPLETED, (message) => {
      handleAgentCompleted(message)
    })
    
    const unsubscribe3 = manager.on(MessageType.GET_CONVERSATION_ID_RESULT, (message) => {
      handleConversationDiscovered(message)
    })
    
    // 3. 标记处理器就绪（触发发现对话）
    manager.markHandlersReady()
    
    return () => {
      // 4. 清理
      unsubscribe1()
      unsubscribe2()
      unsubscribe3()
    }
  }, [handleAituberReceiveText, handleAgentCompleted, handleConversationDiscovered])
}
```

### 在 useExternalLinkage 中

```typescript
useEffect(() => {
  const manager = OrtensiaManager
  
  // 确保初始化
  manager.initialize()
  
  // 获取客户端实例
  const client = manager.getClient()
  
  // 注册消息处理器
  const unsubscribe = manager.on(MessageType.AITUBER_RECEIVE_TEXT, async (msg) => {
    await handleReceiveTextFromWs(...)
  })
  
  // 连接到服务器
  if (!client.isConnected()) {
    client.connect('ws://localhost:8765')
  }
  
  return () => {
    unsubscribe()
  }
}, [])
```

## 🎯 核心优势

### 1. 解决时序问题

**之前**：
```typescript
// ❌ 可能在客户端创建前就尝试订阅
const client = OrtensiaClient.getInstance()
if (!client) {
  // 需要重试逻辑...
}
```

**现在**：
```typescript
// ✅ 管理器确保正确顺序
manager.initialize()     // 创建客户端
manager.on(...)          // 注册处理器
manager.markHandlersReady()  // 自动触发后续操作
```

### 2. 解决竞争条件

**之前**：
```typescript
// ❌ 消息可能在订阅前到达
client.discoverExistingConversations()  // 立即发送
// ... 稍后才订阅处理器
client.subscribe(...)  // 太晚了！
```

**现在**：
```typescript
// ✅ 只有在处理器就绪后才发送请求
manager.on(...)              // 先注册处理器
manager.markHandlersReady()  // 检查条件后才发送请求
```

### 3. 解决 React Strict Mode 问题

**之前**：
```typescript
// ❌ Strict Mode 导致重复创建和订阅
useEffect(() => {
  const client = new OrtensiaClient()  // 创建两次
  client.subscribe(...)                 // 订阅两次
  return () => {
    unsubscribe()  // 清理导致第二次订阅失效
  }
})
```

**现在**：
```typescript
// ✅ 单例 + 幂等性设计
useEffect(() => {
  manager.initialize()  // 只创建一次（幂等）
  const unsub = manager.on(...)  // 可以多次注册
  return () => {
    unsub()  // 只清理自己的订阅
  }
})
```

### 4. 统一消息分发

**之前**：
```typescript
// ❌ 每个组件独立订阅
client.subscribe((msg) => {
  if (msg.type === 'A') handleA()
  if (msg.type === 'B') handleB()
})
```

**现在**：
```typescript
// ✅ 统一分发，支持多个处理器
manager.on('A', handleA1)
manager.on('A', handleA2)  // 同一类型可以有多个处理器
manager.on('B', handleB)
```

## 🔧 管理器状态机

```
状态转换：

INIT → clientReady=true (initialize 完成)
     ↓
     → handlersRegistered=true (markHandlersReady 调用)
     ↓
     → discoveryRequested=true (自动发送发现请求)
```

**条件检查**：
```typescript
private checkAndDiscoverConversations() {
  // 检查前置条件
  if (!clientReady) return        // 等待客户端
  if (!handlersRegistered) return  // 等待处理器
  if (discoveryRequested) return   // 避免重复

  // 所有条件满足，执行发现
  client.discoverExistingConversations()
}
```

## 📊 对比总结

| 维度 | 之前 | 现在 |
|------|------|------|
| **创建位置** | 分散在多个组件 | 统一在 Manager |
| **时序控制** | 手动重试 + setTimeout | 自动状态机 |
| **竞争处理** | 依赖 setTimeout 延迟 | 条件检查 + 标记 |
| **Strict Mode** | 需要复杂的去重逻辑 | 幂等性设计 |
| **消息分发** | 每个组件独立处理 | 统一分发 |
| **可维护性** | 低（逻辑分散） | 高（集中管理） |
| **可测试性** | 难（依赖组件生命周期） | 易（独立单元） |

## ✅ 结论

通过引入 `OrtensiaManager`：

1. ✅ **消除时序依赖**：组件加载顺序不再重要
2. ✅ **消除竞争条件**：消息总是在处理器就绪后发送
3. ✅ **简化组件代码**：不需要关心客户端创建和连接
4. ✅ **提高可维护性**：所有逻辑集中在一个地方
5. ✅ **支持 React Strict Mode**：幂等性设计天然支持

**不再需要处理时序和竞争问题！**

---

**创建时间**: 2025-12-08  
**目标**: 彻底解决 AITuber 的事件管理问题  
**方案**: 中央管理器 + 状态机 + 统一消息分发






















