# AITuber 动作扩展方案设计

## 📊 当前架构分析

### 现有组件
1. **EmoteController** (`aituber-kit/src/features/emoteController/emoteController.ts`)
   - 主控制器，协调表情和动画
   
2. **AnimationController** (`animationController.ts`)
   - 管理身体动画（.vrma 文件）
   - 当前只支持情绪动画（6 种）

3. **ExpressionController** (`expressionController.ts`)
   - 管理面部表情（BlendShapes）
   - 依赖模型的 BlendShape 支持

### 当前触发流程
```
Cursor Hook → Central Server → AITuber
  ↓
OrtensiaClient 接收 AITUBER_RECEIVE_TEXT
  ↓
{
  text: "...",
  emotion: "happy",  // ← 只支持 6 种情绪
  audio_file: "..."
}
  ↓
viewer.model.speak(talk) → playEmotion(emotion)
```

---

## 🎯 方案 1：扩展 Emotion 映射（推荐 ⭐）

### 优点
- ✅ **最简单** - 只需修改一个文件
- ✅ **无协议变更** - 使用现有的 `emotion` 字段
- ✅ **向后兼容** - 不影响现有功能
- ✅ **5 分钟实现**

### 实现步骤

#### 1. 扩展 AnimationController 的映射表

**文件：** `aituber-kit/src/features/emoteController/animationController.ts`

```typescript
private emotionAnimations: Record<string, string> = {
  // 原有情绪
  neutral: 'idle',
  happy: 'joy',
  sad: 'sad',
  angry: 'angry',
  relaxed: 'relax',
  surprised: 'surprise',
  
  // 🆕 新增动作
  wave: 'wave',           // 挥手
  bow: 'bow',             // 鞠躬
  nod: 'nod',             // 点头
  shake_head: 'shake',    // 摇头
  think: 'thinking',      // 思考
  celebrate: 'celebrate', // 庆祝
  dance: 'dance',         // 跳舞
  clap: 'clap',           // 鼓掌
}
```

#### 2. 准备动画文件（可选）

将 `.vrma` 动画文件放到：
```
aituber-kit/public/animations/
  - wave.vrma
  - bow.vrma
  - nod.vrma
  ...
```

如果动画文件不存在，系统会使用默认姿势（不会报错）。

#### 3. 从 Cursor 触发动作

**在 Cursor Hook 中：**
```python
# 发送动作命令
client.send_aituber_text(
    text="收到！我会马上处理",
    emotion="wave",  # ← 使用动作名称
    conversation_id=conv_id
)
```

**示例场景：**
```python
# Agent 开始工作
client.send_aituber_text("开始工作了！", emotion="celebrate")

# Agent 思考中
client.send_aituber_text("让我想想...", emotion="think")

# Agent 完成
client.send_aituber_text("完成了！", emotion="bow")
```

### 优势
- 动画文件是可选的（即使没有 .vrma 文件也能工作）
- 扩展性好（随时添加新动作）
- 实现成本低

---

## 🎯 方案 2：分离 Action 和 Emotion（更规范）

### 优点
- ✅ **语义清晰** - 动作和情绪分开
- ✅ **更灵活** - 可以同时设置情绪和动作
- ❌ **需要修改协议** - 增加 `action` 字段

### 实现步骤

#### 1. 扩展协议

**文件：** `bridge/protocol.py`

```python
@dataclass
class AituberReceiveTextPayload:
    text: str
    emotion: Optional[str] = None      # 情绪（表情）
    action: Optional[str] = None        # 🆕 动作
    audio_file: Optional[str] = None
    conversation_id: Optional[str] = None
```

#### 2. 扩展 AnimationController

```typescript
// 分离情绪和动作
private emotionAnimations: Record<string, string> = {
  neutral: 'idle',
  happy: 'joy',
  // ...
}

private actionAnimations: Record<string, string> = {
  wave: 'wave',
  bow: 'bow',
  nod: 'nod',
  // ...
}

// 新增方法
public playAction(action: string) {
  const animationName = this.actionAnimations[action]
  if (animationName) {
    const clip = this.animationCache.get(animationName)
    if (clip) {
      this.playAnimation(clip, { loop: false, priority: 'high' })
    }
  }
}
```

#### 3. 修改 EmoteController

```typescript
public playEmotion(preset: VRMExpressionPresetName) {
  this._expressionController.playEmotion(preset)
  this._animationController.playEmotion(preset)
}

// 🆕 新增方法
public playAction(action: string) {
  this._animationController.playAction(action)
}
```

#### 4. 修改 OrtensiaClient

```typescript
// 处理 action 字段
if (message.type === MessageType.AITUBER_RECEIVE_TEXT) {
  const { text, emotion, action, audio_file } = message.payload
  
  // 播放动作
  if (action) {
    viewer.model?.playAction(action)
  }
  
  // 说话（会播放情绪）
  viewer.model?.speak({ text, emotion, audio_file })
}
```

### 使用示例

```python
# 同时设置情绪和动作
client.send_aituber_text(
    text="太棒了！",
    emotion="happy",      # 表情开心
    action="celebrate",   # 动作庆祝
    conversation_id=conv_id
)
```

---

## 🎯 方案 3：预定义动作序列（高级）

### 适用场景
- 复杂的组合动作
- 需要精确控制时序

### 示例

```typescript
// 定义动作序列
const actionSequences = {
  greet: [
    { action: 'wave', duration: 1000 },
    { action: 'bow', duration: 1500 },
    { emotion: 'happy', duration: 2000 }
  ],
  agree: [
    { action: 'nod', duration: 500 },
    { action: 'nod', duration: 500 },
    { emotion: 'happy', duration: 1000 }
  ]
}

// 播放序列
public async playActionSequence(sequenceName: string) {
  const sequence = actionSequences[sequenceName]
  for (const step of sequence) {
    if (step.action) {
      this.playAction(step.action)
    }
    if (step.emotion) {
      this.playEmotion(step.emotion)
    }
    await wait(step.duration)
  }
}
```

---

## 📌 推荐方案对比

| 方案 | 实现难度 | 灵活性 | 协议变更 | 推荐度 |
|-----|---------|--------|---------|--------|
| 方案 1 | ⭐ 简单 | ⭐⭐⭐ 中 | ❌ 无 | ⭐⭐⭐⭐⭐ |
| 方案 2 | ⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ✅ 有 | ⭐⭐⭐⭐ |
| 方案 3 | ⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ 很高 | ✅ 有 | ⭐⭐⭐ |

---

## 🚀 快速开始（方案 1）

1. **修改 AnimationController**
   ```bash
   vi aituber-kit/src/features/emoteController/animationController.ts
   ```

2. **添加动作映射**
   ```typescript
   wave: 'wave',
   bow: 'bow',
   think: 'thinking',
   ```

3. **从 Cursor 测试**
   ```python
   client.send_aituber_text("你好！", emotion="wave")
   ```

4. **（可选）添加动画文件**
   - 下载或制作 `.vrma` 动画文件
   - 放到 `public/animations/` 目录

---

## 📦 资源

### 动画文件获取
- **VRM Animation 官方示例**: https://github.com/vrm-c/vrm-specification
- **Mixamo 动画**: https://www.mixamo.com/ (需转换为 .vrma)
- **自制动画**: 使用 Blender + VRM 插件

### 动画文件格式
- `.vrma` - VRM Animation 格式
- 包含骨骼动画数据
- 可以在 VRM 1.0 模型上播放

---

## 🎬 下一步

选择一个方案后告诉我，我可以帮你：
1. ✅ 实现代码修改
2. ✅ 测试动作触发
3. ✅ 集成到 Cursor Hook
4. ✅ 添加更多预定义动作












