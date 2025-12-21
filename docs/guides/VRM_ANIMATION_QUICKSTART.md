# VRM 动画快速开始指南

## 🚀 5 分钟快速添加动画

### 目标
在你的 AITuber 中添加"挥手"动画，从 Cursor Hook 触发。

---

## 📋 准备工作

- [ ] 电脑可以上网
- [ ] 浏览器（Chrome/Firefox/Safari）
- [ ] 约 10 分钟时间

---

## 🎯 步骤 1：下载动画（3分钟）

### 1.1 访问 Mixamo

打开浏览器，访问：https://www.mixamo.com/

![Mixamo 首页](https://www.mixamo.com/assets/images/social.jpg)

> 💡 **提示**：首次访问可能需要注册 Adobe 账号（免费），用邮箱注册即可。

### 1.2 搜索动画

在搜索框输入：`Waving`

你会看到多个挥手动画，选择一个你喜欢的（推荐 "Waving"）。

### 1.3 下载设置

点击右上角的 **"Download"** 按钮，设置如下：

```
┌─────────────────────────────┐
│ Format: FBX for Unity       │  ← 选择这个
│ Skin: Without Skin          │  ← 不要皮肤
│ Frames per second: 30       │  ← 30 FPS
└─────────────────────────────┘
```

点击 **"Download"** 开始下载。

> 📥 文件会保存到你的 Downloads 目录，名称类似：`Waving.fbx`

---

## 🔧 步骤 2：转换为 VRMA 格式（2分钟）

### 2.1 访问转换工具

打开新标签页，访问：https://3dretarget.com/zh

### 2.2 选择转换功能

点击 **"Mixamo FBX 转 VRMA"** 按钮。

### 2.3 上传文件

1. 点击 **"选择文件"** 或拖拽刚下载的 `Waving.fbx`
2. 等待上传（约 5-10 秒）
3. 系统自动转换（约 10-20 秒）
4. 下载生成的 `.vrma` 文件

> 💾 **重命名文件**：将下载的文件重命名为 `wave.vrma`（方便识别）

---

## 📁 步骤 3：放入项目（1分钟）

### 3.1 移动文件

将 `wave.vrma` 文件移动到：

```
/Users/user/Documents/ cursorgirl/aituber-kit/public/animations/wave.vrma
```

使用 Finder 操作：
1. 打开 Finder
2. 前往下载目录
3. 找到 `wave.vrma`
4. 拖到项目的 `aituber-kit/public/animations/` 目录

或使用命令行：

```bash
mv ~/Downloads/wave.vrma "/Users/user/Documents/ cursorgirl/aituber-kit/public/animations/"
```

---

## ⚙️ 步骤 4：配置代码（2分钟）

### 4.1 编辑动画控制器

打开文件：`aituber-kit/src/features/emoteController/animationController.ts`

找到 `preloadAnimations()` 方法（约第 61 行）：

```typescript
async preloadAnimations() {
  console.log('🎬 [AnimationController] Preloading animations...')
  
  const animations = [
    { name: 'idle', url: '/idle_loop.vrma' },
    // 🆕 添加这一行
    { name: 'wave', url: '/animations/wave.vrma' },
  ]
  
  // ... 其余代码不变
}
```

### 4.2 添加情绪映射

在同一文件中，找到 `emotionAnimations` 对象（约第 17 行）：

```typescript
private emotionAnimations: Record<string, string> = {
  neutral: 'idle',
  happy: 'joy',
  sad: 'sad',
  angry: 'angry',
  relaxed: 'relax',
  surprised: 'surprise',
  // 🆕 添加这一行
  wave: 'wave',
}
```

### 4.3 保存文件

按 `Cmd + S`（Mac）或 `Ctrl + S`（Windows）保存。

---

## 🧪 步骤 5：测试动画（2分钟）

### 5.1 重启 AITuber

如果 AITuber 正在运行，重启它：

```bash
cd "/Users/user/Documents/ cursorgirl/aituber-kit"
npm run dev
```

打开浏览器访问：http://localhost:3000

### 5.2 从 Cursor 触发

在 Cursor Hook 中触发动画：

```python
from bridge.websocket_client import OrtensiaClient

client = OrtensiaClient()
client.send_aituber_text(
    text="你好！",
    emotion="wave",  # 🎯 触发挥手动画
    conversation_id="your_conv_id"
)
```

### 5.3 观察效果

你应该看到 AITuber 角色挥手！🎉

---

## ✅ 验证清单

完成后检查：

- [ ] 动画文件存在于 `public/animations/wave.vrma`
- [ ] `animationController.ts` 中添加了 wave 配置
- [ ] AITuber 启动时看到 "✅ Animation loaded: wave" 日志
- [ ] 从 Cursor 发送 `emotion="wave"` 能看到挥手动作
- [ ] 动画播放流畅，无卡顿

---

## 🐛 常见问题

### Q1: 动画没有播放

**检查项**：
1. 文件路径是否正确？
   ```bash
   ls "/Users/user/Documents/ cursorgirl/aituber-kit/public/animations/wave.vrma"
   ```
2. 控制台有错误吗？（打开浏览器 DevTools）
3. 重启 AITuber 了吗？

**解决方案**：
- 确保文件名完全一致（区分大小写）
- 检查 URL 路径：`/animations/wave.vrma`（注意斜杠）
- 查看控制台日志，确认动画加载成功

### Q2: 动画播放不自然

**可能原因**：
- 动画与模型骨骼不匹配
- 文件转换有问题

**解决方案**：
- 尝试下载不同的 Mixamo 动画
- 使用标准 VRM 模型测试
- 在 Blender 中检查动画

### Q3: 下载的 VRMA 文件很大

**正常大小**：100KB - 500KB

**如果 > 2MB**：
- 可能包含了不必要的数据
- 尝试重新转换，确保 "Without Skin" 选项

### Q4: 3dRetarget 转换失败

**备用方案**：
1. 使用 Blender 手动转换（见学习指南）
2. 尝试不同的动画文件
3. 检查 FBX 文件是否完整

---

## 🎯 下一步

成功添加挥手动画后，继续尝试：

1. **添加更多动作**
   - 鞠躬（Bowing）
   - 点头（Yes）
   - 思考（Thinking）
   - 庆祝（Victory）

2. **组合动作**
   - 在一条消息中触发多个动作
   - 根据 AI 回复内容自动选择动作

3. **自定义动画**
   - 学习 Blender 制作专属动画
   - 参考 `VRM_ANIMATION_LEARNING_PATH.md`

---

## 📚 参考资源

- **详细资源列表**：`docs/VRM_ANIMATION_RESOURCES.md`
- **完整学习路径**：`docs/VRM_ANIMATION_LEARNING_PATH.md`
- **动画设计方案**：`docs/ANIMATION_ACTION_DESIGN.md`

---

## 🎨 动画创意参考

为不同场景设计动画：

| 场景 | 推荐动画 | Mixamo 关键词 |
|------|----------|---------------|
| Agent 开始工作 | 点头确认 | Yes, Nod |
| Agent 思考中 | 思考动作 | Thinking, Pondering |
| Agent 完成任务 | 庆祝、鼓掌 | Victory, Clapping |
| Agent 遇到错误 | 挠头、困惑 | Confused, Scratching Head |
| 用户提问 | 挥手问候 | Waving, Greeting |
| 用户感谢 | 鞠躬 | Bowing, Thank You |
| 长时间等待 | 闲置动作 | Idle, Looking Around |
| 阅读代码 | 指向、讲解 | Pointing, Explaining |

---

## 💡 高级技巧

### 动作链

在 Python 中组合多个动作：

```python
# 示例：Agent 完成复杂任务的动作序列
actions = [
    ("开始思考了...", "think"),
    ("找到解决方案！", "celebrate"),
    ("完成！", "bow"),
]

for text, emotion in actions:
    client.send_aituber_text(
        text=text,
        emotion=emotion,
        conversation_id=conv_id
    )
    time.sleep(2)  # 等待动画播放
```

### 根据内容自动选择动作

```python
def choose_emotion(text):
    """根据文本内容选择合适的动作"""
    if "完成" in text or "成功" in text:
        return "celebrate"
    elif "思考" in text or "让我想想" in text:
        return "think"
    elif "收到" in text or "明白" in text:
        return "nod"
    elif "抱歉" in text or "对不起" in text:
        return "bow"
    else:
        return "neutral"

# 使用
emotion = choose_emotion("任务完成了！")
client.send_aituber_text(text="任务完成了！", emotion=emotion)
```

---

## 🎉 恭喜！

你已经成功添加了第一个 VRM 动画！

现在你可以：
- ✅ 从 Mixamo 下载动画
- ✅ 转换为 VRMA 格式
- ✅ 集成到 AITuber 项目
- ✅ 从代码中触发动画

继续探索更多可能性吧！🚀

---

**创建日期**：2025-12-05  
**适用版本**：AITuberKit v2.0+  
**难度等级**：⭐⭐（初级）






















