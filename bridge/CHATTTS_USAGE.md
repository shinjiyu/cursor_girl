# ChatTTS 使用指南

## 概述

ChatTTS 是一个高质量的中文语音合成引擎，已成功集成到项目的 TTS 管理器中。

## 特性

- ✅ 高质量中文语音合成
- ✅ 情感控制（开心、悲伤、兴奋、平静等）
- ✅ 支持多种音色（通过种子控制）
- ✅ 使用 Apple Silicon MPS 加速
- ✅ 本地运行，无需网络连接

## 配置

配置文件位置：`bridge/tts_config.json`

ChatTTS 配置项：

```json
{
  "engine": "chattts",
  "chattts": {
    "model_path": "/Users/user/Documents/tts/chattts/models/ChatTTS",
    "device": "auto",
    "temperature": 0.3,
    "seed": 42,
    "output_dir": "tts_output"
  }
}
```

### 配置说明

- `model_path`: 本地模型路径
- `device`: 设备类型（auto 自动检测，支持 mps/cuda/cpu）
- `temperature`: 温度参数，控制语音变化程度（0.0-1.0，默认 0.3）
- `seed`: 默认音色种子（相同种子产生相同音色）
- `output_dir`: 音频文件输出目录

## 基础使用

### 1. 使用 TTS 管理器

```python
from tts_manager import TTSManager

# 创建管理器
manager = TTSManager(config_path="tts_config.json")

# 初始化 ChatTTS 引擎
manager.initialize("chattts")

# 生成语音
audio_file = manager.generate("你好，我是オルテンシア！")
print(f"生成的音频文件: {audio_file}")
```

### 2. 情感生成

```python
# 支持的情感类型
emotions = [
    "neutral",   # 中性
    "happy",     # 开心
    "excited",   # 兴奋
    "sad",       # 悲伤
    "calm",      # 平静
    "angry",     # 生气
    "surprised", # 惊讶
    "relaxed"    # 放松
]

# 生成带情感的语音
audio_file = manager.generate_with_emotion(
    "太棒了！今天真是个好日子！",
    emotion="happy"
)
```

### 3. 切换音色

```python
# 通过种子切换音色
manager.tts.set_speaker(123)  # 使用种子 123
audio_file = manager.generate("这是新的音色")

# 随机音色
manager.tts.set_speaker(None)  # None 表示随机
```

### 4. 直接使用 ChatTTS 类

```python
from tts import ChatTTS

# 创建实例
config = {
    "temperature": 0.3,
    "seed": 42,
    "output_dir": "tts_output"
}
tts = ChatTTS(config)

# 生成语音
audio_file = tts.generate("你好世界")

# 带情感生成
audio_file = tts.generate_with_emotion("哈哈，太好笑了！", emotion="happy")
```

## 情感标签

ChatTTS 支持在文本中嵌入情感标签：

- `[laugh]` - 笑声
- `[break]` - 停顿
- `[uv_break]` - 呼吸/短停顿
- `[oral_0-9]` - 口语化程度（0 最少，9 最多）
- `[speed_0-9]` - 语速（0 最慢，9 最快）

示例：

```python
text = "哈哈[laugh]，这个笑话太好笑了[uv_break]！"
audio_file = tts.generate(text)
```

## 运行测试

### 方法 1: 使用测试脚本

```bash
cd bridge
./run_chattts_test.sh
```

### 方法 2: 手动激活虚拟环境

```bash
source /Users/user/Documents/tts/chattts/venv/bin/activate
cd bridge
python test_chattts_integration.py
```

## 性能

在 Apple Silicon (M2) 上的测试结果：

- **模型加载时间**: ~4-5 秒（首次）/ ~1 秒（后续）
- **合成速度**: RTF ~1.2-1.9（实时率）
- **音频质量**: 24kHz 采样率
- **设备**: MPS（Metal Performance Shaders）

RTF (Real-Time Factor)：
- RTF < 1.0：比实时更快
- RTF = 1.0：实时
- RTF > 1.0：比实时慢

## 与 macOS TTS 对比

| 特性 | macOS TTS | ChatTTS |
|------|-----------|---------|
| 音质 | 中等 | 高 |
| 情感控制 | 有限（通过语速） | 强大（多种标签） |
| 音色选择 | 系统预设 | 无限（种子控制） |
| 离线使用 | ✅ | ✅ |
| 速度 | 快 | 中等 |
| 自然度 | 中等 | 高 |

## 切换引擎

可以在运行时切换 TTS 引擎：

```python
# 从 macOS TTS 切换到 ChatTTS
manager.initialize("macos")
manager.switch_engine("chattts")

# 从 ChatTTS 切换回 macOS TTS
manager.switch_engine("macos")
```

## 故障排除

### 1. 模型加载失败

```
❌ 错误: 模型文件不存在
解决: 检查 model_path 配置是否正确
```

### 2. 内存不足

```
建议: 关闭其他应用程序，释放内存
```

### 3. 生成速度慢

```
建议: 
- 降低 temperature 参数
- 检查是否使用了正确的设备（MPS/CUDA）
```

## 更多信息

- 本地 ChatTTS 路径: `/Users/user/Documents/tts/chattts`
- 模型路径: `/Users/user/Documents/tts/chattts/models/ChatTTS`
- 输出目录: `bridge/tts_output`
- 测试脚本: `bridge/test_chattts_integration.py`

## 未来改进

- [ ] 支持流式生成
- [ ] 添加更多预设音色
- [ ] 优化生成速度
- [ ] 支持长文本分段合成

























