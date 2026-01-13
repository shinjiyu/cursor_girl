# AITuber Kit 架构说明

## 三个核心组件的关系

### 1. **Next.js Server (本地服务器，localhost:3000)**

**职责：**
- 🎨 **提供 UI 页面**：React 组件渲染的网页界面（`/assistant` 等）
- 🔌 **提供 API 路由**：本地服务接口，处理客户端请求
- 📁 **文件服务**：访问本地文件系统（VRM、Live2D、图片等资源）

**启动方式：**
```bash
npm run dev          # 开发模式（热重载）
npm run build && npm start  # 生产模式（静态构建）
```

**主要 API 路由：**
- `/api/tts-google` - Google TTS 服务
- `/api/tts-voicevox` - VoiceVox TTS 服务
- `/api/save-chat-log` - 保存聊天日志
- `/api/get-vrm-list` - 获取 VRM 模型列表
- `/api/get-live2d-list` - 获取 Live2D 模型列表
- `/api/tts-audio/[filename]` - 提供音频文件访问
- ... 等 40+ 个 API 路由

**关键点：**
- 这是一个 **本地 Node.js 服务器**，运行在用户机器上
- 开发模式：`next dev`（端口 3000）
- 生产模式：`next build` + `next start`（也可以静态导出）

---

### 2. **Electron (桌面应用框架)**

**职责：**
- 🖥️ **创建桌面窗口**：将 Next.js 页面包装成原生桌面应用
- 🔗 **系统集成**：托盘图标、窗口管理、IPC 通信
- 📦 **应用打包**：将整个应用打包成 `.app` (macOS) 或 `.exe` (Windows)

**启动方式：**
```bash
npm run assistant:dev  # 开发模式（并行启动 Next.js + Electron）
npm run assistant      # 仅启动 Electron（需先启动 Next.js）
```

**工作流程：**
1. Electron 主进程启动
2. 等待 Next.js 服务器就绪（`wait-on http://localhost:3000`）
3. 创建 `BrowserWindow`，加载 `http://localhost:3000/assistant`
4. 页面在 Electron 的 Chromium 内核中渲染

**关键点：**
- Electron **不直接提供服务器功能**，它只是一个"浏览器外壳"
- 开发模式：加载 `http://localhost:3000`（需要 Next.js 运行）
- 生产模式：可以加载静态 HTML 文件（`next export`）或继续使用本地服务器

---

### 3. **中央 Server (Ortensia Central, WebSocket 服务器)**

**职责：**
- 🔄 **会话仲裁**：处理多终端输入，保证事件顺序
- 📡 **事件广播**：将 Cursor Agent 的消息转发给所有 AITuber 客户端
- 🌐 **分布式协调**：连接 Cursor IDE 和 AITuber 客户端

**部署位置：**
- 可以是本地：`ws://localhost:8765`
- 也可以是远程：`wss://xxx.trycloudflare.com/`（通过 Cloudflare Tunnel）

**通信协议：**
- WebSocket (WSS/WS)
- JSON 消息格式（定义在 `bridge/protocol.py`）

**关键点：**
- 这是一个 **独立的 Python WebSocket 服务器**
- 与 Next.js Server **完全分离**，运行在不同的端口
- AITuber 客户端通过 `OrtensiaClient.ts` 连接中央服务器

---

## 三者关系图

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron 桌面应用                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │     BrowserWindow (Chromium 内核)                     │ │
│  │  ┌────────────────────────────────────────────────┐  │ │
│  │  │  加载: http://localhost:3000/assistant         │  │ │
│  │  │  (Next.js 页面)                                │  │ │
│  │  │                                                 │  │ │
│  │  │  React 组件 (assistant.tsx)                    │  │ │
│  │  │    ↓                                            │  │ │
│  │  │  OrtensiaClient.ts                             │  │ │
│  │  │    ↓ WebSocket                                  │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP
┌─────────────────────────────────────────────────────────────┐
│          Next.js Server (localhost:3000)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • React 页面渲染 (/assistant)                       │  │
│  │  • API 路由 (/api/tts-google, /api/save-chat-log)  │  │
│  │  • 文件服务 (VRM, Live2D, 图片)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↓ WebSocket
┌─────────────────────────────────────────────────────────────┐
│    中央 Server (Ortensia Central, ws://...:8765)            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • 会话仲裁 (Session Manager)                       │  │
│  │  • 事件广播 (Event Broadcasting)                     │  │
│  │  • 消息路由 (Message Routing)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↕ WebSocket                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cursor IDE (通过 cursor-injector)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据流向示例

### 场景：用户通过 AITuber 发送消息到 Cursor

```
1. 用户在 Electron 窗口的输入框输入文本
   ↓
2. React 组件 (assistant.tsx) 调用 OrtensiaClient.sendCursorInputText()
   ↓
3. OrtensiaClient 通过 WebSocket 发送 INPUT_SUBMIT 消息
   ↓
4. 中央 Server 接收消息，加入会话队列，分配序号
   ↓
5. 中央 Server 将消息路由到 Cursor Injector
   ↓
6. Cursor Injector 执行 DOM 操作，输入文本到 Cursor IDE
   ↓
7. Cursor Agent 处理请求，生成响应
   ↓
8. Cursor Hooks (afterAgentResponse) 捕获响应
   ↓
9. Cursor Hooks 通过 WebSocket 发送到中央 Server
   ↓
10. 中央 Server 广播 SESSION_EVENT 给所有 AITuber 客户端
   ↓
11. AITuber 的 OrtensiaClient 收到消息
   ↓
12. React 组件更新 UI，显示 Agent 响应
   ↓
13. 如果需要 TTS，调用 Next.js API (/api/tts-google)
   ↓
14. Next.js API 调用 Google TTS 服务，返回音频
   ↓
15. React 组件播放音频，驱动 AITuber 角色
```

---

## 关键设计决策

### 为什么需要 Next.js Server？

1. **API 路由**：TTS、文件访问等需要 Node.js 后端能力
2. **开发体验**：React 热重载、TypeScript 支持
3. **生产部署**：可以静态导出，也可以继续运行服务器

### ⚠️ 重要：Electron 与中央服务器没有直接交互

**架构关系：**
```
Electron (桌面外壳)
  └─> BrowserWindow (浏览器窗口)
       └─> 加载 Next.js 页面 (http://localhost:3000/assistant)
            └─> React 组件 (assistant.tsx)
                 └─> OrtensiaClient.ts (WebSocket 客户端)
                      └─> 中央服务器 (ws://...:8765)
```

**关键点：**
- ❌ **Electron 主进程**不直接连接中央服务器
- ❌ **Electron 渲染进程**（BrowserWindow）也不直接连接
- ✅ **React 组件**（在 BrowserWindow 中运行的网页内容）通过 `OrtensiaClient` 连接中央服务器
- Electron 只是一个"浏览器外壳"，它加载网页，网页内容负责所有业务逻辑

**为什么这样设计？**
- Electron 的 `BrowserWindow` 本质上是一个 Chromium 浏览器
- 加载的网页（Next.js 页面）在浏览器环境中运行
- WebSocket 连接在浏览器环境（React 组件）中建立，而不是在 Electron 主进程中
- 这样可以利用浏览器的 WebSocket API，代码更简单，也便于调试

### 为什么中央 Server 是独立的？

- **分布式架构**：可以部署在远程服务器
- **多客户端支持**：一个中央服务器可以服务多个 Cursor + 多个 AITuber
- **解耦**：中央服务器只负责消息路由，不处理 TTS、文件等本地服务

---

## 打包发布时的考虑

### 选项 1：保留 Next.js Server（推荐）

**优点：**
- 无需修改代码
- API 路由继续可用
- 可以动态加载资源

**实现：**
- 打包时：`next build && next start`（生产模式）
- Electron 加载：`http://localhost:3000`（或配置的端口）

**缺点：**
- 需要运行一个本地 Node.js 进程
- 占用额外内存

### 选项 2：完全移除 Next.js Server

**优点：**
- 更轻量，无需本地服务器
- 启动更快

**缺点：**
- **需要大量代码修改**：
  - 将所有 API 路由迁移到 Electron Main 进程（IPC）
  - 或使用外部服务替代本地 API
  - 静态资源需要打包到 Electron 中

**实现难度：** ⚠️ **高**（需要重构）

---

## 总结

| 组件 | 位置 | 端口 | 职责 | 是否必需 | 与中央服务器关系 |
|------|------|------|------|---------|----------------|
| **Next.js Server** | 本地 | 3000 | UI + API 路由 | ✅ 必需 | ❌ 无直接交互 |
| **Electron** | 本地 | - | 桌面窗口外壳 | ✅ 必需 | ❌ **无直接交互** |
| **React 组件** | Electron 窗口内 | - | 业务逻辑 + UI | ✅ 必需 | ✅ **通过 OrtensiaClient 连接** |
| **中央 Server** | 远程/本地 | 8765 | WebSocket 消息路由 | ✅ 必需 | - |

**关键理解：**
- Next.js Server = **本地服务**（UI + API）
- Electron = **桌面外壳**（加载 Next.js 页面，**不直接连接中央服务器**）
- React 组件（在 Electron 窗口中）= **实际业务逻辑**（通过 `OrtensiaClient` 连接中央服务器）
- 中央 Server = **分布式协调**（WebSocket 消息路由）

**通信路径：**
```
用户操作 → Electron窗口 → Next.js页面(React) → OrtensiaClient → 中央服务器
```

**重要澄清：**
- ❌ Electron 主进程/渲染进程**不直接**与中央服务器交互
- ✅ 只有**网页内容**（React 组件）通过 WebSocket 连接中央服务器
- Electron 只是提供了一个"浏览器窗口"来显示网页内容
