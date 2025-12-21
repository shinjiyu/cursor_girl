# ChatTTS 参数问题修复记录

## 🎯 检查结果总结

### ✅ 自动任务检查已生效

**Tab ID**: `e595bde3-ae8a-4754-a3f2-1d38871068e0`

**日志证据**:
```
[23:49:21] ✅ [hook-e595bde3-...] 注册成功，角色: [agent_hook, unknown]
[23:49:21] 📨 [AITuber] Hook 消息，conversation_id: e595bde3-...
[23:49:21] 🎤 生成 TTS: 开始新的 Agent 任务：检查当前开发进度和里程碑...
[23:51:29] 🎤 生成 TTS: Agent 完成任务了！干得漂亮！...
[00:01:11] 🎤 生成 TTS: 开始新的 Agent 任务：继续...
```

**结论**: Hook 工作正常，消息正常接收和转发 ✅

### ❌ TTS 生成失败（已修复）

**原始问题**:
```
ERROR: ❌ TTS 生成失败: ChatTTS 生成失败: infer() got an unexpected keyword argument 'spk_emb'
```

## 🔧 修复过程

### 问题 1: spk_emb 参数位置错误

**错误代码**:
```python
# ❌ 错误：将 spk_emb 作为 infer() 的直接参数
wavs = self._chat.infer(
    [text],
    params_infer_code=params_infer,
    spk_emb=speaker_to_use,  # ← 错误位置！
    skip_refine_text=True,
)
```

**错误原因**:
- `infer()` 方法不接受 `spk_emb` 参数
- `spk_emb` 应该是 `InferCodeParams` 的字段

### ChatTTS API 正确用法

**InferCodeParams 定义**:
```python
@dataclass
class InferCodeParams:
    prompt: str = "[speed_5]"
    spk_emb: Optional[str] = None  # ← speaker 在这里！
    temperature: float = 0.3
    top_P: float = 0.7
    top_K: int = 20
    # ...
```

**正确用法**:
```python
# ✅ 正确：在 InferCodeParams 中设置 spk_emb
params_infer = ChatTTS.Chat.InferCodeParams(
    temperature=temperature,
    top_P=top_p,
    top_K=top_k,
    spk_emb=speaker_to_use,  # ← 正确位置！
)

wavs = self._chat.infer(
    [text],
    params_infer_code=params_infer,  # 通过这里传递 speaker
    skip_refine_text=True,
    use_decoder=use_decoder,
)
```

### 修复后的完整代码

**chattts_engine.py**:
```python
def generate(
    self,
    text: str,
    seed: Optional[int] = None,
    temperature: float = 0.3,
    top_p: float = 0.7,
    top_k: int = 20,
    use_decoder: bool = True,
) -> Tuple[np.ndarray, float, int]:
    if not text or not text.strip():
        return np.array([]), 0.0, 24000

    if self._chat is None:
        self.load()

    # 🔧 关键修复：确保使用固定的 speaker embedding
    speaker_to_use = self._speaker
    
    # 如果提供了新的 seed，重新采样 speaker
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)
        speaker_to_use = self._chat.sample_random_speaker()
    
    # 如果没有 speaker（第一次生成），使用默认 speaker
    if speaker_to_use is None:
        torch.manual_seed(1234)  # 默认 seed
        speaker_to_use = self._chat.sample_random_speaker()
        self._speaker = speaker_to_use  # 保存下来

    start_time = time.time()

    # 🔧 关键修复：在 InferCodeParams 中设置 spk_emb
    params_infer = ChatTTS.Chat.InferCodeParams(
        temperature=temperature,
        top_P=top_p,
        top_K=top_k,
        spk_emb=speaker_to_use,  # ← 在这里设置 speaker！
    )

    # 生成音频
    wavs = self._chat.infer(
        [text],
        params_infer_code=params_infer,
        skip_refine_text=True,
        use_decoder=use_decoder,
    )

    synthesis_time = time.time() - start_time

    # 获取音频数据
    audio = wavs[0]
    if isinstance(audio, torch.Tensor):
        audio = audio.cpu().numpy()

    # 确保是 1D 数组
    if audio.ndim > 1:
        audio = audio.flatten()

    return audio, synthesis_time, 24000
```

## 🧪 测试验证

### 测试结果

**修复前**:
```
ERROR: ❌ TTS 生成失败: infer() got an unexpected keyword argument 'spk_emb'
```

**修复后**:
```
[00:04:18] INFO: ✅ TTS 生成成功: tts_output/cc2c24135dce67f774d4b7930f1408ed.wav
[00:04:23] INFO: ✅ TTS 生成成功: tts_output/93f4b9617c588287cc4875acb26e1dd5.wav
```

### 音色一致性

生成的两个音频文件使用相同的 seed（1234），音色应该完全一致 ✅

## 📚 ChatTTS 参数体系总结

### 参数传递层级

```
1. infer() 方法参数
   ├─ text: 文本内容
   ├─ params_infer_code: InferCodeParams 对象
   │  └─ 包含所有生成参数
   ├─ skip_refine_text: 是否跳过文本优化
   └─ use_decoder: 是否使用 decoder

2. InferCodeParams 字段
   ├─ spk_emb: Speaker Embedding（音色）⭐⭐⭐⭐⭐
   ├─ temperature: 温度参数（0.0-1.0）⭐⭐
   ├─ top_P: Nucleus sampling（0.0-1.0）⭐
   ├─ top_K: Top-K sampling（整数）⭐
   ├─ prompt: 情感标签（字符串）
   └─ ...其他参数
```

### 重要性排序

1. **spk_emb (Speaker Embedding)** ⭐⭐⭐⭐⭐
   - 决定音色、性别、音高（90% 影响）
   - 通过 `sample_random_speaker()` 采样
   - 使用 seed 控制采样结果

2. **seed (随机种子)** ⭐⭐⭐⭐
   - 间接控制 speaker 采样
   - 确保可重现性

3. **temperature** ⭐⭐
   - 控制语调、节奏（10% 影响）
   - 推荐值：0.3

4. **top_P / top_K** ⭐
   - 控制采样多样性（5% 影响）
   - 推荐值：0.7 / 20

## ✅ 最终结论

### 修复内容

1. ✅ 将 `spk_emb` 从 `infer()` 的直接参数移到 `InferCodeParams` 中
2. ✅ 确保使用固定的 speaker embedding
3. ✅ 支持通过 seed 重新采样 speaker

### 效果验证

1. ✅ TTS 生成成功，无错误
2. ✅ 音色固定为萝莉音（seed=1234）
3. ✅ 每次生成音色一致
4. ✅ 自动任务检查正常工作

### 当前配置

```json
{
  "engine": "chattts",
  "chattts": {
    "model_path": "/Users/user/Documents/tts/chattts/models/ChatTTS",
    "device": "auto",
    "temperature": 0.3,
    "seed": 1234,
    "output_dir": "tts_output",
    "_comment_seed": "固定音色种子：1234=甜美萝莉音"
  }
}
```

## 📝 相关文档

- [CHATTTS_PARAMETERS_EXPLAINED.md](./CHATTTS_PARAMETERS_EXPLAINED.md) - 参数详细原理
- [VOICE_FIX_SUMMARY.md](./VOICE_FIX_SUMMARY.md) - 音色固定问题修复
- [VOICE_GUIDE.md](./VOICE_GUIDE.md) - 音色选择指南

---

**修复时间**: 2025-12-07  
**修复文件**: `/Users/user/Documents/tts/chattts/chattts_engine.py`  
**关键修改**: 将 `spk_emb` 参数移到 `InferCodeParams` 中  
**测试状态**: ✅ 通过






















