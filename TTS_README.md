# TTS 集成说明

## 📌 概述

项目现已集成 **ChatTTS** 高质量中文语音合成引擎。

## ⚡ 快速开始

### 1. 测试 ChatTTS

```bash
cd bridge
./quick_test_chattts.sh
```

如果看到 "🎉 ChatTTS 工作正常！" 说明一切就绪。

### 2. 切换到 ChatTTS

编辑 `bridge/tts_config.json`:

```json
{
  "engine": "chattts"
}
```

### 3. 启动服务器

```bash
source /Users/user/Documents/tts/chattts/venv/bin/activate
cd bridge
python websocket_server.py
```

## 📚 详细文档

- **[CHATTTS_INTEGRATION_SUMMARY.md](CHATTTS_INTEGRATION_SUMMARY.md)** - 完整集成总结
- **[bridge/CHATTTS_USAGE.md](bridge/CHATTTS_USAGE.md)** - 使用指南
- **[bridge/CHATTTS_MIGRATION.md](bridge/CHATTTS_MIGRATION.md)** - 迁移指南

## 🎯 功能特性

✅ 高质量中文语音合成  
✅ 8 种情感控制（开心、悲伤、兴奋等）  
✅ 无限音色（种子控制）  
✅ Apple Silicon MPS 加速  
✅ 本地运行，无需网络  
✅ 完全兼容现有代码  

## 🧪 测试脚本

```bash
# 快速测试（30秒）
cd bridge
./quick_test_chattts.sh

# 完整测试（2分钟）
cd bridge
./run_chattts_test.sh
```

## 🔄 引擎对比

| 特性 | macOS TTS | ChatTTS |
|------|-----------|---------|
| 音质 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 情感 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 自然度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 使用示例

```python
from tts_manager import TTSManager

manager = TTSManager()
manager.initialize("chattts")

# 基础生成
audio = manager.generate("你好世界")

# 带情感
audio = manager.generate_with_emotion(
    "太棒了！",
    emotion="happy"
)

# 切换音色
manager.tts.set_speaker(123)
```

## 📊 性能

- **加载**: ~4-5秒（首次）/ ~1秒（后续）
- **合成**: RTF ~1.2-1.9
- **设备**: MPS (Apple Silicon)
- **质量**: 24kHz

## ⚙️ 配置位置

- 配置文件: `bridge/tts_config.json`
- 模型路径: `/Users/user/Documents/tts/chattts/models/ChatTTS`
- 虚拟环境: `/Users/user/Documents/tts/chattts/venv`

## 🆘 故障排除

### 问题: 找不到 ChatTTS 模块

```bash
source /Users/user/Documents/tts/chattts/venv/bin/activate
```

### 问题: 模型加载失败

检查配置文件中的 `model_path` 是否正确。

### 问题: 内存不足

修改配置使用 CPU:
```json
{
  "chattts": {
    "device": "cpu"
  }
}
```

更多问题见 [bridge/CHATTTS_USAGE.md](bridge/CHATTTS_USAGE.md)

## ✅ 集成状态

- **实现**: ✅ 完成
- **测试**: ✅ 全部通过
- **文档**: ✅ 完善
- **状态**: ✅ 生产就绪

---

**开始使用 ChatTTS，享受高质量的中文语音合成！** 🎉























