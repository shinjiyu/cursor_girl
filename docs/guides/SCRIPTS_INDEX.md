# 📝 脚本和工具索引

快速查找所有脚本和工具的位置和用途。

---

## 🚀 快速启动脚本

### scripts/START_ALL.sh
**用途**: 一键启动所有服务（中央服务器 + Cursor）  
**使用**:
```bash
./scripts/START_ALL.sh
```

### scripts/STOP_ALL.sh
**用途**: 停止所有服务  
**使用**:
```bash
./scripts/STOP_ALL.sh
```

### scripts/start_cursor_with_server.sh
**用途**: 启动中央服务器并等待 Cursor 连接  
**使用**:
```bash
./scripts/start_cursor_with_server.sh
```

---

## 🔧 安装和配置

### cursor-injector/install-v9.sh ⭐
**用途**: 安装 V9 Cursor Hook（最新版本）  
**使用**:
```bash
cd cursor-injector
./install-v9.sh
```
**说明**: 
- 注入 WebSocket 客户端到 Cursor
- 支持本地模式和中央服务器模式
- 自动备份原文件

### cursor-injector/uninstall.sh
**用途**: 卸载 Cursor Hook，恢复原始文件  
**使用**:
```bash
cd cursor-injector
./uninstall.sh
```

### scripts/setup_central_mode.sh
**用途**: 配置中央服务器模式  
**使用**:
```bash
./scripts/setup_central_mode.sh
```
**说明**: 设置环境变量并重新注入

---

## 🧪 测试脚本

### tests/quick_test_central.py ⭐
**用途**: 快速测试中央服务器模式  
**使用**:
```bash
cd tests
python3 quick_test_central.py
```
**说明**: 
- 自动发现 Cursor Hook ID
- 发送测试命令
- 验证完整流程

### cursor-injector/test_complete_flow.py
**用途**: 测试本地模式（直接连接 Cursor Hook）  
**使用**:
```bash
cd cursor-injector
python3 test_complete_flow.py
```
**说明**: 
- 连接本地 WebSocket 服务器（端口 9876）
- 测试所有 Composer 操作
- 不需要中央服务器

### cursor-injector/test_central_server.py
**用途**: 交互式中央服务器测试  
**使用**:
```bash
cd cursor-injector
python3 test_central_server.py
```
**说明**: 
- 需要手动输入 Cursor Hook ID
- 支持自定义命令
- 适合调试

---

## 🛠️ 开发工具

### cursor-injector/dom_monitor.py
**用途**: 实时监控 Cursor UI 的 DOM 结构  
**使用**:
```bash
cd cursor-injector
python3 dom_monitor.py
```
**说明**: 
- 定期抓取 DOM 快照
- 帮助分析 UI 变化
- 开发 DOM 操作时使用

### cursor-injector/auto_analyze_button.py
**用途**: 自动分析按钮元素的详细信息  
**使用**:
```bash
cd cursor-injector
python3 auto_analyze_button.py
```
**说明**: 
- 查找特定选择器的元素
- 显示元素属性和样式
- 帮助定位可点击元素

### cursor-injector/inspect-input.py
**用途**: 检查 Composer 输入框的状态  
**使用**:
```bash
cd cursor-injector
python3 inspect-input.py
```
**说明**: 
- 查看输入框内容
- 检查输入框属性
- 调试输入问题

### cursor-injector/test_custom_selector.py
**用途**: 测试自定义 CSS 选择器  
**使用**:
```bash
cd cursor-injector
python3 test_custom_selector.py
```
**说明**: 
- 验证选择器是否正确
- 测试元素查找

---

## 🌐 服务器和客户端

### bridge/websocket_server.py ⭐
**用途**: 中央 WebSocket 服务器  
**使用**:
```bash
cd bridge
python3 websocket_server.py
```
**说明**: 
- 监听端口 8765
- 管理所有客户端连接
- 路由消息
- 保持心跳

### bridge/websocket_client.py
**用途**: WebSocket 客户端示例（用于测试）  
**使用**:
```bash
cd bridge
python3 websocket_client.py
```

### bridge/test_server.py
**用途**: 测试服务器基础功能  
**使用**:
```bash
cd bridge
python3 test_server.py
```

---

## 📚 示例代码

### examples/command_client_example.py
**用途**: 基础 Command Client 示例  
**使用**:
```bash
cd examples
python3 command_client_example.py
```
**说明**: 
- 展示如何连接服务器
- 展示如何注册客户端
- 展示如何发送命令

### examples/semantic_command_client.py
**用途**: 语义操作客户端示例  
**使用**:
```bash
cd examples
python3 semantic_command_client.py
```
**说明**: 
- 使用高级语义操作
- 完整的执行流程
- 包含错误处理

---

## 🔍 辅助工具

### scripts/wait_for_cursor.sh
**用途**: 等待 Cursor Hook 成功连接到中央服务器  
**使用**:
```bash
./scripts/wait_for_cursor.sh
```
**说明**: 
- 监控日志文件
- 等待连接成功消息
- 超时保护

### bridge/cursor_dom_inspector.py
**用途**: 检查 Cursor DOM 结构（使用 Playwright）  
**使用**:
```bash
cd bridge
python3 cursor_dom_inspector.py
```
**说明**: 
- 需要 Playwright
- 用于深度分析 DOM

---

## 📦 Python 模块

### bridge/protocol.py
**说明**: Ortensia Protocol v1 实现  
**导入**:
```python
from bridge.protocol import Message, MessageType, MessageBuilder
```

### cursor-injector/composer_operations.py
**说明**: Composer DOM 操作封装  
**导入**:
```python
from cursor_injector.composer_operations import ComposerOperations
```

### cursor-injector/ortensia_cursor_client.py
**说明**: Cursor 客户端基类  
**导入**:
```python
from cursor_injector.ortensia_cursor_client import OrtensiaClient
```

---

## 🗂️ 分类总结

### 必备脚本 ⭐
1. `cursor-injector/install-v9.sh` - 安装 Hook
2. `bridge/websocket_server.py` - 启动服务器
3. `tests/quick_test_central.py` - 快速测试

### 开发工具
1. `cursor-injector/dom_monitor.py` - 监控 DOM
2. `cursor-injector/auto_analyze_button.py` - 分析按钮
3. `cursor-injector/inspect-input.py` - 检查输入框

### 测试脚本
1. `tests/quick_test_central.py` - 中央模式测试
2. `cursor-injector/test_complete_flow.py` - 本地模式测试
3. `cursor-injector/test_central_server.py` - 交互式测试

### 示例代码
1. `examples/command_client_example.py` - 基础示例
2. `examples/semantic_command_client.py` - 高级示例

---

## 🎯 常用工作流

### 首次使用
```bash
# 1. 安装 Hook
cd cursor-injector && ./install-v9.sh

# 2. 启动服务器
cd ../bridge && python3 websocket_server.py &

# 3. 启动 Cursor
# （手动启动或等待自动启动）

# 4. 测试
cd ../tests && python3 quick_test_central.py
```

### 日常开发
```bash
# 监控 DOM 变化
cd cursor-injector
python3 dom_monitor.py

# 测试新功能
python3 test_complete_flow.py
```

### 调试问题
```bash
# 查看 Cursor Hook 日志
tail -f /tmp/cursor_ortensia.log

# 查看服务器日志
tail -f /tmp/ws_server.log

# 重新注入（如果出问题）
cd cursor-injector
./uninstall.sh
./install-v9.sh
```

---

## 📝 脚本依赖

### Python 依赖
```bash
# 服务器和客户端
pip install websockets

# TTS（可选）
pip install pyttsx3

# Playwright（可选，用于深度分析）
pip install playwright
playwright install
```

### 系统要求
- Python 3.13+
- macOS（主要测试平台）
- Cursor IDE
- Node.js 18+（如需修改注入代码）

---

## 🔄 脚本更新历史

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| V9 | 2025-11-04 | 完整的中央服务器支持 |
| V8 | 2025-11-03 | DOM 操作优化 |
| V7 | 2025-11-02 | 初始协议实现 |

---

**脚本索引最后更新**: 2025-11-04 22:35:00


