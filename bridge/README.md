# Event Bridge - オルテンシア情感控制系统

将编程事件转换为オルテンシア的表情和对话。

## 📦 安装

```bash
cd bridge
pip install -r requirements.txt
```

## 🚀 快速开始

### 1. 启动 AITuber Kit（另一个终端）

```bash
cd ../aituber-kit
npm run assistant
```

### 2. 运行快速测试

```bash
# 快速测试（2分钟）
python test_emotions.py quick

# 完整测试（5-10分钟）
python test_emotions.py full

# 交互模式
python test_emotions.py interactive
```

## 📋 支持的事件类型

### 文件操作
- `file_save` - 文件保存
- `file_create` - 创建文件
- `file_delete` - 删除文件

### Git 操作
- `git_commit` - 提交代码
- `git_push` - 推送代码
- `git_merge` - 合并分支
- `git_conflict` - 冲突

### AI 工作
- `ai_start` - AI 开始工作
- `ai_thinking` - AI 思考中
- `ai_complete` - AI 完成

### 错误
- `syntax_error` - 语法错误
- `runtime_error` - 运行时错误
- `build_error` - 构建错误
- `critical_error` - 严重错误

### 测试
- `test_start` - 开始测试
- `test_pass` - 测试通过
- `test_fail` - 测试失败

### 调试
- `debug_start` - 开始调试
- `breakpoint_hit` - 断点命中
- `bug_found` - 发现 Bug
- `bug_fixed` - Bug 修复

### 性能
- `performance_slow` - 性能慢
- `performance_improved` - 性能提升

### 重构
- `refactor_start` - 开始重构
- `refactor_complete` - 重构完成

### 时间
- `work_start` - 开始工作
- `work_break` - 休息
- `work_complete` - 完成工作

### 特殊
- `celebration` - 庆祝
- `surprise` - 惊喜
- `thinking` - 思考
- `greeting` - 问候

## 🎭 支持的表情

- **neutral** - 中性/工作
- **happy** - 开心/成功
- **sad** - 难过/错误
- **angry** - 生气/严重错误
- **relaxed** - 放松/完成
- **surprised** - 惊讶/意外

## 🔧 命令行使用

### 基本用法

```bash
python cursor_event.py <event_type> [options]
```

### 示例

```bash
# 文件保存
python cursor_event.py file_save --file="main.py"

# Git 提交
python cursor_event.py git_commit --message="feat: add feature" --files=5

# 测试通过
python cursor_event.py test_pass --passed=10

# 语法错误
python cursor_event.py syntax_error --error="undefined variable x"

# 庆祝
python cursor_event.py celebration
```

## ⚙️ 配置

配置文件：`config/emotion_rules.yaml`

可以自定义：
- 事件 → 表情映射
- 对话模板
- 优先级
- 表情持续时间
- 上下文感知规则

## 📊 测试模式

### 快速测试（推荐）

展示所有 6 种表情类型，大约 2 分钟：

```bash
python test_emotions.py quick
```

### 完整测试

运行 6 个测试场景，展示各种编程情景：

```bash
python test_emotions.py full
```

场景包括：
1. 🌅 早上工作流
2. ✨ 成功提交流
3. 🐛 调试流程
4. 😱 错误处理流
5. 🎯 性能优化流
6. 🎉 特殊场景

### 交互模式

手动触发任意事件：

```bash
python test_emotions.py interactive
```

在交互模式中：
- 输入事件名称触发
- `list` - 查看所有可用事件
- `quick` - 运行快速测试
- `full` - 运行完整测试
- `quit` - 退出

## 🔌 WebSocket 连接

Event Bridge 通过 WebSocket 与 AITuber Kit 通信：

- **默认地址**: `ws://localhost:8000/ws`
- **消息格式**:
  ```json
  {
    "text": "消息内容",
    "role": "assistant",
    "emotion": "happy",
    "type": "assistant"
  }
  ```

## 🎯 下一步

### 集成到 Cursor IDE

创建 Cursor Hooks：

```bash
# .cursor/hooks/on-save.sh
#!/bin/bash
cd /path/to/bridge
python cursor_event.py file_save --file="$1"
```

### 自定义配置

编辑 `config/emotion_rules.yaml` 添加：
- 新的事件类型
- 自定义对话
- 调整优先级
- 修改表情持续时间

## 📝 开发

### 测试单个模块

```bash
# 测试情感映射器
python emotion_mapper.py

# 测试 WebSocket 客户端
python websocket_client.py
```

## 🐛 故障排除

### WebSocket 连接失败

确保：
1. AITuber Kit 正在运行
2. 透明悬浮窗已启动
3. WebSocket 地址正确（默认 `ws://localhost:8000/ws`）

### 表情没有变化

检查：
1. AITuber Kit 是否启用"外部連携"
2. VRM 模型是否正确加载
3. 查看终端日志

## 📄 许可

MIT License

