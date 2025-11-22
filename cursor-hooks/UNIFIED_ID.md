# 统一 ID 策略 - 快速参考

## 🎯 核心问题

你提出的三个关键问题：
1. ❌ 无法区分多个 Cursor 实例
2. ✅ 短连接设计正确（但需要优化）
3. ❌ 同一会话的不同 hook 使用不同 ID

**额外挑战**：inject 启动时没有 workspace/conversation 信息

---

## ✅ 解决方案

### ID 格式

| 组件 | ID 格式 | 示例 | 说明 |
|------|---------|------|------|
| **Cursor Hook** | `cursor-{pid}` | `cursor-12345` | 基于进程 PID |
| **Agent Hook** | `agent-hook-{ws}-{conv}` | `agent-hook-d42b-ed81` | workspace+conversation 哈希 |

### 关联方式

通过 **workspace** 字段关联：

```
Cursor: cursor-12345
  ├─ workspace: /Users/user/project
  │
Agent: agent-hook-d42b-ed81
  ├─ workspace: /Users/user/project  ← 相同！
  └─ related_cursor_id: cursor-d42b
```

---

## 📊 实际效果

### 测试结果
```
Workspace: cursorgirl
客户端ID: agent-hook-d42b-ed81
关联Cursor: cursor-d42b
```

### 服务器日志
```
[13:50:10] ✅ [agent-hook-d42b-ed81] 注册成功
[13:50:19] ✅ [agent-hook-d42b-ed81] 注册成功  ← 相同 ID
```

---

## 🎯 优点

1. **独立生成**：无需进程间通信
2. **稳定追踪**：同一会话用相同 ID
3. **可关联**：通过 workspace 建立联系
4. **简单可靠**：无竞态条件和文件锁

---

## 📚 详细文档

- `ID_STRATEGY.md` - 完整设计文档
- `DESIGN_DECISIONS.md` - 架构决策说明

