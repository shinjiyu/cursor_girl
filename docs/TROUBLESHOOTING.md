# 故障排查指南

## AITuber 没有收到消息

### 症状
- Hook 成功发送消息到中央服务器
- 中央服务器日志显示消息已接收
- 但 AITuber 客户端没有收到消息

### 检查步骤

#### 1. 检查 AITuber 客户端是否已连接

**在浏览器控制台（AITuber 页面）检查：**
```javascript
// 打开浏览器控制台，检查连接状态
const client = window.OrtensiaClient?.getInstance?.()
console.log('连接状态:', client?.isConnected?.())
```

**应该看到：**
- `✅ [Ortensia] WebSocket 已连接`
- `✅ [Ortensia] 注册成功`

#### 2. 检查中央服务器日志

**查看中央服务器日志，应该看到：**
```
📨 [AITuber] Hook 消息，conversation_id: xxx
🔍 [诊断] 当前已注册客户端总数: X
🔍 [诊断] 已注册客户端列表:
    - aituber-xxxxx: 角色=['aituber_client', 'command_client']
📤 [AITuber] 消息已转发: hook-xxx → aituber-xxxxx
```

**如果没有看到转发日志，可能原因：**
- AITuber 客户端未连接
- AITuber 客户端未正确注册为 `aituber_client` 类型
- 中央服务器没有找到 AITuber 客户端

#### 3. 检查 AITuber 客户端注册

**在浏览器控制台检查：**
```javascript
// 检查客户端 ID 和注册状态
console.log('客户端 ID:', client?.clientId)
```

**应该看到注册消息：**
```
📤 [Ortensia] 发送注册消息 (多角色): aituber-xxxxx ['aituber_client', 'command_client']
✅ [Ortensia] 注册成功: {success: true, ...}
```

#### 4. 检查消息订阅

**在浏览器控制台检查：**
```javascript
// 检查消息处理器
console.log('消息处理器:', client?.messageHandlers)
```

**应该看到：**
- `AITUBER_RECEIVE_TEXT` 处理器已注册

### 常见问题

#### Q1: AITuber 客户端未连接

**症状：**
- 浏览器控制台没有 `✅ [Ortensia] WebSocket 已连接` 日志
- `client.isConnected()` 返回 `false`

**解决方案：**
1. 检查 `NEXT_PUBLIC_ORTENSIA_SERVER` 环境变量
2. 检查中央服务器是否运行
3. 检查网络连接（Cloudflare Tunnel 是否正常）

#### Q2: AITuber 客户端已连接但未注册

**症状：**
- WebSocket 已连接
- 但没有看到 `✅ [Ortensia] 注册成功` 日志

**解决方案：**
1. 检查浏览器控制台是否有错误
2. 检查 WebSocket 消息是否正常接收
3. 检查 `sendRegister()` 是否被调用

#### Q3: 中央服务器找不到 AITuber 客户端

**症状：**
- 中央服务器日志显示：`⚠️  目标客户端不存在: aituber`
- 诊断日志显示没有 `aituber_client` 类型的客户端

**解决方案：**
1. 确认 AITuber 客户端已连接并注册
2. 检查注册时的 `client_types` 是否包含 `aituber_client`
3. 检查中央服务器的 `get_by_type('aituber_client')` 逻辑

#### Q4: 消息已转发但 AITuber 未收到

**症状：**
- 中央服务器日志显示：`📤 [AITuber] 消息已转发`
- 但 AITuber 浏览器控制台没有收到消息

**解决方案：**
1. 检查 AITuber 的消息订阅是否正确
2. 检查 `OrtensiaManager` 的消息分发是否正常
3. 检查 `handleAituberReceiveText` 是否被调用

### 调试命令

#### 在浏览器控制台（AITuber 页面）

```javascript
// 1. 检查连接状态
const client = window.OrtensiaClient?.getInstance?.()
console.log('连接状态:', client?.isConnected?.())

// 2. 手动连接（如果需要）
if (!client?.isConnected()) {
  client?.connect('wss://mazda-commissioners-organised-perceived.trycloudflare.com/')
}

// 3. 检查注册状态
console.log('客户端 ID:', client?.clientId)

// 4. 检查消息处理器
console.log('消息处理器:', Array.from(client?.messageHandlers?.keys() || []))

// 5. 手动订阅消息（用于调试）
client?.on('aituber_receive_text', (msg) => {
  console.log('📬 [手动订阅] 收到消息:', msg)
})
```

#### 在中央服务器

查看日志输出，特别是：
- `📨 [收包]` - 收到的消息
- `📤 [发包]` - 发送的消息
- `🔍 [诊断]` - 诊断信息
- `⚠️` - 警告信息

### 日志级别

确保中央服务器日志级别设置为 `INFO` 或 `DEBUG`：
```python
logging.basicConfig(
    level=logging.INFO,  # 或 DEBUG
    ...
)
```

### 相关文件

- `aituber-kit/src/pages/assistant.tsx` - AITuber 主页面
- `aituber-kit/src/utils/OrtensiaClient.ts` - WebSocket 客户端
- `aituber-kit/src/components/useExternalLinkage.tsx` - 连接逻辑
- `bridge/websocket_server.py` - 中央服务器
- `bridge/websocket_server.py:handle_aituber_receive_text` - 消息转发逻辑
