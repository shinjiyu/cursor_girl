# 最终方案：通过环境变量传递 inject ID

## 🎯 问题

你指出的关键问题：

1. **inject 不一定与 workspace 对应**
   - Cursor 可以不加载 workspace 启动（空窗口）
   - Cursor 可以中途修改 workspace（切换项目）

2. **之前的 workspace 映射方案有致命缺陷**
   ```
   时刻 0: workspace: /project/A → inject-12345
   时刻 1: 用户切换到 /project/B
        → 映射过期！无法找到正确的 inject ❌
   ```

---

## ✅ 最终方案：环境变量传递

### 核心思路

**inject 通过环境变量告诉 hook 自己的 ID**

```
inject 启动
  ├─→ 生成 ID: inject-{pid}
  ├─→ 设置环境变量: ORTENSIA_INJECT_ID=inject-12345
  │
  └─→ Cursor 调用 hook
        └─→ hook 继承环境变量
              └─→ 读取 ORTENSIA_INJECT_ID
                    └─→ 在消息中包含 inject_id
```

---

## 📊 完整流程

### 步骤 1：inject 设置环境变量

```javascript
// inject 启动时（in install-v9.sh）
const injectId = `inject-${process.pid}`;
process.env.ORTENSIA_INJECT_ID = injectId;
log(`📌 设置 inject ID: ${injectId}`);

// 连接到 server
await register();  // 使用 injectId 注册
```

### 步骤 2：hook 读取环境变量

```python
# hook 执行时（in agent_hook_handler.py）
inject_id = os.getenv('ORTENSIA_INJECT_ID', '')

if not inject_id:
    logger.warning("⚠️  未找到 ORTENSIA_INJECT_ID 环境变量")

# 在消息 payload 中包含 inject_id
message = {
    "type": "aituber_receive_text",
    "from": "hook-xxx",
    "payload": {
        "text": "命令完成",
        "inject_id": inject_id  # ← 关键！
    }
}
```

### 步骤 3：server 直接查找

```python
# server 处理消息时（in websocket_server.py）
async def handle_hook_message(message: Message):
    # 直接从消息中提取 inject_id
    inject_id = message.payload.get('inject_id')
    
    # 直接查找，无需 workspace 映射
    inject_client = registry.get_by_id(inject_id)
    
    if inject_client:
        # 发送新任务
        command = MessageBuilder.agent_execute_prompt(
            to_id=inject_id,
            prompt="新任务"
        )
        await inject_client.websocket.send(command.to_json())
```

---

## 🔄 数据流图

```
┌─────────────────────────────────────────┐
│ 1. Cursor 启动 (PID: 12345)              │
├─────────────────────────────────────────┤
│ inject 设置环境变量:                      │
│   process.env.ORTENSIA_INJECT_ID        │
│     = "inject-12345"                    │
│                                         │
│ inject 注册到 server:                    │
│   ID: inject-12345                      │
└─────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│ 2. Cursor 执行命令并调用 hook            │
├─────────────────────────────────────────┤
│ hook 继承环境变量:                        │
│   os.getenv('ORTENSIA_INJECT_ID')      │
│     → "inject-12345"                    │
│                                         │
│ hook 发送消息:                           │
│   payload.inject_id = "inject-12345"    │
└─────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│ 3. server 接收 hook 消息                 │
├─────────────────────────────────────────┤
│ 提取 inject_id: "inject-12345"          │
│   ↓                                     │
│ 查询 registry.get_by_id()               │
│   ↓                                     │
│ 找到: inject-12345 ✅                   │
└─────────────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│ 4. server 发送新任务                     │
├─────────────────────────────────────────┤
│ to: inject-12345                        │
│ command: agent_execute_prompt           │
└─────────────────────────────────────────┘
```

---

## ✨ 优点

| 特性 | workspace 映射方案 | 环境变量方案 |
|------|-------------------|--------------|
| **无 workspace 启动** | ❌ 失败 | ✅ 工作 |
| **切换 workspace** | ❌ 映射过期 | ✅ 不受影响 |
| **实现复杂度** | 需要维护映射表 | 简单直接 |
| **准确性** | 可能出错 | 100% 准确 |
| **维护成本** | 需要清理映射 | 无需维护 |

---

## 🔧 实现细节

### inject (install-v9.sh)

```javascript
// 启动时设置环境变量
const injectId = `inject-${process.pid}`;
process.env.ORTENSIA_INJECT_ID = injectId;

// 注册时使用这个 ID
function generateInjectId() {
    return `inject-${process.pid}`;
}
```

### hook (agent_hook_handler.py)

```python
# 读取环境变量
inject_id = os.getenv('ORTENSIA_INJECT_ID', '')

# 包含在消息中
message = {
    "payload": {
        "inject_id": inject_id
    }
}
```

### server (websocket_server.py)

```python
# 直接查找
async def find_inject_for_hook(message: Message):
    inject_id = message.payload.get('inject_id')
    return registry.get_by_id(inject_id)
```

---

## 🎯 术语说明

| 术语 | 说明 | 连接方式 | ID 格式 |
|------|------|----------|---------|
| **inject** | 注入到 Cursor 的 WebSocket 服务 | 长连接 | `inject-{pid}` |
| **hook** | Agent Hooks 脚本 | 短连接 | `hook-{hash}` |
| **server** | Ortensia 中央服务器 | - | - |

---

## 📝 使用场景

### 场景 1：收到 complete 事件，发送新任务

```python
# server 端代码
async def on_hook_complete(message):
    # 提取 inject_id
    inject_id = message.payload.get('inject_id')
    
    # 查找对应的 inject
    inject = registry.get_by_id(inject_id)
    
    # 发送新任务
    await inject.websocket.send(new_task.to_json())
```

### 场景 2：workspace 变化

```
时刻 0: workspace: /project/A
  → inject_id: inject-12345 (不变)
  
时刻 1: 切换到 /project/B
  → inject_id: inject-12345 (依然不变)
  
✅ 无论 workspace 如何变化，inject_id 始终有效
```

---

## 🚨 边界情况

### 1. 环境变量未设置

```python
inject_id = os.getenv('ORTENSIA_INJECT_ID', '')
if not inject_id:
    logger.warning("⚠️  inject 未正确设置环境变量")
    # 可以回退到其他方案，或者跳过
```

### 2. inject 重启（PID 改变）

```
旧 inject: inject-12345 (断开)
新 inject: inject-67890 (新 PID)

✅ hook 会自动使用新的 inject_id
```

---

## 📚 相关文档

- `QUICK_EXAMPLE.md` - 快速示例
- `ID_STRATEGY.md` - ID 设计策略
- `../bridge/example_find_cursor.py` - 完整代码示例

---

## 🎉 总结

**问题**：
- ❌ workspace 映射不可靠（Cursor 可以无 workspace 启动或切换 workspace）

**解决方案**：
- ✅ inject 通过环境变量传递自己的 ID
- ✅ hook 读取环境变量并包含在消息中
- ✅ server 直接通过 inject_id 查找

**优点**：
- ✅ 100% 准确
- ✅ 无需维护映射表
- ✅ 适用于所有场景（无 workspace / 切换 workspace）
- ✅ 实现简单

---

**最后更新**: 2025-11-22
**版本**: 3.0

