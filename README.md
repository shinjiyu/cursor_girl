# Ortensia - Cursor IDE 自动化控制系统

**版本**: V9  
**状态**: ✅ 核心功能完成  
**最后更新**: 2025-11-04

---

## 📖 简介

Ortensia 是一个用于程序化控制 Cursor IDE 的系统，通过注入 WebSocket 服务器到 Cursor 主进程，实现对 IDE 的完全自动化控制。

### 核心功能

- ✅ 自动输入提示词到 AI Composer
- ✅ 自动提交并触发 AI Agent 执行
- ✅ 检测 Agent 工作状态
- ✅ 支持本地开发模式和中央服务器模式
- ✅ WebSocket 协议通信
- ✅ Python 客户端库

---

## 🚀 快速开始

### 1. 安装 V9 注入

```bash
cd cursor-injector
./install-v9.sh
```

### 2. 重启 Cursor

完全退出 Cursor (Cmd+Q) 并重新启动。

### 3. 测试

```bash
python3 test_complete_flow.py
```

**详细指南**: 查看 [QUICK_START_V9.md](QUICK_START_V9.md)

---

## 📁 项目结构

```
cursorgirl/
├── cursor-injector/          # 注入相关
│   ├── install-v9.sh         # V9 注入脚本 ⭐
│   ├── composer_operations.py # 底层操作库 ⭐
│   ├── test_complete_flow.py # 完整测试
│   ├── test_final_click.py   # 最终验证
│   ├── auto_analyze_button.py # 按钮分析工具
│   ├── dom_monitor.py        # DOM 监控
│   └── ortensia_cursor_client.py # 客户端库
│
├── bridge/                   # 中央服务器
│   ├── websocket_server.py   # 中央 WebSocket Server
│   └── protocol.py           # 协议定义
│
├── docs/                     # 文档
│   ├── V9_IMPLEMENTATION_SUMMARY.md    # V9 实施总结
│   ├── IMPLEMENTATION_STATUS.md        # 实施状态
│   ├── WEBSOCKET_PROTOCOL.md           # 协议规范
│   └── ...
│
├── examples/                 # 示例
│   └── command_client_example.py
│
├── archive/                  # 归档（早期探索）
│
├── QUICK_START_V9.md        # 快速开始
├── V9_COMPLETION_REPORT.md  # 完成报告
├── TODO.md                  # 待办事项
└── README.md               # 本文件
```

---

## 🔑 关键发现

### 正确的 DOM 选择器

经过大量测试验证：

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 输入框 | `.aislash-editor-input` | Lexical 编辑器 |
| **提交按钮** | **`.send-with-mode > .anysphere-icon-button`** | ⚠️ 必须点击子元素！ |
| 按钮图标 | `.codicon-arrow-up-two` | 上箭头 |
| 状态指示器 | `[class*="loading" i]` | Loading 状态 |
| Editor Tab | `.segmented-tab` | 标签切换 |

**重要**: `.send-with-mode` 父元素的 `cursor: auto`，不可点击。必须点击子元素 `.anysphere-icon-button` (cursor: pointer)。

### 操作流程

1. 确保在 **Editor tab**（不是 Agents）
2. 如果 Composer 不可见，用 **Cmd+I** 唤出
3. 输入文字使用 `document.execCommand('insertText')`
4. **等待 1-1.5 秒**让上箭头按钮出现
5. 点击 `.send-with-mode > .anysphere-icon-button` 子元素
6. 检测 `[class*="loading" i]` 判断是否开始工作

---

## 🧪 测试工具

### 基础测试

```bash
# 完整流程测试
python3 test_complete_flow.py

# 最终点击验证
python3 test_final_click.py

# 自定义选择器测试
python3 test_custom_selector.py ".your-selector"
```

### 分析工具

```bash
# 自动分析按钮结构
python3 auto_analyze_button.py

# 实时 DOM 监控
python3 dom_monitor.py
```

---

## 🔧 两种模式

### 模式 1: 本地开发模式

**特点**: 
- 无需中央服务器
- 直接连接到 Cursor (端口 9876)
- 适合开发和调试

**使用**:
```python
from composer_operations import ComposerOperator

async def test():
    operator = ComposerOperator()
    await operator.connect()
    
    result = await operator.execute_prompt(
        "你的提示词",
        wait_for_completion=True
    )
    print(result)
```

### 模式 2: 中央服务器模式

**特点**:
- 支持多个 Cursor 实例
- 支持远程控制
- 消息路由和广播

**使用**:
```bash
# 1. 启动中央服务器
cd bridge
python3 websocket_server.py

# 2. 设置环境变量
export ORTENSIA_SERVER=ws://localhost:8765

# 3. 重启 Cursor
```

详细协议见 [docs/WEBSOCKET_PROTOCOL.md](docs/WEBSOCKET_PROTOCOL.md)

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICK_START_V9.md](QUICK_START_V9.md) | 5分钟快速开始 |
| [V9_COMPLETION_REPORT.md](V9_COMPLETION_REPORT.md) | 完成报告 |
| [docs/V9_IMPLEMENTATION_SUMMARY.md](docs/V9_IMPLEMENTATION_SUMMARY.md) | 实施总结 |
| [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) | 当前状态 |
| [docs/WEBSOCKET_PROTOCOL.md](docs/WEBSOCKET_PROTOCOL.md) | 协议规范 |
| [TODO.md](TODO.md) | 待办事项 |

---

## ⚠️ 注意事项

1. **安全性**: 注入会修改 Cursor 应用，仅用于开发测试
2. **签名**: 安装后需要重新签名应用
3. **备份**: 系统会自动备份原始 `main.js`
4. **恢复**: 如需恢复，使用备份文件：
   ```bash
   cp /Applications/Cursor.app/Contents/Resources/app/out/main.js.ortensia.backup \
      /Applications/Cursor.app/Contents/Resources/app/out/main.js
   ```

---

## 🔧 故障排查

### Cursor 无法启动

重新签名：
```bash
codesign --force --deep --sign - /Applications/Cursor.app
```

### WebSocket 连接失败

检查日志：
```bash
cat /tmp/cursor_ortensia.log
```

### 按钮点击无效

1. 确保使用正确选择器：`.send-with-mode > .anysphere-icon-button`
2. 输入后等待 1-1.5 秒
3. 确保在 Editor tab

更多问题见 [QUICK_START_V9.md](QUICK_START_V9.md) 的故障排查部分。

---

## 🎯 测试结果

**V9 本地模式测试**: ✅ 成功

- ✅ 自动切换到 Editor tab
- ✅ 自动检测 Composer 就绪
- ✅ 成功输入文字
- ✅ 成功点击子元素提交
- ✅ Agent 成功启动
- ✅ 检测到 6 个 loading 指示器

---

## 📊 版本历史

### V9 (2025-11-04) - Current ✅

- ✅ 修复提交按钮选择器（使用子元素）
- ✅ 增加等待时间（1.5 秒）
- ✅ 完善错误处理
- ✅ 详细的调试日志
- **核心功能验证通过**

### V8 (2025-11-04)

- 添加中央 Server 连接
- 实现消息路由
- 支持多客户端

### V7 及更早

- 基础注入实现
- DOM 访问探索
- 协议设计

---

## 🚧 下一步计划

见 [TODO.md](TODO.md)

- [ ] 测试中央 Server 模式
- [ ] 端到端系统验证
- [ ] 性能优化
- [ ] 更多语义操作

---

## 📝 许可

MIT License

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

*最后更新: 2025-11-04*  
*版本: V9*  
*状态: ✅ 核心功能完成*
