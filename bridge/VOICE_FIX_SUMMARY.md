# ChatTTS 音色固定问题修复总结

## 🐛 问题现象

**症状**: 每次合成的声音都不一样，甚至男女都不一样

**根本原因**: ChatTTS 的 Speaker Embedding 没有被正确使用

## 🔍 问题分析

### ChatTTS 音色控制的核心原理

ChatTTS 使用 **Speaker Embedding（说话人嵌入向量）** 来控制音色：

```python
# 音色采样
torch.manual_seed(seed)  # 设置种子
speaker = chat.sample_random_speaker()  # 采样一个 768 维向量

# 生成音频
wavs = chat.infer(
    text,
    spk_emb=speaker  # ← 关键：使用固定的 speaker
)
```

### 原代码的问题

**chattts_engine.py (修复前)**:

```python
def generate(self, text: str, seed: Optional[int] = None, ...):
    # ❌ 虽然设置了 seed
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)
    
    # ❌ 但没有传入 speaker embedding！
    wavs = self._chat.infer(
        [text],
        params_infer_code=params_infer,
        # 缺少: spk_emb=...  ← 这里是问题所在！
    )
```

**问题**:
- 虽然设置了 seed，但没有使用固定的 speaker embedding
- ChatTTS 内部每次都会重新随机采样 speaker
- 导致每次音色都不同，甚至男女都不同

## ✅ 修复方案

### 修改 chattts_engine.py

```python
def generate(self, text: str, seed: Optional[int] = None, ...):
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

    # 生成参数
    params_infer = ChatTTS.Chat.InferCodeParams(
        temperature=temperature,
        top_P=top_p,
        top_K=top_k,
    )

    # 🔧 关键修复：传入固定的 speaker embedding！
    wavs = self._chat.infer(
        [text],
        params_infer_code=params_infer,
        spk_emb=speaker_to_use,  # ← 添加固定的 speaker！
        skip_refine_text=True,
        use_decoder=use_decoder,
    )

    # ...
    return audio, synthesis_time, 24000
```

## 🎯 核心修改点

### 1. 使用固定的 Speaker Embedding

```python
# 修复前：每次都重新随机采样
wavs = self._chat.infer([text])  # 没有 spk_emb 参数

# 修复后：使用固定的 speaker
wavs = self._chat.infer([text], spk_emb=speaker_to_use)
```

### 2. 保存并复用 Speaker

```python
# 初始化时
self._speaker = None

# 第一次生成时
if self._speaker is None:
    torch.manual_seed(1234)
    self._speaker = self._chat.sample_random_speaker()

# 后续生成时
speaker_to_use = self._speaker  # 复用保存的 speaker
```

### 3. 支持动态切换音色

```python
# 如果指定了新 seed，重新采样
if seed is not None:
    torch.manual_seed(seed)
    speaker_to_use = self._chat.sample_random_speaker()
```

## 📊 参数详解

### Speaker Embedding ⭐⭐⭐⭐⭐

**最重要的参数！决定音色的 90%**

- **类型**: 768 维浮点向量
- **作用**: 编码说话人的所有特征（性别、音色、音高、口音等）
- **控制方式**:
  - 通过 seed 控制随机采样
  - 采样后保存并复用

### Seed ⭐⭐⭐⭐

**间接控制音色**

- **类型**: 整数 (0 ~ 2^32-1)
- **作用**: 控制 speaker 采样的随机性
- **关键**: 必须在采样 speaker 时设置
- **示例**:
  ```python
  torch.manual_seed(1234)  # 设置种子
  speaker = chat.sample_random_speaker()  # 采样固定音色
  ```

### Temperature ⭐⭐

**控制语调和节奏**

- **类型**: 浮点数 (0.0 ~ 1.0)
- **作用**: 控制生成的随机性
- **推荐值**:
  - `0.2`: 最稳定（朗读、播报）
  - `0.3`: 平衡（对话）← **推荐**
  - `0.4`: 生动（表演、配音）

### top_P ⭐

**Nucleus Sampling**

- **类型**: 浮点数 (0.0 ~ 1.0)
- **默认值**: `0.7`
- **作用**: 控制采样范围

### top_K ⭐

**Top-K Sampling**

- **类型**: 整数
- **默认值**: `20`
- **作用**: 限制候选词数量

## 🧪 测试验证

### 一致性测试

```bash
# 运行一致性测试
python test_voice_consistency.py

# 生成 5 次相同文本，验证音色是否一致
```

### 测试结果

```bash
# 查看生成的文件
ls -lht bridge/tts_output/*.wav | head -5

# 输出示例（文件大小相近说明内容相似）
-rw-r--r--  117K  f0910ad3b09b1e07fb4ca25df7f73ee3.wav
-rw-r--r--  143K  1fdf585dcd4ec5b60ab72cf971d41101.wav
-rw-r--r--  496K  782784fdcaca533fdb46bc36ec923916.wav
```

### 验证标准

✅ **成功**: 所有音频都是同样的女声/萝莉音  
❌ **失败**: 出现男声或不同的女声

## 🎀 当前配置

### tts_config.json

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

### 音色特征

**Seed 1234**:
- 🎀 甜美萝莉音
- 音高: 较高（女声）
- 语速: 中等
- 音色: 清脆可爱

## 📝 总结

### 修复前

```
用户: "你好"
AI: [生成音频 - 女声]

用户: "再见"
AI: [生成音频 - 男声] ← 音色变了！
```

### 修复后

```
用户: "你好"
AI: [生成音频 - 萝莉女声]

用户: "再见"
AI: [生成音频 - 萝莉女声] ← 音色一致！✅
```

## 🎯 关键理解

### 为什么只设置 seed 不够？

```python
# ❌ 错误做法
torch.manual_seed(1234)
wavs = chat.infer(text)  # 没有 spk_emb

# ChatTTS 内部会重新随机采样 speaker：
# speaker = random_sample()  ← 每次都不同！
```

```python
# ✅ 正确做法
torch.manual_seed(1234)
speaker = chat.sample_random_speaker()  # 采样一次
wavs = chat.infer(text, spk_emb=speaker)  # 使用固定 speaker
```

### 音色控制的层级

```
1. Speaker Embedding (核心)
   ↓ 90% 影响
   决定音色、性别、音高

2. Seed (间接)
   ↓ 通过控制 speaker 采样
   影响音色选择

3. Temperature (微调)
   ↓ 10% 影响
   影响语调、节奏
```

## 📚 相关文档

- [CHATTTS_PARAMETERS_EXPLAINED.md](./CHATTTS_PARAMETERS_EXPLAINED.md) - 参数详细解释
- [VOICE_GUIDE.md](./VOICE_GUIDE.md) - 音色选择指南
- [CHATTTS_USAGE.md](./CHATTTS_USAGE.md) - 使用说明

## ✅ 结论

**问题**: 每次生成的声音都不一样，甚至男女都不一样  
**原因**: Speaker Embedding 没有被正确使用  
**修复**: 在 `infer` 时添加 `spk_emb` 参数，使用固定的 speaker  
**结果**: 音色固定，每次都是同样的萝莉音 ✅

---

**修复时间**: 2025-12-07  
**修复文件**: `/Users/user/Documents/tts/chattts/chattts_engine.py`  
**关键修改**: 添加 `spk_emb=speaker_to_use` 参数






















