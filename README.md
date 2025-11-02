# オルテンシア - AI 编程助手 🎀

一个基于 AITuber Kit 的虚拟编程助手，能够实时响应编码事件并通过语音和表情与你互动。

![オルテンシア](https://img.shields.io/badge/Status-Working-success)
![TTS](https://img.shields.io/badge/TTS-macOS-blue)
![WebSocket](https://img.shields.io/badge/WebSocket-Active-green)

## ✨ 特性

- 🎣 **Cursor Hooks 集成** - 自动感知文件保存、Git 提交等编码事件
- 🎤 **实时语音合成** - 使用 macOS TTS 生成自然流畅的中文语音
- 🎭 **表情动画系统** - 根据情绪显示不同表情和动作
- 🔌 **WebSocket 通信** - 实时接收编码事件并响应
- 📊 **事件映射** - 自动将编码事件映射到情绪和对话
- 🎨 **オルテンシア 主题** - 优雅的紫白配色
- 🌐 **浏览器支持** - 可在 Chrome/Electron 中运行

## 🚀 快速开始

### 前置要求

- macOS (用于 `say` 命令)
- [ffmpeg](https://ffmpeg.org/) - 音频格式转换
- Python 3.8+
- Node.js 18+

### 安装

1. **安装 ffmpeg**
```bash
brew install ffmpeg
```

2. **安装 Python 依赖**
```bash
cd bridge
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **安装 Node 依赖**
```bash
cd aituber-kit
npm install
```

### 运行

#### 方法 1: 一键启动（推荐）

```bash
./START_ALL.sh
```

这将自动启动：
- WebSocket 服务器 (端口 8000)
- Next.js 开发服务器 (端口 3000)
- Electron 桌面应用

#### 方法 2: 分别启动

**终端 1 - WebSocket 服务器:**
```bash
cd bridge
source venv/bin/activate
python websocket_server.py
```

**终端 2 - AITuber Kit:**
```bash
cd aituber-kit
npm run dev
```

**终端 3 - Electron (可选):**
```bash
cd aituber-kit
npm run assistant:dev
```

### 访问

- 🌐 **Web 界面**: http://localhost:3000/assistant
- 🖥️ **Electron 应用**: 自动弹出窗口

### 停止服务

```bash
./STOP_ALL.sh
```

## 📁 项目结构

```
cursorgirl/
├── aituber-kit/          # Next.js + Electron 前端
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── features/     # 核心功能
│   │   ├── pages/        # 页面和 API 路由
│   │   └── config/       # オルテンシア 主题配置
│   └── public/
│       └── vrm/          # VRM 3D 模型
│
├── bridge/               # Python 后端
│   ├── websocket_server.py    # WebSocket 服务器
│   ├── websocket_client.py    # 客户端示例
│   ├── emotion_mapper.py      # 事件→情绪映射
│   ├── tts_manager.py         # TTS 管理器
│   ├── tts/                   # TTS 实现
│   │   ├── base.py           # TTS 基类
│   │   ├── macos_tts.py      # macOS TTS
│   │   └── placeholder_tts.py # 占位符
│   ├── tts_config.json        # TTS 配置
│   └── config/
│       └── emotion_rules.yaml # 情绪映射规则
│
├── README.md             # 本文件
├── TTS_SUCCESS.md        # TTS 集成成功报告
├── WEBSOCKET_ARCHITECTURE.md  # WebSocket 架构文档
├── START_ALL.sh          # 一键启动脚本
└── STOP_ALL.sh           # 停止脚本
```

## 🎤 TTS 配置

编辑 `bridge/tts_config.json` 来配置 TTS:

```json
{
  "engine": "macos",
  "macos": {
    "voice": "Meijia",    // 音色: Meijia, Sinji, Tingting, Flo, Sandy
    "rate": 220,          // 语速: 150-300
    "output_dir": "tts_output"
  }
}
```

### 推荐音色（少女音）

- **Meijia** (美佳) - 年轻女声，自然流畅 ⭐ 推荐
- **Sinji** (欣基) - 轻快少女音 ⭐ 推荐
- **Tingting** (婷婷) - 标准女声
- **Flo** - 清脆女声
- **Sandy** - 温柔女声

查看所有可用音色:
```bash
say -v '?'
```

## 🔌 WebSocket API

### 消息格式

发送给 オルテンシア:

```json
{
  "text": "你好！我是オルテンシア！",
  "role": "assistant",
  "emotion": "happy",
  "type": "assistant"
}
```

服务器会自动添加 `audio_file` 字段:

```json
{
  "text": "你好！我是オルテンシア！",
  "role": "assistant",
  "emotion": "happy",
  "type": "assistant",
  "audio_file": "tts_output/xxxxx.wav"
}
```

### 支持的情绪

- `neutral` - 中性
- `happy` - 开心
- `sad` - 难过
- `angry` - 生气
- `relaxed` - 放松
- `surprised` - 惊讶
- `excited` - 兴奋

## 🎣 Cursor Hooks (自动编码事件)

オルテンシア已经集成了 Cursor Hooks，可以自动响应你的编码操作！

### 工作原理

```
保存文件 (Cmd+S) → post-save hook → WebSocket → オルテンシア: "保存成功~" 😊
Git commit       → post-commit hook → WebSocket → オルテンシア: "太棒了！代码提交成功~" 🎉
```

### 在本项目中使用

Hooks 已经在本项目中启用！当你：
- 保存文件 - オルテンシア 会说 "保存成功~"
- Git commit - オルテンシア 会说 "太棒了！代码提交成功~"

### 在其他项目中使用

```bash
# 1. 复制 .cursor 目录到你的项目
cp -r /path/to/cursorgirl/.cursor /path/to/your/project/

# 2. 确保 hooks 可执行
chmod +x /path/to/your/project/.cursor/hooks/*

# 3. 确保オルテンシア服务运行中
cd /path/to/cursorgirl && ./START_ALL.sh

# 4. 在 Cursor 中打开你的项目并编码
# オルテンシア 会自动响应 ✨
```

### 支持的 Hooks

**文件操作** (1个):
- ✅ **post-save** - 文件保存后触发

**Git 操作** (3个):
- ✅ **pre-commit** - Git 提交前触发（验证、格式化）
- ✅ **post-commit** - Git 提交后触发
- ✅ **post-push** - Git 推送后触发

**构建** (2个):
- ✅ **on-build** - 构建开始时触发
- ✅ **post-build** - 构建完成后触发（成功/失败）

**测试** (2个):
- ✅ **on-test** - 测试开始时触发
- ✅ **post-test** - 测试完成后触发（通过/失败）

**错误处理** (1个):
- ✅ **on-error** - 错误发生时触发（语法/运行时/构建/测试错误）

**总计**: ✅ 10 个 Hooks 已实现

### 查看 Hook 日志

```bash
# 实时查看
tail -f /tmp/cursor-hooks.log

# 查看最近记录
tail -20 /tmp/cursor-hooks.log
```

### 自定义配置

编辑 `.cursor/hooks/config.sh`:

```bash
# WebSocket 服务器地址
WS_SERVER="ws://localhost:8000/ws"

# 是否启用调试模式
DEBUG=true

# 是否启用 WebSocket 发送
ENABLE_WEBSOCKET=true
```

### 详细文档

- [Cursor Hooks README](./cursor-hooks/README.md) - 完整说明
- [快速开始指南](./cursor-hooks/QUICKSTART.md) - 5分钟上手
- [安装指南](./cursor-hooks/INSTALL.md) - 详细安装步骤

---

## 📝 测试

### 发送测试消息

```bash
cd bridge
python websocket_client.py
```

或使用 Python 代码:

```python
import asyncio
from websocket_client import WebSocketClient

async def test():
    client = WebSocketClient()
    await client.connect()
    await client.send_emotion('你好！我是オルテンシア！', 'happy')
    await asyncio.sleep(5)
    await client.close()

asyncio.run(test())
```

## 🛠️ 故障排查

### WebSocket 连接失败

1. 检查服务器是否运行: `lsof -ti :8000`
2. 查看服务器日志: `tail -f /tmp/websocket_server.log`
3. 重启服务: `./STOP_ALL.sh && ./START_ALL.sh`

### 音频无法播放

1. 确认 ffmpeg 已安装: `which ffmpeg`
2. 检查音频文件: `ls bridge/tts_output/`
3. 查看浏览器控制台错误

### TTS 生成失败

1. 测试 say 命令: `say -v Meijia "测试" -o /tmp/test.aiff`
2. 测试 ffmpeg: `ffmpeg -i /tmp/test.aiff /tmp/test.wav`
3. 检查 TTS 配置: `cat bridge/tts_config.json`

## 📚 文档

- [TTS 成功报告](./TTS_SUCCESS.md) - 完整的 TTS 集成过程和结果
- [WebSocket 架构](./WEBSOCKET_ARCHITECTURE.md) - WebSocket 通信架构详解
- [AITuber Kit 文档](./aituber-kit/README.md) - 原始项目文档

## 🎯 技术栈

### 前端
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Three.js (VRM 渲染)
- Electron (桌面应用)

### 后端
- Python 3.13
- websockets
- PyYAML
- ffmpeg (音频转换)

### TTS
- macOS System TTS (`say` 命令)
- ffmpeg (AIFF → WAV 转换)

## 🌟 特别感谢

- [AITuber Kit](https://github.com/tegnike/aituber-kit) - 原始项目
- [pixiv/three-vrm](https://github.com/pixiv/three-vrm) - VRM 模型渲染
- オルテンシア 模型创作者

## 📄 许可证

本项目基于 AITuber Kit 开发，遵循其原始许可证。

## 💬 联系

如有问题或建议，请创建 Issue。

---

**状态**: ✅ 正常工作  
**最后更新**: 2025-11-01  
**版本**: 1.0.0

🎉 **オルテンシア 现在可以说话了！**
