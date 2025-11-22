# Cursor Hooks 快速开始

## 🎯 5 分钟快速体验

### 1. 复制 Hooks 到项目 (1分钟)

```bash
# 进入你的测试项目目录
cd ~/your-test-project

# 复制 hooks
cp -r "/Users/user/Documents/ cursorgirl/cursor-hooks/.cursor" .

# 设置权限
chmod +x .cursor/hooks/*
```

### 2. 启动オルテンシア (1分钟)

```bash
# 打开新终端
cd "/Users/user/Documents/ cursorgirl"
./START_ALL.sh

# 等待启动完成，看到:
# ✅ WebSocket 服务器运行中
# ✅ Next.js 开发服务器运行中
# ✅ Electron 窗口已打开
```

### 3. 在 Cursor 中测试 (3分钟)

1. **在 Cursor 中打开项目**
   ```bash
   cursor ~/your-test-project
   ```

2. **测试文件保存**
   - 创建或编辑任意文件
   - 按 `Cmd+S` 保存
   - 👀 观察オルテンシア说: "保存成功~" 😊

3. **测试 Git 提交**
   ```bash
   # 在项目中
   git init  # 如果还没有 Git 仓库
   git add .
   git commit -m "test: 测试オルテンシア"
   
   # 👀 观察オルテンシア说: "太棒了！代码提交成功~" 🎉
   ```

## 🎉 成功！

如果你看到オルテンシア响应了，恭喜！Cursor Hooks 已经工作了！

## 📋 查看日志

```bash
# 实时查看 hook 执行日志
tail -f /tmp/cursor-hooks.log

# 查看オルテンシア服务日志
tail -f /tmp/websocket_server.log
```

## 🐛 常见问题

### オルテンシア 没有反应？

```bash
# 检查 WebSocket 服务器
lsof -i :8765

# 如果没有运行，启动它
cd "/Users/user/Documents/ cursorgirl/bridge"
source venv/bin/activate
python websocket_server.py

# 检查日志
tail -20 /tmp/cursor-hooks.log
```

### Hook 没有触发？

```bash
# 手动测试 hook
cd ~/your-test-project
./.cursor/hooks/post-save "test.txt" "$(pwd)"

# 应该看到日志输出
```

## 📚 更多文档

- `README.md` - 完整功能说明
- `INSTALL.md` - 详细安装指南
- `STATUS.md` - 开发状态

## ✨ 支持的事件

当前版本支持：
- ✅ 文件保存 - "保存成功~"
- ✅ Git 提交 - "太棒了！代码提交成功~"

即将支持：
- ⏳ 构建成功/失败
- ⏳ 测试通过/失败
- ⏳ 代码错误检测

---

**享受和オルテンシア一起编程的乐趣！** 🎀✨

