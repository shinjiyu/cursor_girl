# V9 快速开始指南

**版本**: V9  
**更新**: 2025-11-04

---

## 🚀 5 分钟快速开始

### 步骤 1: 安装 V9 到 Cursor

```bash
cd cursor-injector
./install-v9.sh
```

**预期输出**:
```
创建备份...
✅ V9 已注入 - 正确的 DOM 操作流程
```

### 步骤 2: 重启 Cursor

完全退出 Cursor：
```bash
# Mac: 按 Cmd+Q
# 或者命令行
killall Cursor
```

重新启动 Cursor，等待 **10 秒**。

### 步骤 3: 验证安装

查看日志：
```bash
cat /tmp/cursor_ortensia.log
```

**应该看到**:
```
🎉 Ortensia V9 启动中...
✅ 本地 WebSocket Server 启动成功！
📍 端口: 9876
```

### 步骤 4: 运行测试

```bash
cd cursor-injector
python3 test_complete_flow.py
```

**预期行为**:
1. ✅ 自动切换到 Editor tab
2. ✅ 自动唤出 Composer（如果需要）
3. ✅ 输入测试文字
4. ✅ 点击上箭头按钮提交
5. ✅ Agent 开始工作

---

## 🎯 使用场景

### 场景 1: 开发调试（本地模式）

**适用于**: 开发和测试单个 Cursor 实例

```bash
# 不需要中央 Server，直接使用
python3 test_complete_flow.py
```

**特点**:
- ✅ 无需额外配置
- ✅ 快速测试功能
- ✅ 本地 WebSocket Server (9876)

### 场景 2: 生产环境（中央 Server 模式）

**适用于**: 多个 Cursor 实例，远程控制

```bash
# 1. 启动中央 Server
cd bridge
python3 websocket_server.py

# 2. 设置环境变量
export ORTENSIA_SERVER=ws://localhost:8765

# 3. 重启 Cursor
killall Cursor
# 重新启动 Cursor

# 4. 运行 Command Client
cd examples
python3 command_client_example.py
```

**特点**:
- ✅ 支持多个 Cursor 实例
- ✅ 远程控制
- ✅ 消息路由和广播

---

## 📖 常用命令

### 测试相关

```bash
# 完整流程测试
python3 test_complete_flow.py

# 单个功能测试
python3 test_complete_flow.py --individual

# 快速连接测试
python3 quick_test.py

# DOM 监控（实时查看状态）
python3 dom_monitor.py
```

### 日志相关

```bash
# 查看日志
cat /tmp/cursor_ortensia.log

# 实时监控日志
tail -f /tmp/cursor_ortensia.log

# 清空日志
rm /tmp/cursor_ortensia.log
```

### 安装相关

```bash
# 安装 V9
./install-v9.sh

# 恢复原始版本（使用备份）
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup \
   /Applications/Cursor.app/Contents/Resources/app/out/main.js

# 重新签名
codesign --force --deep --sign - /Applications/Cursor.app
```

---

## 🔧 配置选项

### 环境变量

```bash
# 中央 Server 地址（可选）
export ORTENSIA_SERVER=ws://your-server:8765

# 示例：本地
export ORTENSIA_SERVER=ws://localhost:8765

# 示例：远程
export ORTENSIA_SERVER=ws://192.168.1.100:8765
```

**持久化设置**（添加到 `~/.zshrc` 或 `~/.bashrc`）:
```bash
echo 'export ORTENSIA_SERVER=ws://localhost:8765' >> ~/.zshrc
source ~/.zshrc
```

---

## ❓ 常见问题

### Q1: 安装后 Cursor 无法启动

**A**: 检查签名是否成功

```bash
# 重新签名
codesign --force --deep --sign - /Applications/Cursor.app

# 如果还是不行，恢复备份
cp /Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup \
   /Applications/Cursor.app/Contents/Resources/app/out/main.js
```

### Q2: 日志中没有任何输出

**A**: 确保 Cursor 完全重启

```bash
# 完全退出
killall Cursor

# 清空旧日志
rm /tmp/cursor_ortensia.log

# 重启 Cursor
# 等待 10 秒

# 查看新日志
cat /tmp/cursor_ortensia.log
```

### Q3: 测试脚本连接失败

**A**: 检查本地 Server 是否启动

```bash
# 查看日志
cat /tmp/cursor_ortensia.log | grep "9876"

# 应该看到
✅ 本地 WebSocket Server 启动成功！
📍 端口: 9876

# 测试端口
lsof -i :9876
```

### Q4: 输入文字后没有反应

**A**: 检查是否在 Editor tab

```bash
# 手动切换到 Editor tab
# 或者运行
python3 invoke_composer.py
```

### Q5: 找不到提交按钮

**A**: 这是正常的，按钮在输入后才出现

**解决方案**: 已在 V9 中修复，会自动等待按钮出现

### Q6: Agent 不开始工作

**A**: 检查上箭头按钮是否成功点击

```bash
# 运行诊断
python3 find_clickable_elements.py

# 应该能看到 .send-with-mode 元素
```

---

## 🐛 故障排查

### 检查清单

- [ ] Cursor 已完全重启（Cmd+Q）
- [ ] 等待了至少 10 秒
- [ ] 日志文件存在且有内容
- [ ] 本地 Server 在 9876 端口启动
- [ ] Python 依赖已安装（`websockets`）
- [ ] Cursor 在 Editor tab（不是 Agents）

### 详细诊断

```bash
# 1. 检查日志
cat /tmp/cursor_ortensia.log

# 2. 检查端口
lsof -i :9876

# 3. 检查进程
ps aux | grep Cursor

# 4. 测试连接
python3 quick_test.py

# 5. 查看 DOM
python3 diagnose_dom.py
```

---

## 📚 更多资源

### 文档

- `docs/V9_IMPLEMENTATION_SUMMARY.md` - 完整实施总结
- `docs/IMPLEMENTATION_STATUS.md` - 当前状态
- `docs/WEBSOCKET_PROTOCOL.md` - 协议规范
- `docs/END_TO_END_TESTING_GUIDE.md` - 测试指南

### 示例

- `cursor-injector/test_complete_flow.py` - 完整流程测试
- `examples/command_client_example.py` - Command Client 示例
- `cursor-injector/dom_monitor.py` - DOM 监控工具

### 工具

- `cursor-injector/quick_test.py` - 快速测试
- `cursor-injector/diagnose_dom.py` - DOM 诊断
- `cursor-injector/invoke_composer.py` - 唤出 Composer

---

## 🎓 进阶使用

### 自定义提示词

```python
from composer_operations import ComposerOperator

async def custom_prompt():
    operator = ComposerOperator()
    await operator.connect()
    
    result = await operator.execute_prompt(
        prompt="你的自定义提示词",
        wait_for_completion=True,
        timeout=120
    )
    
    print(f"结果: {result}")

# 运行
import asyncio
asyncio.run(custom_prompt())
```

### 批量执行

```python
async def batch_prompts():
    operator = ComposerOperator()
    await operator.connect()
    
    prompts = [
        "生成一个 Python 函数",
        "解释代码",
        "优化性能"
    ]
    
    for prompt in prompts:
        result = await operator.execute_prompt(prompt, wait_for_completion=True)
        print(f"完成: {prompt}")
        await asyncio.sleep(2)  # 等待一下再执行下一个
```

### 状态监控

```python
async def monitor_status():
    operator = ComposerOperator()
    await operator.connect()
    
    while True:
        status = await operator.is_agent_working()
        print(f"Agent 状态: {status}")
        await asyncio.sleep(1)
```

---

## 💡 最佳实践

### 1. 使用 Editor Tab

```python
# 推荐：使用 ensure_composer_ready
await operator.ensure_composer_ready()

# 不推荐：手动检查
input_result = await operator.find_input()
```

### 2. 等待完成

```python
# 推荐：等待完成确保下一个命令有效
result = await operator.execute_prompt(
    prompt="...",
    wait_for_completion=True,
    timeout=60
)

# 不推荐：不等待可能导致冲突
result = await operator.execute_prompt(
    prompt="...",
    wait_for_completion=False
)
# 立即发送下一个命令 ❌
```

### 3. 错误处理

```python
# 推荐：始终检查结果
result = await operator.execute_prompt("...")
if result['success']:
    print("成功")
else:
    print(f"失败: {result.get('error')}")

# 不推荐：假设总是成功
result = await operator.execute_prompt("...")
# 直接使用 result ❌
```

---

## 🎉 完成！

现在你已经成功安装并测试了 V9 系统。

**下一步建议**:
1. 尝试自定义提示词
2. 集成到你的工作流
3. 探索进阶功能

**需要帮助?**
- 查看 `docs/` 目录下的详细文档
- 运行 `python3 dom_monitor.py` 实时查看状态
- 查看 `/tmp/cursor_ortensia.log` 日志

---

*祝你使用愉快！* 🚀

