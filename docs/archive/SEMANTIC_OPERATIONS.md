# Cursor 语义操作设计

**版本**: 1.0  
**日期**: 2025-11-03

---

## 🎯 什么是语义操作？

**语义操作**是**高层次的业务接口**，封装了完整的操作流程，而不是单一的底层动作。

###  对比：底层操作 vs 语义操作

| 类型 | 示例 | 特点 |
|------|------|------|
| **底层操作** | `composer_send_prompt` | 只做一件事：输入文字到输入框 |
| **语义操作** | `agent_execute_prompt` | 完整流程：输入 → 提交 → 执行 → 完成 |

---

## 📐 设计理念

### 1. 用户思维 vs 实现细节

**用户的真实需求**：
> "我要让 Cursor AI 帮我写一个函数"

**不应该是**：
```python
# 步骤 1: 输入文字
composer_send_prompt("写一个函数")
# 步骤 2: 点击提交按钮
click_submit()
# 步骤 3: 等待执行
wait_for_completion()
# 步骤 4: 获取结果
get_result()
```

**应该是**：
```python
# 一个语义操作完成所有步骤
agent_execute_prompt(
    prompt="写一个函数",
    wait_for_completion=True
)
```

### 2. 隐藏实现细节

**语义操作封装了**：
- ✅ DOM 操作（选择器、事件触发）
- ✅ 时序控制（等待、轮询）
- ✅ 错误处理（重试、超时）
- ✅ UI 变化适配（Cursor 版本更新）

**用户只需关心**：
- 💭 我要做什么？
- 📝 提示词是什么？
- ⏱️ 要不要等待完成？

---

## 🏗️ 实现架构

### 三层架构

```
┌─────────────────────────────────────────┐
│  语义层 (Semantic Layer)                │
│  • agent_execute_prompt                 │
│  • agent_stop_execution                 │
│  完整的业务操作                          │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│  协议层 (Protocol Layer)                │
│  • AGENT_EXECUTE_PROMPT 消息            │
│  • 路由、序列化、传输                   │
└─────────────────┬───────────────────────┘
                  │
                  v
┌─────────────────────────────────────────┐
│  实现层 (Implementation Layer)          │
│  • cursor_semantic_operations.js       │
│  • DOM 操作、状态检测、时序控制         │
└─────────────────────────────────────────┘
```

### 文件组织

```
cursor-injector/
├── cursor_semantic_operations.js     ✅ 语义操作实现
└── cursor_dom_operations.js          📦 DOM 操作封装（可选使用）

bridge/
└── protocol.py                        ✅ 协议定义（包含语义消息）

examples/
└── semantic_command_client.py         ✅ 使用示例
```

---

## 📋 API 设计

### 核心语义操作

#### 1. agent_execute_prompt（执行提示词）

**完整的操作流程**：输入 → 提交 → 执行 → （可选）等待完成

**协议消息**：
```json
{
  "type": "agent_execute_prompt",
  "from": "cc-001",
  "to": "cursor-abc123",
  "payload": {
    "agent_id": "default",
    "prompt": "写一个快速排序函数",
    "wait_for_completion": false,
    "timeout": 300000,
    "clear_first": true
  }
}
```

**JavaScript 实现**：
```javascript
async function handleAgentExecutePrompt(fromId, payload) {
    const { agent_id, prompt, wait_for_completion, timeout, clear_first } = payload;
    
    // 使用语义操作类
    const result = await window.CursorSemantic.agent.executePrompt(prompt, {
        waitForCompletion: wait_for_completion,
        timeout: timeout,
        clearFirst: clear_first
    });
    
    // 返回结果
    sendResult(fromId, result);
}
```

**Python 使用**：
```python
from protocol import MessageBuilder

# 创建消息
msg = MessageBuilder.agent_execute_prompt(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    prompt="写一个快速排序函数",
    wait_for_completion=False,  # 立即返回
    timeout=300000,             # 5 分钟
    clear_first=True            # 先清空输入框
)

# 发送
await ws.send(msg.to_json())

# 接收结果
response = json.loads(await ws.recv())
# => { "type": "agent_execute_prompt_result", "payload": { ... } }
```

**返回结果**：
```json
{
  "type": "agent_execute_prompt_result",
  "from": "cursor-abc123",
  "to": "cc-001",
  "payload": {
    "success": true,
    "agent_id": "default",
    "phase": "submitted",
    "message": "提示词已提交",
    "input_completed": true,
    "submit_completed": true,
    "execution_time": null,
    "status": null
  }
}
```

#### 2. agent_stop_execution（停止执行）

**停止正在执行的 Agent 任务**

**协议消息**：
```json
{
  "type": "agent_stop_execution",
  "from": "cc-001",
  "to": "cursor-abc123",
  "payload": {
    "agent_id": "default",
    "reason": "用户取消"
  }
}
```

**JavaScript 实现**：
```javascript
async function handleAgentStopExecution(fromId, payload) {
    const { agent_id, reason } = payload;
    
    // 使用语义操作类
    const result = window.CursorSemantic.agent.stopExecution();
    
    // 返回结果
    sendStopResult(fromId, result);
}
```

**Python 使用**：
```python
# 创建停止消息
msg = MessageBuilder.agent_stop_execution(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    reason="用户取消"
)

await ws.send(msg.to_json())
```

---

## 🔄 执行流程

### 不等待完成（wait_for_completion=False）

```
Command Client              Server              Cursor Hook
      │                       │                       │
      │─ agent_execute_prompt →                       │
      │                       │─ 路由 ──────────────→ │
      │                       │                       │
      │                       │                 ┌─────┴─────┐
      │                       │                 │ 1. 输入   │
      │                       │                 │ 2. 提交   │
      │                       │                 └─────┬─────┘
      │                       │                       │
      │                       │ ←── 返回结果 ─────────│
      │ ←─── 返回结果 ────────│                       │
      │                       │                       │
   ✅ 立即返回                                   Agent 继续执行
```

**优点**：
- ✅ 响应快速
- ✅ 不阻塞
- ✅ 适合异步场景

**适用场景**：
- 发送后无需等待结果
- 通过事件通知获取进度
- 多个并行任务

### 等待完成（wait_for_completion=True）

```
Command Client              Server              Cursor Hook
      │                       │                       │
      │─ agent_execute_prompt →                       │
      │   (wait=true)         │─ 路由 ──────────────→ │
      │                       │                       │
      │                       │                 ┌─────┴─────┐
      │                       │                 │ 1. 输入   │
      │                       │                 │ 2. 提交   │
      │                       │                 │ 3. 轮询   │
      │                       │                 │ 4. 检测   │
      │   ⏳ 等待...          │   ⏳ 等待...    │ 5. 完成   │
      │                       │                 └─────┬─────┘
      │                       │                       │
      │                       │ ←── 完成结果 ─────────│
      │ ←─── 完成结果 ────────│                       │
      │                       │                       │
   ✅ 收到完成通知
```

**优点**：
- ✅ 确保任务完成
- ✅ 获得最终状态
- ✅ 简化调用逻辑

**适用场景**：
- 需要任务结果才能继续
- 顺序执行的工作流
- 测试和验证

---

## 💡 设计亮点

### 1. 灵活的等待策略

**不强制等待**：
- 默认 `wait_for_completion=False`
- 适合大多数异步场景
- 通过事件通知获取进度

**可选等待**：
- 设置 `wait_for_completion=True`
- 适合需要确保完成的场景
- 超时保护避免永久阻塞

### 2. 详细的执行阶段

返回结果包含 `phase` 字段，指示执行到哪个阶段：

- `init` - 初始化
- `input` - 输入阶段
- `submit` - 提交阶段
- `executing` - 执行中
- `completed` - 已完成

**好处**：调试时可以精确定位问题

### 3. 渐进式返回信息

```json
{
  "success": true,
  "phase": "submitted",
  "input_completed": true,    // ✅ 输入完成
  "submit_completed": true,   // ✅ 提交完成
  "execution_time": null      // ⏳ 尚未执行
}
```

即使不等待完成，也能知道哪些步骤成功了。

### 4. 向后兼容

保留底层操作（`composer_send_prompt`），不影响现有代码。

**两者可以并存**：
- 需要精细控制 → 使用底层操作
- 需要简单易用 → 使用语义操作

---

## 🧪 测试示例

### 示例 1: 快速提交（不等待）

```python
msg = MessageBuilder.agent_execute_prompt(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    prompt="写一个二分查找",
    wait_for_completion=False,
    timeout=300000,
    clear_first=True
)

await ws.send(msg.to_json())

# 立即收到响应（约 500ms）
response = await ws.recv()
# => { success: true, phase: "submitted", ... }
```

### 示例 2: 等待完成

```python
msg = MessageBuilder.agent_execute_prompt(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    prompt="解释装饰器模式",
    wait_for_completion=True,
    timeout=60000,  # 60 秒
    clear_first=True
)

await ws.send(msg.to_json())

# 等待执行完成（可能需要几十秒）
response = await asyncio.wait_for(ws.recv(), timeout=65)
# => { success: true, phase: "completed", execution_time: 35000, ... }
```

### 示例 3: 停止执行

```python
# 先发送长任务
execute_msg = MessageBuilder.agent_execute_prompt(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    prompt="详细分析 Python GIL 的实现原理",
    wait_for_completion=False
)
await ws.send(execute_msg.to_json())

# 等待几秒
await asyncio.sleep(3)

# 发送停止指令
stop_msg = MessageBuilder.agent_stop_execution(
    from_id="cc-001",
    to_id="cursor-abc123",
    agent_id="default",
    reason="用户取消"
)
await ws.send(stop_msg.to_json())

# 收到停止结果
response = await ws.recv()
# => { success: true, message: "已发送停止指令" }
```

---

## 📊 与底层操作的对比

| 特性 | composer_send_prompt | agent_execute_prompt |
|------|---------------------|---------------------|
| **操作范围** | 只输入文字 | 输入 + 提交 + 执行 |
| **返回时机** | 输入完成后 | 可选：提交后 / 完成后 |
| **错误处理** | 输入失败 | 输入/提交/执行 各阶段 |
| **状态追踪** | 无 | 详细的 phase 信息 |
| **等待控制** | 无 | 可选 wait_for_completion |
| **适用场景** | 精细控制 | 业务操作 |

### 何时使用底层操作？

- 需要在输入后做其他操作（不立即提交）
- 需要精细控制每个步骤
- 实现自定义的提交逻辑

### 何时使用语义操作？

- 标准的"输入并执行"流程
- 简化调用代码
- 隐藏实现细节

---

## 🎯 最佳实践

### 1. 默认使用语义操作

```python
# ✅ 推荐：语义操作
msg = MessageBuilder.agent_execute_prompt(
    from_id="cc-001",
    to_id=cursor_id,
    agent_id="default",
    prompt="写一个函数",
    wait_for_completion=False
)
```

```python
# ⚠️  不推荐：除非需要精细控制
msg1 = MessageBuilder.composer_send_prompt(...)
msg2 = MessageBuilder.composer_click_submit(...)
msg3 = MessageBuilder.agent_wait(...)
```

### 2. 异步场景不等待

```python
# 发送多个任务
for task in tasks:
    msg = MessageBuilder.agent_execute_prompt(
        ...,
        wait_for_completion=False  # ✅ 不阻塞
    )
    await ws.send(msg.to_json())
    
# 通过事件通知获取完成状态
```

### 3. 关键任务要等待

```python
# 需要确保完成的任务
msg = MessageBuilder.agent_execute_prompt(
    ...,
    wait_for_completion=True  # ✅ 等待完成
)
```

### 4. 设置合理的超时

```python
# 短任务
timeout=30000   # 30 秒

# 中等任务
timeout=60000   # 60 秒

# 长任务
timeout=300000  # 5 分钟
```

---

## 🚀 未来扩展

### 计划中的语义操作

1. **editor_modify_file** - 修改文件
   - 打开文件 → 定位位置 → 修改内容 → 保存

2. **terminal_run_command** - 运行终端命令
   - 打开终端 → 输入命令 → 执行 → 获取输出

3. **project_add_file** - 添加文件
   - 创建文件 → 写入内容 → 保存 → 刷新文件树

4. **chat_ask_question** - 询问问题
   - 打开聊天 → 输入问题 → 获取回答

---

## 📝 总结

### 语义操作的核心价值

1. **简化调用** - 一个命令完成完整流程
2. **隐藏细节** - 用户无需了解 DOM 结构
3. **健壮性** - 封装了错误处理和重试逻辑
4. **可维护** - UI 变化只需修改实现层
5. **易扩展** - 可以轻松添加新的语义操作

### 使用建议

- ✅ **优先使用语义操作** - 对于标准业务流程
- ✅ **保留底层操作** - 对于特殊需求
- ✅ **灵活选择等待策略** - 根据场景决定
- ✅ **设置合理超时** - 避免永久阻塞

---

*最后更新: 2025-11-03*

