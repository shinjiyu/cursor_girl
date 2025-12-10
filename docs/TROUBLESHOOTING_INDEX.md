# 故障排查索引

> 常见问题和解决方案快速查找

## 🔍 快速诊断

### 症状 → 文档

| 症状 | 可能原因 | 文档链接 |
|------|---------|---------|
| 消息被处理 4 次 | 重复订阅 | [Ortensia Manager 方案](../ORTENSIA_MANAGER_SOLUTION.md) |
| 自动检查不触发 | ID 不匹配 / 开关关闭 | [自动检查最终修复](../AUTO_CHECK_FINAL_FIX.md) |
| 对话无法发现 | 时序问题 / WebSocket 未连接 | [AITuber 发现修复](../AITUBER_DISCOVERY_FIX.md) |
| VRM 加载错误 | 动画时序问题 | [架构指南 - 故障排查](./AITUBER_ARCHITECTURE_GUIDE.md#问题-3vrm-加载错误) |
| TTS 无声音 | 配置错误 / 模型未加载 | [ChatTTS 集成总结](../CHATTTS_INTEGRATION_SUMMARY.md) |
| 语音性别不一致 | Seed 未固定 | [萝莉音优化](../LOLI_VOICE_OPTIMIZATION_SUMMARY.md) |

---

## 📚 按类别分类

### AITuber 前端问题

#### 1. 消息处理

**问题**: 消息被处理多次
- **文档**: [Ortensia Manager 方案](../ORTENSIA_MANAGER_SOLUTION.md)
- **关键点**: 
  - 检查 `isSubscribed` 标记
  - 确认只有 1 个订阅者
  - 查看消息去重机制
- **诊断命令**:
  ```javascript
  // 浏览器控制台
  📢 [订阅] 实例 xxx: 现在有 X 个订阅者
  // 应该只有 1 个
  ```

**问题**: 消息未收到
- **文档**: [AITuber 架构指南](./AITUBER_ARCHITECTURE_GUIDE.md#消息流转)
- **检查项**:
  1. WebSocket 连接状态
  2. 消息类型是否注册了处理器
  3. 消息去重是否误判
- **诊断命令**:
  ```javascript
  // 检查 WebSocket 状态
  ✅ [Ortensia] WebSocket 已连接
  
  // 检查处理器
  ➕ [OrtensiaManager] 注册处理器: message_type
  ```

#### 2. 对话发现

**问题**: 初始化时无法获取对话
- **文档**: [AITuber 发现修复](../AITUBER_DISCOVERY_FIX.md)
- **原因**: React Strict Mode 双重挂载导致时序问题
- **解决方案**: 
  - 实现重试机制（2s, 4s, 6s）
  - 确保 WebSocket 连接后再发送请求
- **日志关键词**:
  ```
  🔍 [Ortensia] 正在发现已存在的 Cursor 对话 (尝试 X/3)
  📤 [Ortensia] 已发送 GET_CONVERSATION_ID 请求
  🔍 [Discovery] 发现对话完成
  ```

**问题**: 对话发现成功但没有 UI 显示
- **检查项**:
  1. `conversationStore` 中是否有数据
  2. `MultiConversationChat` 组件是否渲染
  3. 浏览器控制台是否有 React 错误

#### 3. VRM 和动画

**问题**: `Error: You have to load VRM first`
- **文档**: [架构指南 - 故障排查](./AITUBER_ARCHITECTURE_GUIDE.md#问题-3vrm-加载错误)
- **原因**: 动画在 VRM 加载前就尝试加载
- **解决方案**:
  ```typescript
  // viewer.ts
  if (vrma && this.model.vrm) {
    this.model.loadAnimation(vrma)
  }
  
  // model.ts
  if (vrm == null || mixer == null) {
    console.warn('VRM not loaded yet')
    return  // 不抛出错误
  }
  ```

**问题**: 动画不播放
- **检查项**:
  1. 动画文件是否存在（`/idle_loop.vrma`）
  2. `AnimationController` 是否初始化
  3. 查看控制台日志：`🎬 [AnimationController]`

#### 4. 自动任务检查

**问题**: Agent 完成后没有自动继续
- **文档**: [自动检查最终修复](../AUTO_CHECK_FINAL_FIX.md)
- **诊断流程**:
  
  ```typescript
  // 1. 检查是否收到事件
  📨 [OrtensiaManager] 收到消息: agent_completed
  
  // 2. 检查 ID 匹配
  ✅ [Auto Check] 找到匹配: e595bde3 → e595bde3-ae8a-...
  
  // 3. 检查开关状态
  🔍 [Store] getAutoCheckEnabled(xxx): true
  
  // 4. 检查防抖
  🎯 [Auto Check] 是否可以触发: true
  
  // 5. 发送提示
  📤 [Auto Check] 发送检查提示 "继续"
  ```

**问题**: Conversation ID 不匹配
- **原因**: Hook 和 Inject 返回的 ID 不同
- **解决方案**: 使用短 ID（前 8 字符）匹配
- **代码**:
  ```typescript
  const shortConvId = convId.substring(0, 8)
  const matchedConv = allConvs.find(([id]) => id.startsWith(shortConvId))
  ```

---

### 后端服务问题

#### 1. WebSocket 服务器

**问题**: WebSocket 连接失败
- **检查项**:
  1. 服务器是否运行：`ps aux | grep websocket_server`
  2. 端口是否被占用：`lsof -i :8765`
  3. 防火墙设置
- **启动命令**:
  ```bash
  cd bridge
  source /Users/user/Documents/tts/chattts/venv/bin/activate
  python websocket_server.py
  ```

**问题**: 消息路由错误
- **检查项**:
  1. 客户端是否正确注册
  2. `to` 字段是否正确
  3. 服务器日志：`[路由]` 关键词

#### 2. TTS 生成

**问题**: TTS 不生成音频
- **文档**: [ChatTTS 集成总结](../CHATTTS_INTEGRATION_SUMMARY.md)
- **检查项**:
  1. `tts_config.json` 配置
  2. ChatTTS 模型是否加载
  3. 虚拟环境是否正确
- **测试命令**:
  ```bash
  cd bridge
  python test_chattts_integration.py
  ```

**问题**: 语音性别/音色不一致
- **文档**: [萝莉音优化](../LOLI_VOICE_OPTIMIZATION_SUMMARY.md)
- **原因**: Seed 未固定
- **解决方案**:
  ```json
  // tts_config.json
  {
    "chattts": {
      "seed": 1234,  // 固定种子
      "temperature": 0.3
    }
  }
  ```

**问题**: 音频文件路径错误
- **检查项**:
  1. `tts_output/` 目录是否存在
  2. 文件权限
  3. 音频文件是否真的生成了

#### 3. Agent Hooks

**问题**: Hook 不触发
- **检查项**:
  1. Hook 脚本是否可执行
  2. 环境变量是否正确
  3. Python 版本（需要 3.9+）
- **测试命令**:
  ```bash
  cd cursor-hooks
  python test_stop_hook.py
  ```

**问题**: `asyncio.timeout` 错误
- **原因**: Python 3.9 不支持
- **解决方案**: 使用 `try-except` 处理超时
  ```python
  try:
      async with websockets.connect(...) as ws:
          # 逻辑
  except asyncio.TimeoutError:
      logger.error("超时")
  ```

---

## 🛠️ 调试工具

### 浏览器控制台

**关键日志前缀**:
- `🎛️  [OrtensiaManager]` - 管理器操作
- `📨 [OrtensiaManager]` - 消息分发
- `✅ [Ortensia]` - WebSocket 操作
- `🎯 [Auto Check]` - 自动检查逻辑
- `🔍 [Discovery]` - 对话发现
- `🎬 [AnimationController]` - 动画控制

**有用的命令**:
```javascript
// 查看当前对话
conversationStore.getState().conversations

// 查看自动检查状态
Array.from(conversationStore.getState().conversations.values())
  .map(c => ({ id: c.id.substring(0, 8), autoCheck: c.autoCheckEnabled }))

// 手动触发对话发现
OrtensiaClient.getInstance().discoverExistingConversations()
```

### 服务器日志

**关键日志前缀**:
- `[注册]` - 客户端注册
- `[路由]` - 消息路由
- `[TTS]` - TTS 生成
- `[广播]` - 消息广播

**查看日志**:
```bash
# 实时查看
tail -f bridge/logs/websocket_server.log

# 过滤特定客户端
grep "aituber-xxx" bridge/logs/websocket_server.log
```

### 网络调试

**Chrome DevTools**:
1. Network → WS 标签
2. 查看 WebSocket 帧
3. 检查发送/接收的消息

**WebSocket 测试工具**:
```python
# test_agent_completed.py
python3 test_agent_completed.py
```

---

## 📋 常见检查清单

### AITuber 无法启动

- [ ] Next.js 服务是否运行 (`npm run dev`)
- [ ] 端口 3000 是否被占用
- [ ] `node_modules` 是否安装
- [ ] 浏览器控制台是否有错误

### 消息未正常流转

- [ ] WebSocket 连接状态（应该是 `OPEN`）
- [ ] 服务器是否运行
- [ ] 客户端是否注册成功
- [ ] 消息类型是否有对应处理器
- [ ] 消息去重是否误判

### 自动检查不工作

- [ ] `autoCheckEnabled` 是否为 `true`
- [ ] Conversation ID 是否匹配
- [ ] 距离上次检查是否超过 5 秒
- [ ] `AGENT_COMPLETED` 事件是否收到
- [ ] Hook 是否正确触发

### TTS 不工作

- [ ] `tts_config.json` 配置正确
- [ ] ChatTTS 模型已下载
- [ ] 虚拟环境已激活
- [ ] `tts_output/` 目录存在
- [ ] 音频文件是否生成

---

## 🚨 紧急问题处理

### 系统完全无响应

1. **重启所有服务**:
   ```bash
   cd /Users/user/Documents/cursorgirl
   ./scripts/STOP_ALL.sh
   ./scripts/START_ALL.sh
   ```

2. **检查端口占用**:
   ```bash
   lsof -i :3000  # Next.js
   lsof -i :8765  # WebSocket 服务器
   ```

3. **清理缓存**:
   ```bash
   cd aituber-kit
   rm -rf .next
   npm run dev
   ```

### WebSocket 连接频繁断开

1. **检查心跳**:
   - 浏览器控制台应该每 30 秒看到心跳日志
   - 服务器日志应该有心跳响应

2. **增加超时时间**:
   ```typescript
   // OrtensiaClient.ts
   private heartbeatInterval = 60000  // 改为 60 秒
   ```

3. **检查网络**:
   - 是否有代理
   - 防火墙设置
   - 网络稳定性

### React 双重挂载问题

**现象**: 所有日志都出现两次

**原因**: React Strict Mode（开发模式）

**处理**: 
- 开发模式下正常，不需要修复
- 确保代码支持双重挂载（幂等性）
- 生产环境不会出现

---

## 📚 相关文档链接

- [AITuber 架构详解](./AITUBER_ARCHITECTURE_GUIDE.md) - 完整架构说明
- [项目文档索引](./PROJECT_DOCUMENTATION_INDEX.md) - 所有文档导航
- [WebSocket 协议](../archive/WEBSOCKET_PROTOCOL_IMPLEMENTATION.md) - 协议定义
- [快速开始](../QUICK_START.md) - 项目启动

---

**维护者**: AI Assistant  
**最后更新**: 2025-12-08  
**版本**: 1.0.0







