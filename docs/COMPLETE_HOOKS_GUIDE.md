# オルテンシア完整 Hooks 指南

## 📚 概述

オルテンシア现在支持**两种类型的 Hooks**，共计 **18 个 Hooks**！

### 🤖 Agent Hooks (9个)
控制和扩展 Cursor AI Agent 的行为

### 👧 IDE Event Hooks (9个)
监听 IDE 事件，提供编码陪伴和情感反馈

---

## 🎯 完整对照表

| 类型 | Hook 名称 | 触发时机 | 功能 | 状态 |
|------|----------|---------|------|------|
| **Agent** | `beforeShellExecution` | Agent 执行命令前 | 阻止危险命令 | ✅ 已实现 |
| **Agent** | `afterShellExecution` | Agent 执行命令后 | 审计日志 | ✅ 已实现 |
| **Agent** | `beforeMCPExecution` | Agent 执行 MCP 前 | MCP 工具审核 | ✅ 已实现 |
| **Agent** | `afterMCPExecution` | Agent 执行 MCP 后 | MCP 审计 | ✅ 已实现 |
| **Agent** | `afterFileEdit` | Agent 编辑文件后 | 自动格式化 | ✅ 已实现 |
| **Agent** | `beforeReadFile` | Agent 读取文件前 | 敏感信息过滤 | ✅ 已实现 |
| **Agent** | `beforeSubmitPrompt` | 提交 Prompt 前 | 提示审核 | ✅ 已实现 |
| **Agent** | `afterAgentResponse` | Agent 响应后 | 响应审计 | ✅ 已实现 |
| **Agent** | `stop` | Agent 循环结束 | 自动后续操作 | ✅ 已实现 |
| **IDE** | `post-save` | 文件保存后 | オルテンシア反馈 | ✅ 已实现 |
| **IDE** | `pre-commit` | Git commit 前 | オルテンシア提示 | ✅ 已实现 |
| **IDE** | `post-commit` | Git commit 后 | オルテンシア庆祝 | ✅ 已实现 |
| **IDE** | `post-push` | Git push 后 | オルテンシア鼓励 | ✅ 已实现 |
| **IDE** | `on-build` | 构建开始 | オルテンシア陪伴 | ✅ 已实现 |
| **IDE** | `post-build` | 构建完成 | オルテンシア反馈 | ✅ 已实现 |
| **IDE** | `on-test` | 测试开始 | オルテンシア陪伴 | ✅ 已实现 |
| **IDE** | `post-test` | 测试完成 | オルテンシア庆祝 | ✅ 已实现 |
| **IDE** | `on-error` | 发生错误 | オルテンシア安慰 | ✅ 已实现 |

**总计**: 18/18 实现 ✅

---

## Part 1: Agent Hooks（AI Agent 控制）

### 📁 架构

```
~/.cursor-agent/
├── hooks/                      # 所有 Agent Hook 脚本
│   ├── beforeShellExecution.py
│   ├── afterShellExecution.py
│   ├── beforeMCPExecution.py
│   ├── afterMCPExecution.py
│   ├── afterFileEdit.py
│   ├── beforeReadFile.py
│   ├── beforeSubmitPrompt.py
│   ├── afterAgentResponse.py
│   └── stop.py
├── lib/                        # 共享库
│   └── agent_hook_handler.py  # Hook 基类
├── hooks.json                  # 配置文件
├── deploy_agent_hooks.sh       # 部署脚本
└── test_agent_hooks.sh         # 测试脚本

~/.cursor/
└── hooks.json -> ~/.cursor-agent/hooks.json  # 符号链接
```

### 🚀 部署 Agent Hooks

#### 方法 A: 使用部署脚本（推荐）

```bash
cd /Users/user/Documents/ cursorgirl/.cursor-agent
./deploy_agent_hooks.sh
```

部署后会：
- 复制所有 hooks 到 `~/.cursor-agent/`
- 创建 `~/.cursor/hooks.json` 符号链接
- 设置可执行权限
- 显示使用说明

#### 方法 B: 手动部署

```bash
# 复制目录
cp -r /Users/user/Documents/ cursorgirl/.cursor-agent ~/.cursor-agent

# 设置权限
chmod +x ~/.cursor-agent/hooks/*.py
chmod +x ~/.cursor-agent/lib/*.py

# 创建符号链接
mkdir -p ~/.cursor
ln -s ~/.cursor-agent/hooks.json ~/.cursor/hooks.json
```

### 🧪 测试 Agent Hooks

```bash
cd /Users/user/Documents/ cursorgirl/.cursor-agent
./test_agent_hooks.sh
```

期望输出：
```
📝 测试: beforeShellExecution
✅ 通过 (输出包含: permission)

📝 测试: beforeShellExecution (危险命令)
✅ 通过 (输出包含: deny)

...

📊 测试结果:
   总计: 11
   通过: 11
   失败: 0

🎉 所有测试通过！
```

### 📖 Agent Hooks 详细说明

#### 1. beforeShellExecution

**触发时机**: Agent 执行 Shell 命令前

**输入数据**:
```json
{
  "command": "rm -rf /tmp/test",
  "cwd": "/Users/user/project"
}
```

**输出数据**:
```json
{
  "permission": "allow" | "deny" | "ask",
  "user_message": "提示消息",
  "agent_message": "Agent 消息"
}
```

**功能**:
- ✅ 阻止危险命令（如 `rm -rf /`）
- ⚠️ 确认风险命令（如 `rm -rf`, `git push --force`）
- ℹ️ 通知オルテンシア重要命令

**示例**:
```bash
# 允许普通命令
echo '{"command":"ls -la"}' | python3 ~/.cursor-agent/hooks/beforeShellExecution.py
# 输出: {"permission": "allow"}

# 阻止危险命令
echo '{"command":"rm -rf /"}' | python3 ~/.cursor-agent/hooks/beforeShellExecution.py
# 输出: {"permission": "deny", "user_message": "🚫 危险命令已被阻止"}
```

#### 2. afterShellExecution

**触发时机**: Agent 执行 Shell 命令后

**输入数据**:
```json
{
  "command": "npm build",
  "output": "Build successful!"
}
```

**功能**:
- 📊 审计命令执行
- ✅/❌ 检测成功/失败
- 📢 通知オルテンシア结果

#### 3. beforeMCPExecution

**触发时机**: Agent 执行 MCP 工具前

**输入数据**:
```json
{
  "tool_name": "delete_file",
  "tool_input": "{\"path\": \"/tmp/test.txt\"}"
}
```

**功能**:
- 🔒 审核敏感 MCP 工具
- ⚠️ 确认删除/修改操作

#### 4. afterMCPExecution

**触发时机**: Agent 执行 MCP 工具后

**输入数据**:
```json
{
  "tool_name": "read_file",
  "tool_input": "{}",
  "result_json": "{\"success\": true, \"content\": \"...\"}"
}
```

**功能**:
- 📊 审计 MCP 工具使用
- 📢 通知オルテンシア结果

#### 5. afterFileEdit

**触发时机**: Agent 编辑文件后

**输入数据**:
```json
{
  "file_path": "/Users/user/project/main.py",
  "edits": [
    {"old_string": "def foo():", "new_string": "def bar():"}
  ]
}
```

**功能**:
- 🎨 自动格式化（支持 Python, JS, TS, JSON, CSS, MD）
- 📊 审计文件修改
- 📢 通知オルテンシア

**支持的格式化工具**:
- Python: `black`
- JS/TS/JSX/TSX: `prettier`
- JSON/CSS/MD: `prettier`

#### 6. beforeReadFile

**触发时机**: Agent 读取文件前

**输入数据**:
```json
{
  "file_path": "/Users/user/.env",
  "content": "SECRET=xxx"
}
```

**功能**:
- 🔐 检测敏感文件
- ⚠️ 确认读取权限
- 🛡️ 保护密钥、证书、配置文件

**敏感文件模式**:
- `.env`, `.env.*`
- `id_rsa`, `*.pem`, `*.key`
- `password`, `secret`, `token`, `credentials`
- `.ssh/`, `.aws/`, `.kube/config`

#### 7. beforeSubmitPrompt

**触发时机**: 用户提交 Prompt 前

**输入数据**:
```json
{
  "prompt": "帮我写一个函数",
  "attachments": [
    {"type": "file", "filePath": "/Users/user/project/main.py"}
  ]
}
```

**输出数据**:
```json
{
  "continue": true | false
}
```

**功能**:
- 🔍 检测 Prompt 中的敏感信息
- ⚠️ 警告可能泄露的 API Key、密码、IP 地址
- 📢 通知オルテンシア新任务开始

#### 8. afterAgentResponse

**触发时机**: Agent 完成响应后

**输入数据**:
```json
{
  "text": "任务已完成！"
}
```

**功能**:
- 📊 审计 Agent 响应
- 🎉 检测任务完成
- 😢 检测错误情况
- 📢 通知オルテンシア

#### 9. stop

**触发时机**: Agent 循环结束

**输入数据**:
```json
{
  "status": "completed" | "aborted" | "error",
  "loop_count": 0
}
```

**输出数据**:
```json
{
  "followup_message": "继续优化代码"  // 可选
}
```

**功能**:
- 🎉 通知任务完成
- 😢 通知错误
- 🔄 可选：自动继续循环（最多 5 次）

---

## Part 2: IDE Event Hooks（编码陪伴）

### 📁 架构

```
project/.cursor/
├── hooks/                      # IDE Event Hook 脚本
│   ├── post-save
│   ├── pre-commit
│   ├── post-commit
│   ├── post-push
│   ├── on-build
│   ├── post-build
│   ├── on-test
│   ├── post-test
│   └── on-error
├── lib/                        # 共享库
│   ├── hook_utils.sh           # Bash 工具函数
│   └── websocket_sender.py     # WebSocket 消息发送器
└── hooks/
    └── config.sh               # 配置文件

cursor-hooks/
├── .cursor/                    # 源码
├── deploy.sh                   # 部署脚本
├── undeploy.sh                 # 卸载脚本
└── test/                       # 测试脚本
```

### 🚀 部署 IDE Event Hooks

#### 方法 A: 使用部署脚本（推荐）

```bash
cd cursor-hooks
./deploy.sh ..  # 部署到オルテンシア项目
# 或
./deploy.sh /path/to/your/project  # 部署到其他项目
```

#### 方法 B: 手动复制

```bash
cp -r cursor-hooks/.cursor /path/to/your/project/
chmod +x /path/to/your/project/.cursor/hooks/*
```

### 📖 IDE Event Hooks 详细说明

每个 IDE Event Hook 会：
1. 收集事件数据（文件名、路径、状态等）
2. 通过 WebSocket 发送到オルテンシア
3. オルテンシア 播放语音和动作

**示例输出** (WebSocket 消息):
```json
{
  "type": "file_save",
  "text": "保存成功~",
  "emotion": "happy",
  "audio_file": "/path/to/tts_output/xxx.wav",
  "timestamp": "2025-11-02T12:00:00"
}
```

---

## 🔧 配置

### Agent Hooks 配置 (`~/.cursor/hooks.json`)

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {"command": "python3 ~/.cursor-agent/hooks/beforeShellExecution.py"}
    ],
    "afterShellExecution": [
      {"command": "python3 ~/.cursor-agent/hooks/afterShellExecution.py"}
    ],
    // ... 其他 hooks
  }
}
```

### IDE Event Hooks 配置 (`.cursor/hooks/config.sh`)

```bash
# WebSocket 服务器地址
WS_SERVER="ws://localhost:8000/ws"

# オルテンシア项目路径（自动检测）
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BRIDGE_PATH="${PROJECT_ROOT}/bridge"

# 日志文件
LOG_FILE="/tmp/cursor-hooks.log"

# 调试模式
DEBUG=true
```

---

## 🎯 使用场景

### Agent Hooks 使用场景

1. **企业级安全**
   - 阻止危险命令（`rm -rf /`）
   - 审计所有 Agent 操作
   - 保护敏感文件（`.env`, `id_rsa`）

2. **代码质量**
   - Agent 编辑后自动格式化
   - 检测 Prompt 中的敏感信息
   - 审核 MCP 工具使用

3. **开发效率**
   - 实时监控 Agent 状态
   - 自动记录操作日志
   - 与オルテンシア集成反馈

### IDE Event Hooks 使用场景

1. **编码激励**
   - 保存文件: "保存成功~" 😊
   - Git commit: "太棒了！代码提交成功~" 🎉
   - 测试通过: "测试通过！你真厉害！" 🎊

2. **工作流提示**
   - 构建开始: "开始构建..." 😐
   - 测试开始: "开始测试..." 😐

3. **错误安慰**
   - 构建失败: "构建失败了...别担心~" 😢
   - 测试失败: "测试失败了...我们再检查一下~" 😢

---

## 📊 对比总结

| 特性 | Agent Hooks | IDE Event Hooks |
|------|------------|----------------|
| **目标** | 控制 AI Agent | 增强编码体验 |
| **配置位置** | `~/.cursor/hooks.json` | 项目 `.cursor/hooks/` |
| **触发者** | AI Agent | 用户操作 |
| **主要功能** | 安全/审计/格式化 | 反馈/鼓励/陪伴 |
| **企业级** | ✅ 云端分发 | ❌ 项目级配置 |
| **实时反馈** | ⚠️ 主要审计 | ✅ 语音+动作 |
| **オルテンシア集成** | ✅ 间接集成 | ✅ 直接集成 |

---

## 🚀 快速开始

### 1. 部署两种 Hooks

```bash
# 部署 Agent Hooks
cd /Users/user/Documents/ cursorgirl/.cursor-agent
./deploy_agent_hooks.sh

# 部署 IDE Event Hooks
cd /Users/user/Documents/ cursorgirl/cursor-hooks
./deploy.sh ..
```

### 2. 启动オルテンシア服务

```bash
cd /Users/user/Documents/ cursorgirl
./START_ALL.sh
```

### 3. 重启 Cursor

完全退出 Cursor 并重新打开

### 4. 开始编码

- 💾 保存文件 → オルテンシア: "保存成功~" 😊
- 🤖 Agent 执行命令 → 自动审核
- 📝 Agent 编辑文件 → 自动格式化
- 🔐 Agent 读取敏感文件 → 需要确认
- 🎉 任务完成 → オルテンシア: "太棒了！" 🎉

---

## 📝 日志

### Agent Hooks 日志

```bash
tail -f /tmp/cursor-agent-hooks.log
```

### IDE Event Hooks 日志

```bash
tail -f /tmp/cursor-hooks.log
```

### オルテンシア WebSocket 日志

```bash
tail -f /tmp/ortensia-websocket.log
```

---

## 🧪 测试

### 测试 Agent Hooks

```bash
cd /Users/user/Documents/ cursorgirl/.cursor-agent
./test_agent_hooks.sh
```

### 测试 IDE Event Hooks

```bash
# 测试保存文件
echo "test" > test.txt
./.cursor/hooks/post-save test.txt "$(pwd)"

# 测试 Git commit
./.cursor/hooks/post-commit "Initial commit" "abc123"
```

### 测试 WebSocket 连接

```bash
cd bridge
source venv/bin/activate
python cursor_event.py file_save
```

---

## 🎊 完成状态

### ✅ 已完成

**Agent Hooks (9/9)**:
- ✅ beforeShellExecution - 阻止危险命令
- ✅ afterShellExecution - 审计日志
- ✅ beforeMCPExecution - MCP 审核
- ✅ afterMCPExecution - MCP 审计
- ✅ afterFileEdit - 自动格式化
- ✅ beforeReadFile - 敏感信息过滤
- ✅ beforeSubmitPrompt - 提示审核
- ✅ afterAgentResponse - 响应审计
- ✅ stop - Agent 循环结束

**IDE Event Hooks (9/9)**:
- ✅ post-save - 文件保存
- ✅ pre-commit - Git commit 前
- ✅ post-commit - Git commit 后
- ✅ post-push - Git push 后
- ✅ on-build - 构建开始
- ✅ post-build - 构建完成
- ✅ on-test - 测试开始
- ✅ post-test - 测试完成
- ✅ on-error - 错误处理

**基础设施**:
- ✅ Agent Hook 基类和架构
- ✅ IDE Event Hook 工具函数库
- ✅ WebSocket 通信
- ✅ TTS 语音合成
- ✅ VRM 模型动作
- ✅ 部署脚本
- ✅ 测试脚本
- ✅ 完整文档

---

## 📚 相关文档

- `HOOKS_COMPARISON.md` - Hooks 对照表
- `README.md` - 项目主文档
- `HOOKS_GUIDE.md` - IDE Event Hooks 指南
- `.cursor-agent/README.md` - Agent Hooks 详细说明（待创建）

---

**版本**: 2.0.0  
**日期**: 2025-11-02  
**状态**: ✅ 18/18 Hooks 全部实现并测试通过

