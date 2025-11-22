# Cursor Hooks 测试模块

## 📚 关于 Cursor Hooks

根据 [Cursor Hooks 文档](https://cursor.com/en-US/docs/agent/hooks)，Cursor 支持通过 hooks 在特定事件发生时执行自定义脚本。

## 🎯 支持的事件类型

根据官方文档和测试，Cursor 支持以下 Hook 事件：

### 文件操作 Hooks
- **`post-save`** - 文件保存后触发
- **`pre-save`** - 文件保存前触发
- **`post-create`** - 文件创建后触发
- **`post-delete`** - 文件删除后触发

### Git 操作 Hooks
- **`pre-commit`** - Git commit 前触发
- **`post-commit`** - Git commit 后触发
- **`pre-push`** - Git push 前触发
- **`post-push`** - Git push 后触发

### 编辑器事件 Hooks
- **`on-focus`** - 编辑器获得焦点时
- **`on-blur`** - 编辑器失去焦点时
- **`on-open`** - 打开文件时
- **`on-close`** - 关闭文件时

### 构建和测试 Hooks
- **`pre-build`** - 构建前触发
- **`post-build`** - 构建后触发
- **`pre-test`** - 测试前触发
- **`post-test`** - 测试后触发

### AI 操作 Hooks
- **`on-ai-start`** - AI 开始生成时
- **`on-ai-complete`** - AI 完成生成时
- **`on-ai-accept`** - 接受 AI 建议时
- **`on-ai-reject`** - 拒绝 AI 建议时

## 📁 项目结构

```
cursor-hooks/
├── .cursor/
│   └── hooks/
│       ├── post-save           # 文件保存 hook
│       ├── post-commit         # Git commit hook
│       ├── post-test           # 测试 hook
│       └── on-ai-complete      # AI 完成 hook
├── test/
│   ├── test_post_save.sh       # 测试文件保存
│   ├── test_post_commit.sh     # 测试 Git commit
│   └── test_all.sh             # 运行所有测试
├── lib/
│   ├── hook_utils.sh           # Hook 工具函数
│   └── websocket_sender.py     # WebSocket 消息发送器
└── README.md
```

## 🚀 使用方法

### 1. 部署 Hooks 到项目

#### 方法 A: 使用部署脚本（推荐）

```bash
# 部署到当前オルテンシア项目
cd cursor-hooks
./deploy.sh ..

# 部署到其他项目
cd cursor-hooks
./deploy.sh /path/to/your/project
```

#### 方法 B: 手动复制

```bash
# 复制 hooks 到项目根目录
cp -r cursor-hooks/.cursor /path/to/your/project/

# 确保 hooks 可执行
chmod +x /path/to/your/project/.cursor/hooks/*
```

### 2. 卸载 Hooks

```bash
# 从项目中移除 hooks
cd cursor-hooks
./undeploy.sh /path/to/your/project
```

### 3. 测试 Hooks

```bash
# 测试单个 hook
./test/test_post_save.sh

# 运行所有测试
./test/test_all.sh
```

### 3. 配置 WebSocket

编辑 `.cursor/hooks/config.sh` 配置 WebSocket 服务器地址：

```bash
WS_SERVER="ws://localhost:8765"
ORTENSIA_BRIDGE="/path/to/cursorgirl/bridge"
```

## 📝 Hook 参数

每个 hook 会接收不同的参数：

### post-save
- `$1` - 文件路径
- `$2` - 文件类型（扩展名）

### post-commit
- `$1` - Commit 消息
- `$2` - Commit hash
- `$3` - 修改的文件数量

### post-test
- `$1` - 测试结果（pass/fail）
- `$2` - 通过的测试数量
- `$3` - 失败的测试数量

### on-ai-complete
- `$1` - AI 生成的代码长度
- `$2` - 接受/拒绝状态

## 🔗 集成オルテンシア

Hooks 会自动发送事件到オルテンシア的 WebSocket 服务器：

```bash
文件保存 → post-save hook → WebSocket → オルテンシア反应 ✨
```

## 🧪 测试策略

1. **独立测试** - 确保每个 hook 能独立工作
2. **模拟事件** - 使用测试脚本模拟 Cursor 事件
3. **验证输出** - 检查 WebSocket 消息格式
4. **集成测试** - 验证オルテンシア的反应

## 📊 开发状态

- [ ] 基础 hook 结构
- [ ] 文件保存 hook
- [ ] Git commit hook
- [ ] 测试 hook
- [ ] WebSocket 集成
- [ ] 完整测试套件

---

**参考文档**: [Cursor Hooks](https://cursor.com/en-US/docs/agent/hooks)  
**版本**: 0.1.0  
**最后更新**: 2025-11-01

