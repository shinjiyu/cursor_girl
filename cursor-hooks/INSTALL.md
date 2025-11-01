# Cursor Hooks 安装和使用指南

## ✅ 测试结果

所有 Hooks 测试通过：
- ✅ post-save Hook - 文件保存事件
- ✅ post-commit Hook - Git 提交事件

## 📦 安装方法

### 方法 1: 复制到现有项目（推荐）

```bash
# 1. 进入你的项目目录
cd /path/to/your/project

# 2. 复制 .cursor 目录
cp -r "/Users/user/Documents/ cursorgirl/cursor-hooks/.cursor" .

# 3. 确保 hooks 可执行
chmod +x .cursor/hooks/*

# 4. 配置 WebSocket 服务器地址（如果需要）
vi .cursor/hooks/config.sh
```

### 方法 2: 使用符号链接

```bash
# 1. 进入你的项目目录
cd /path/to/your/project

# 2. 创建符号链接
ln -s "/Users/user/Documents/ cursorgirl/cursor-hooks/.cursor" .cursor

# 3. 确保 hooks 可执行
chmod +x .cursor/hooks/*
```

## 🔧 配置

编辑 `.cursor/hooks/config.sh`：

```bash
# WebSocket 服务器地址
WS_SERVER="ws://localhost:8000/ws"

# オルテンシア Bridge 路径
BRIDGE_PATH="/Users/user/Documents/ cursorgirl/bridge"

# Python 虚拟环境路径
VENV_PATH="${BRIDGE_PATH}/venv"

# 是否启用调试模式
DEBUG=true

# 是否启用 WebSocket 发送
ENABLE_WEBSOCKET=true
```

## 🚀 使用方法

### 前置条件

确保オルテンシア服务正在运行：

```bash
# Terminal 1: WebSocket 服务器
cd "/Users/user/Documents/ cursorgirl/bridge"
source venv/bin/activate
python websocket_server.py

# Terminal 2: AITuber Kit（可选，用于可视化）
cd "/Users/user/Documents/ cursorgirl/aituber-kit"
npm run dev
# 浏览器访问: http://localhost:3000/assistant
```

### Cursor 中使用

1. **打开项目**: 在 Cursor 中打开安装了 hooks 的项目

2. **正常编码**: Cursor 会自动触发 hooks

3. **观察反应**: 
   - 保存文件 → オルテンシア: "保存成功~" 😊
   - Git commit → オルテンシア: "太棒了！代码提交成功~" 🎉

## 🎯 支持的事件

目前已实现：
- ✅ **post-save** - 文件保存后
- ✅ **post-commit** - Git 提交后

计划实现：
- ⏳ pre-commit - Git 提交前
- ⏳ post-push - Git 推送后
- ⏳ on-build - 构建时
- ⏳ on-test - 测试时
- ⏳ on-error - 错误时

## 📝 日志查看

```bash
# 实时查看日志
tail -f /tmp/cursor-hooks.log

# 查看最近 50 行
tail -50 /tmp/cursor-hooks.log

# 清空日志
> /tmp/cursor-hooks.log
```

## 🐛 故障排查

### Hook 没有触发

1. **检查 hooks 是否可执行**:
   ```bash
   ls -l .cursor/hooks/
   # 应该看到 -rwxr-xr-x 权限
   ```

2. **检查配置文件**:
   ```bash
   cat .cursor/hooks/config.sh
   # 确保路径正确
   ```

3. **手动测试 hook**:
   ```bash
   ./.cursor/hooks/post-save "test.txt" "$(pwd)"
   ```

### オルテンシア 没有反应

1. **检查 WebSocket 服务器**:
   ```bash
   lsof -i :8000
   # 应该看到 Python 进程
   ```

2. **检查日志**:
   ```bash
   tail -50 /tmp/cursor-hooks.log
   # 查找错误信息
   ```

3. **测试 WebSocket 连接**:
   ```bash
   cd "/Users/user/Documents/ cursorgirl/bridge"
   source venv/bin/activate
   python websocket_client.py
   ```

### Python 环境问题

```bash
# 检查虚拟环境
ls -la "/Users/user/Documents/ cursorgirl/bridge/venv"

# 重新创建虚拟环境
cd "/Users/user/Documents/ cursorgirl/bridge"
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🧪 测试

```bash
cd "/Users/user/Documents/ cursorgirl/cursor-hooks"

# 测试单个 hook
./test/test_post_save.sh
./test/test_post_commit.sh

# 运行所有测试
./test/test_all.sh
```

## 📊 工作原理

```
┌─────────────────────────────────────────────────────────┐
│  Cursor 事件流程                                        │
└─────────────────────────────────────────────────────────┘

1. 保存文件
   ↓
2. Cursor 触发 post-save hook
   ↓
3. Hook 脚本执行
   ├─ 收集文件信息（文件名、类型、路径）
   ├─ 记录日志
   └─ 调用 Python WebSocket 发送器
      ↓
4. WebSocket 发送器
   ├─ 连接到 WebSocket 服务器 (ws://localhost:8000/ws)
   ├─ 构建消息（文件保存 → "保存成功~" + neutral 情绪）
   └─ 发送消息
      ↓
5. WebSocket 服务器
   ├─ 接收消息
   ├─ 生成 TTS 音频（macOS TTS）
   └─ 广播给所有客户端
      ↓
6. AITuber Kit 前端
   ├─ 接收消息
   ├─ 更新表情和动作
   └─ 播放语音
      ↓
7. オルテンシア 说话 ✨
   "保存成功~" 😊
```

## 🎨 自定义

### 添加新的事件类型

1. **创建 hook 脚本**:
   ```bash
   cp .cursor/hooks/post-save .cursor/hooks/on-error
   chmod +x .cursor/hooks/on-error
   ```

2. **修改脚本内容**: 编辑 `on-error`

3. **更新消息映射**: 编辑 `lib/websocket_sender.py`
   ```python
   messages = {
       # ...
       'on_error': ('出错了...别担心，我们一起修复它~', 'sad'),
   }
   ```

4. **测试**: 创建对应的测试脚本

### 自定义消息和情绪

编辑 `cursor-hooks/lib/websocket_sender.py`:

```python
def get_message_for_event(event_type: str, event_data: dict) -> tuple[str, str]:
    messages = {
        'file_save': ('你的自定义消息', '自定义情绪'),
        # ...
    }
```

支持的情绪类型：
- `neutral` - 中性
- `happy` - 开心
- `sad` - 难过
- `angry` - 生气
- `relaxed` - 放松
- `surprised` - 惊讶
- `excited` - 兴奋

## 📚 参考

- [Cursor Hooks 官方文档](https://cursor.com/en-US/docs/agent/hooks)
- オルテンシア 项目: `/Users/user/Documents/ cursorgirl`
- WebSocket 架构: `WEBSOCKET_ARCHITECTURE.md`

## ✨ 效果演示

```bash
💻 你: 保存文件 (Cmd+S)
🎀 オルテンシア: "保存成功~" 😊

💻 你: git commit -m "feat: add feature"
🎀 オルテンシア: "太棒了！代码提交成功~" 🎉

💻 你: npm test (测试通过)
🎀 オルテンシア: "测试通过！你真厉害！" 🎊
```

---

**状态**: ✅ 测试通过，可以使用  
**版本**: 1.0.0  
**最后更新**: 2025-11-01

🎊 **享受和オルテンシア一起编程的乐趣吧！**

