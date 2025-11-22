# 🌸 AITuber Kit 与 Ortensia 中央服务器集成指南

## 📋 概述

AITuber Kit 现在可以作为客户端连接到 Ortensia 中央服务器，使用标准的 Ortensia 协议进行通信。

## 🏗️ 架构

```
┌─────────────────────┐
│  Command Client     │ 发送命令
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Central Server     │ 消息路由
│  (8765端口)         │
└──────────┬──────────┘
           │
           ├───────────────┐
           │               │
           ↓               ↓
┌─────────────────────┐ ┌─────────────────────┐
│  Cursor Hook        │ │  AITuber Kit        │
└─────────────────────┘ └─────────────────────┘
```

## 🔧 配置步骤

### 1. 启动中央服务器

```bash
cd bridge
python3 websocket_server.py
```

### 2. 启动 AITuber Kit

```bash
cd aituber-kit
npm run dev
```

### 3. 启用外部联动模式

在 AITuber Kit 设置中:

```
Settings → External Linkage → ON
```

### 4. 验证连接

打开浏览器控制台，应该看到:

```
✅ [Ortensia] WebSocket 已连接
📤 [Ortensia] 发送注册消息: aituber-xxxxx
✅ [Ortensia] 注册成功
```

## 📡 Ortensia 协议

### 客户端类型

```typescript
AITUBER_CLIENT = 'aituber_client'
```

### 消息类型

| 消息类型 | 方向 | 说明 |
|---------|------|------|
| `register` | AITuber → Server | 注册客户端 |
| `register_ack` | Server → AITuber | 注册确认 |
| `heartbeat` | AITuber ↔ Server | 心跳 (30秒间隔) |
| `aituber_receive_text` | Server → AITuber | 接收文本消息 |
| `aituber_speak` | AITuber → Server | 发送语音/文本 |
| `aituber_emotion` | AITuber → Server | 情绪变化 |
| `aituber_status` | AITuber → Server | 状态更新 |

### 消息格式

```typescript
interface OrtensiaMessage {
  type: MessageType
  from: string      // 发送者 ID
  to: string        // 接收者 ID (或 "broadcast")
  timestamp: number // Unix 时间戳 (毫秒)
  payload: any      // 消息内容
}
```

### 示例：接收文本消息

```json
{
  "type": "aituber_receive_text",
  "from": "command-client-123",
  "to": "aituber-abc123",
  "timestamp": 1700000000000,
  "payload": {
    "text": "你好！",
    "role": "user",
    "emotion": "happy",
    "type": "text"
  }
}
```

## 🧪 测试

### 方法1：使用测试脚本

```bash
cd tests
python3 test_aituber_integration.py
```

### 方法2：手动测试

1. 确保中央服务器和 AITuber Kit 都在运行
2. 在 AITuber Kit 中启用外部联动模式
3. 使用 Command Client 发送消息:

```bash
cd cursor-injector
python3 test_central_server.py
```

## 🔍 调试

### 查看 AITuber 日志

打开浏览器控制台 (F12)，查看以 `[Ortensia]` 开头的日志。

### 查看中央服务器日志

中央服务器会显示:
- ✅ 客户端注册: `[aituber-xxxxx] 注册成功: aituber_client`
- 📨 消息路由: `[aituber-xxxxx] aituber_receive_text`

### 常见问题

1. **连接失败 (ERR_CONNECTION_REFUSED)**
   - 确保中央服务器在 8765 端口运行
   - 检查防火墙设置

2. **注册失败**
   - 检查控制台错误日志
   - 确认中央服务器版本支持 AITUBER_CLIENT

3. **收不到消息**
   - 确认外部联动模式已启用
   - 检查消息的 `to` 字段是否正确

## 📚 相关文件

### AITuber Kit
- `src/utils/OrtensiaClient.ts` - Ortensia 协议客户端
- `src/components/useExternalLinkage.tsx` - 外部联动 Hook

### 中央服务器
- `bridge/protocol.py` - 协议定义
- `bridge/websocket_server.py` - 服务器实现

### 测试
- `tests/test_aituber_integration.py` - 集成测试脚本

## 🚀 下一步

1. 实现更多 AITuber 消息类型
2. 添加双向通信（AITuber 主动发送消息）
3. 集成 TTS 功能
4. 添加情绪和表情控制

