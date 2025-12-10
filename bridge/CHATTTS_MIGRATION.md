# ChatTTS 迁移指南

## 概述

本指南帮助你从旧的 TTS 实现（macOS TTS）迁移到新的 ChatTTS 实现。

## 已完成的工作

✅ **集成完成**

1. 创建了 `chattts_tts.py` - ChatTTS 适配器
2. 更新了 `__init__.py` - 导入新的 ChatTTS 实现
3. 更新了 `tts_config.json` - 添加 ChatTTS 配置
4. 创建了测试脚本 - `test_chattts_integration.py`
5. 创建了运行脚本 - `run_chattts_test.sh`

✅ **测试通过**

- 基础生成测试 ✅
- 情绪生成测试 ✅
- 音色切换测试 ✅
- 引擎切换测试 ✅

## 快速切换

### 方法 1: 修改配置文件（推荐）

编辑 `bridge/tts_config.json`：

```json
{
  "engine": "chattts"    // 改为 "chattts"
}
```

重启服务器即可。

### 方法 2: 运行时切换

```python
from tts_manager import TTSManager

manager = TTSManager()
manager.initialize("chattts")  # 使用 ChatTTS
```

## 迁移步骤

### 1. 确认本地环境

确保 ChatTTS 已安装：

```bash
ls -la /Users/user/Documents/tts/chattts/models/ChatTTS
```

应该看到以下文件：
- `Decoder.pt` / `Decoder.safetensors`
- `DVAE.pt` / `DVAE.safetensors`
- `GPT.pt`
- `Vocos.pt` / `Vocos.safetensors`
- 等等

### 2. 运行测试

```bash
cd bridge
./run_chattts_test.sh
```

如果测试通过，说明环境正常。

### 3. 更新配置

修改 `tts_config.json`：

```diff
{
-  "engine": "macos",
+  "engine": "chattts",
  
  "chattts": {
    "model_path": "/Users/user/Documents/tts/chattts/models/ChatTTS",
    "device": "auto",
    "temperature": 0.3,
    "seed": 42,
    "output_dir": "tts_output"
  }
}
```

### 4. 重启服务

如果 WebSocket 服务器正在运行，重启它：

```bash
# 停止旧服务
pkill -f websocket_server.py

# 启动新服务（使用 ChatTTS 虚拟环境）
source /Users/user/Documents/tts/chattts/venv/bin/activate
cd bridge
python websocket_server.py
```

### 5. 验证

发送一个测试消息：

```bash
python cursor_event.py celebration
```

应该听到 ChatTTS 生成的语音。

## API 变化

### 无需修改代码

新的 ChatTTS 实现完全兼容现有的 `TTSBase` 接口，所有现有代码无需修改。

### 新增功能

如果想使用 ChatTTS 的特殊功能：

```python
# 切换音色
manager.tts.set_speaker(123)

# 使用情感标签
text = "哈哈[laugh]，太好笑了[uv_break]！"
audio = manager.generate(text)
```

## 性能对比

| 指标 | macOS TTS | ChatTTS |
|------|-----------|---------|
| 首次加载 | < 0.1s | ~4-5s |
| 后续加载 | < 0.1s | ~1s |
| 合成速度 | ~0.5s/句 | ~2-3s/句 |
| 音质 | 中等 | 高 |
| 自然度 | 中等 | 高 |
| 情感表达 | 有限 | 强大 |

## 注意事项

### 1. 虚拟环境

ChatTTS 需要使用其专用的虚拟环境：

```bash
source /Users/user/Documents/tts/chattts/venv/bin/activate
```

**重要**: 确保在启动 WebSocket 服务器前激活该虚拟环境。

### 2. 依赖冲突

如果遇到依赖冲突，确保：
- 使用 ChatTTS 的虚拟环境
- 不要混用不同的虚拟环境

### 3. 内存使用

ChatTTS 需要更多内存：
- macOS TTS: ~50MB
- ChatTTS: ~500MB-1GB

如果内存不足，可以考虑：
- 降低 `temperature` 参数
- 使用 CPU 而不是 MPS

### 4. 初次运行慢

ChatTTS 首次加载模型需要 4-5 秒，这是正常的。后续加载会快很多（~1 秒）。

## 回滚方案

如果遇到问题，可以随时切换回 macOS TTS：

```json
{
  "engine": "macos"
}
```

然后重启服务器。

## 故障排除

### 问题 1: 找不到 ChatTTS 模块

```
ModuleNotFoundError: No module named 'ChatTTS'
```

**解决**: 确保使用 ChatTTS 的虚拟环境：

```bash
source /Users/user/Documents/tts/chattts/venv/bin/activate
```

### 问题 2: 模型加载失败

```
❌ ChatTTS 初始化失败: 模型文件不存在
```

**解决**: 检查 `model_path` 配置：

```bash
ls -la /Users/user/Documents/tts/chattts/models/ChatTTS
```

### 问题 3: 内存不足

```
RuntimeError: MPS backend out of memory
```

**解决**: 修改配置使用 CPU：

```json
{
  "chattts": {
    "device": "cpu"
  }
}
```

### 问题 4: 生成速度慢

**优化建议**:
- 降低 `temperature`（如 0.2）
- 确保使用 `device: "mps"`（Apple Silicon）
- 关闭其他占用 GPU 的应用

## 更多帮助

- 使用文档: [CHATTTS_USAGE.md](CHATTTS_USAGE.md)
- 测试脚本: `test_chattts_integration.py`
- 本地模型: `/Users/user/Documents/tts/chattts`

## 完成清单

- [ ] 确认 ChatTTS 环境正常
- [ ] 运行测试脚本验证
- [ ] 更新 `tts_config.json`
- [ ] 重启 WebSocket 服务器（使用正确的虚拟环境）
- [ ] 测试实际语音生成
- [ ] 验证情感控制功能

完成后，享受高质量的 ChatTTS 语音合成！🎉









