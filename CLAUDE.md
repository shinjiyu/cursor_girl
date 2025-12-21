# AI 协作规则

> 本项目使用 Vibe Coding 方式与 AI 协作开发
> 
> **处理任何任务前，请先阅读 `docs/AI_INDEX.md`**

---

## 📜 协议优先原则

**协议是系统的灵魂**。在理解或修改任何功能前，必须先阅读相关协议：

| 协议 | 位置 | 说明 |
|-----|------|------|
| Ortensia 协议 | `bridge/protocol.py` | 消息类型、Payload、MessageBuilder |
| WebSocket 协议 | `docs/protocols/WEBSOCKET_PROTOCOL.md` | 通信规范 |
| 协议索引 | `docs/protocols/README.md` | 所有协议文档 |

---

## 🗺️ 代码地图

### 前端 (aituber-kit)

| 职责 | 文件 |
|-----|------|
| WebSocket 客户端 | `src/utils/OrtensiaClient.ts` |
| 消息管理 | `src/utils/OrtensiaManager.ts` |
| 消息处理入口 | `src/pages/assistant.tsx` |

### 后端 (bridge)

| 职责 | 文件 |
|-----|------|
| WebSocket 服务器 | `websocket_server.py` |
| 协议定义 | `protocol.py` |
| TTS 生成 | `tts_manager.py` |

### Cursor 注入

| 职责 | 文件 |
|-----|------|
| 安装脚本 | `cursor-injector/install-v10.sh` |
| Agent Hooks | `cursor-hooks/` |

---

## ⚠️ 已知陷阱

| 陷阱 | 表现 | 解决方案 |
|-----|------|---------|
| logging 配置顺序 | DEBUG 不显示 | `basicConfig()` 必须在任何 `logging.xxx()` 之前 |
| 消息类型未处理 | `未知消息类型` | 在 `handle_new_protocol_message()` 添加处理 |
| React 双重执行 | 日志出现两次 | 使用单例 + 幂等设计 |
| Inject 不处理消息 | 消息无响应 | Inject 只处理 EXECUTE_JS，其他由服务器生成 JS |

---

## 📂 文档结构

```
docs/
├── AI_INDEX.md          # 🤖 AI 入口（必读）
├── protocols/           # 📜 协议文档
├── _FEATURES/           # 📦 功能实现
├── _DECISIONS/          # 🎯 架构决策
└── archive/             # 📁 归档文档
```

---

## 📝 开发规范

### 添加新消息类型

1. `bridge/protocol.py` - 添加 MessageType
2. `bridge/protocol.py` - 创建 Payload dataclass
3. `bridge/protocol.py` - MessageBuilder 添加方法
4. `bridge/websocket_server.py` - handle_new_protocol_message 添加处理
5. **更新 `docs/AI_INDEX.md`**

### 添加新功能

1. 创建 `docs/_FEATURES/功能名.md`
2. 更新 `docs/AI_INDEX.md` 的功能索引
3. 如有重大决策，创建 `docs/_DECISIONS/ADR-XXX.md`

---

## 🔗 快速链接

- [AI 索引](docs/AI_INDEX.md) - AI 协作入口
- [协议定义](bridge/protocol.py) - 消息类型定义
- [服务器实现](bridge/websocket_server.py) - 消息处理逻辑

