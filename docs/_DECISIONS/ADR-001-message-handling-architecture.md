# ADR-001: 消息处理架构

> **状态**: 已采纳  
> **日期**: 2025-12-08  
> **决策者**: AI Assistant

## 背景

在实现 AITuber 与 Cursor 的通信时，遇到了以下问题：

1. React Strict Mode 导致 `useEffect` 执行两次
2. WebSocket 消息被重复处理（最多 4 次）
3. 消息订阅和取消订阅时序混乱
4. 多个组件需要订阅同一消息类型

## 决策

### 采用 OrtensiaManager 单例模式

#### 架构

```
┌─────────────────────────────────────────────────────────┐
│                   OrtensiaManager (单例)                 │
│                                                          │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │  OrtensiaClient  │───►│  消息分发器               │   │
│  │  (WebSocket)     │    │  handlers: Map<Type, Set>│   │
│  └──────────────────┘    └──────────────────────────┘   │
│                                                          │
│  isSubscribed: boolean  (防止重复订阅)                    │
└─────────────────────────────────────────────────────────┘
         │
         │ 分发消息
         ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Handler 1      │  │  Handler 2      │  │  Handler 3      │
│  (assistant.tsx)│  │  (其他组件)      │  │  ...            │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

#### 关键设计

1. **单例模式**：全局只有一个 OrtensiaManager 实例
2. **isSubscribed 标记**：防止重复订阅 OrtensiaClient
3. **handlers Map**：每个消息类型可以有多个处理器
4. **返回取消函数**：`on()` 方法返回取消订阅的函数

#### 代码示例

```typescript
// 注册处理器
const unsubscribe = OrtensiaManager.on(MessageType.XXX, handler)

// 在 useEffect cleanup 中取消
return () => unsubscribe()
```

## 替代方案

### 方案 A: 直接在组件中订阅 OrtensiaClient

**问题**：React Strict Mode 会导致多次订阅

### 方案 B: 使用 Context 传递

**问题**：复杂度高，不适合跨层级共享

### 方案 C: 使用 Redux/Zustand 中间件

**问题**：过度工程化

## 后果

### 正面

- 消息只被处理一次
- 组件可以独立订阅/取消订阅
- 支持 React Strict Mode
- 代码结构清晰

### 负面

- 额外的抽象层
- 需要理解 Manager 的生命周期
- 调试时需要检查多层

## 相关文档

- [OrtensiaManager 实现](../../aituber-kit/src/utils/OrtensiaManager.ts)
- [问题修复记录](../ORTENSIA_MANAGER_SOLUTION.md)
- [架构指南](../AITUBER_ARCHITECTURE_GUIDE.md)

