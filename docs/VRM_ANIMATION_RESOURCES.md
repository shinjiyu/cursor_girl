# VRM 动画资源下载指南

## 📦 第一步：下载 VRM 身体动画文件

### 方式 1：从 Mixamo 获取并转换（推荐 ⭐⭐⭐⭐⭐）

**Mixamo 优势**：
- ✅ 完全免费
- ✅ 动画质量高
- ✅ 种类丰富（2000+ 动画）
- ✅ 无需注册

#### 📥 推荐下载的动画列表

| 动画名称 | 用途 | Mixamo 搜索关键词 | 优先级 |
|---------|------|------------------|-------|
| 挥手打招呼 | 问候、确认 | `Waving` | ⭐⭐⭐⭐⭐ |
| 鞠躬 | 感谢、道歉 | `Bowing` | ⭐⭐⭐⭐⭐ |
| 点头 | 同意、确认 | `Yes` | ⭐⭐⭐⭐⭐ |
| 摇头 | 否定、拒绝 | `No` | ⭐⭐⭐⭐ |
| 思考动作 | AI 处理中 | `Thinking` | ⭐⭐⭐⭐⭐ |
| 庆祝动作 | 成功完成 | `Victory` | ⭐⭐⭐⭐ |
| 拍手 | 鼓励、赞美 | `Clapping` | ⭐⭐⭐⭐ |
| 惊讶 | 意外情况 | `Surprised` | ⭐⭐⭐ |
| 指向前方 | 引导注意 | `Pointing` | ⭐⭐⭐ |
| 交叉双臂 | 等待、自信 | `Arms Cross` | ⭐⭐⭐ |
| 站立呼吸 | 空闲动画 | `Idle` | ⭐⭐⭐⭐⭐ |
| 讲话手势 | 说话配合 | `Talking` | ⭐⭐⭐⭐ |

#### 🔧 转换工具

**选项 A：3dRetarget（在线工具，推荐）**
- 网址：https://3dretarget.com/zh
- 功能：Mixamo FBX → VRMA 一键转换
- 优点：无需安装软件，直接在线转换
- 限制：可能有文件大小限制

**使用步骤**：
1. 访问 https://www.mixamo.com/
2. 搜索动画（如 "Waving"）
3. 点击 "Download" → 选择 FBX 格式
4. 访问 https://3dretarget.com/zh
5. 选择 "Mixamo FBX 转 VRMA"
6. 上传刚下载的 FBX 文件
7. 下载生成的 `.vrma` 文件
8. 放到 `aituber-kit/public/animations/` 目录

**选项 B：Blender 手动转换（专业用户）**
- 需要安装 Blender + VRM 插件
- 适合需要微调动画的场景
- 详见下文"学习路径"部分

---

### 方式 2：使用 BVH 文件转换

**BVH 资源网站**：
- Carnegie Mellon Motion Capture Database: http://mocap.cs.cmu.edu/
- 免费的动作捕捉数据
- 需要转换为 VRMA 格式

**转换流程**：
```
BVH 文件 → 3dRetarget → VRMA 文件
```

---

### 方式 3：从开源项目获取

#### GitHub 资源（可能有限）

搜索关键词：
```bash
site:github.com vrma animation
site:github.com VRM animation files
```

**已知资源仓库**：
- `pixiv/three-vrm` - VRM 官方库，可能包含示例动画
- `vrm-c/vrm-specification` - VRM 规范仓库，包含测试文件

---

## 📂 推荐的文件组织结构

```
aituber-kit/public/
├── animations/              # 新建目录
│   ├── idle_loop.vrma      # 已有（站立循环）
│   ├── wave.vrma           # 挥手
│   ├── bow.vrma            # 鞠躬
│   ├── nod.vrma            # 点头
│   ├── shake_head.vrma     # 摇头
│   ├── think.vrma          # 思考
│   ├── celebrate.vrma      # 庆祝
│   ├── clap.vrma           # 鼓掌
│   ├── point.vrma          # 指向
│   └── talking.vrma        # 讲话手势
└── vrm/                    # VRM 模型目录
```

---

## 🚀 快速开始脚本

创建一个下载脚本（需要手动执行 Mixamo 下载，因为需要浏览器交互）：

```bash
#!/bin/bash
# download_animations.sh

# 创建动画目录
mkdir -p "aituber-kit/public/animations"

echo "📋 请按以下步骤下载 Mixamo 动画："
echo ""
echo "1️⃣  访问 https://www.mixamo.com/"
echo "2️⃣  搜索以下动画并下载（FBX 格式）："
echo "    - Waving (挥手)"
echo "    - Bowing (鞠躬)"
echo "    - Yes (点头)"
echo "    - Thinking (思考)"
echo "    - Victory (庆祝)"
echo "    - Clapping (鼓掌)"
echo ""
echo "3️⃣  访问 https://3dretarget.com/zh 转换为 VRMA"
echo "4️⃣  将生成的 .vrma 文件放到："
echo "    aituber-kit/public/animations/"
echo ""
echo "✅ 完成后运行 'npm run dev' 测试"
```

---

## 🎬 动画文件使用示例

下载完成后，修改 `animationController.ts`：

```typescript
// aituber-kit/src/features/emoteController/animationController.ts

async preloadAnimations() {
  const animations = [
    { name: 'idle', url: '/animations/idle_loop.vrma' },
    { name: 'wave', url: '/animations/wave.vrma' },
    { name: 'bow', url: '/animations/bow.vrma' },
    { name: 'nod', url: '/animations/nod.vrma' },
    { name: 'think', url: '/animations/think.vrma' },
    { name: 'celebrate', url: '/animations/celebrate.vrma' },
    { name: 'clap', url: '/animations/clap.vrma' },
  ]
  
  // ... 其余代码不变
}

// 扩展情绪映射
private emotionAnimations: Record<string, string> = {
  neutral: 'idle',
  happy: 'celebrate',
  sad: 'sad',
  angry: 'angry',
  relaxed: 'idle',
  surprised: 'surprise',
  // 新增动作
  wave: 'wave',
  bow: 'bow',
  nod: 'nod',
  think: 'think',
  clap: 'clap',
}
```

---

## 📊 动画质量检查清单

下载动画后，检查以下项目：

- [ ] 文件格式是否为 `.vrma`
- [ ] 文件大小是否合理（通常 100KB - 2MB）
- [ ] 在 VRM 模型上播放是否流畅
- [ ] 动画循环是否自然（如果是循环动画）
- [ ] 骨骼映射是否正确
- [ ] 手部动作是否完整
- [ ] 面部表情是否保留（如果原动画包含）

---

## 🔗 相关资源链接

- **Mixamo**: https://www.mixamo.com/
- **3dRetarget**: https://3dretarget.com/zh
- **VRM 规范**: https://github.com/vrm-c/vrm-specification
- **CMU Motion Capture**: http://mocap.cs.cmu.edu/
- **VRoid Hub**: https://hub.vroid.com/
- **VRM Consortium**: https://vrm.dev/

---

## ⚠️ 注意事项

1. **版权问题**：
   - Mixamo 动画可免费用于个人和商业项目
   - 其他来源请检查授权许可
   
2. **模型兼容性**：
   - 确保你的 VRM 模型支持 VRM 1.0 标准
   - 某些动画可能需要调整骨骼权重
   
3. **性能优化**：
   - 不要一次加载太多动画（影响性能）
   - 使用懒加载策略
   - 考虑压缩动画文件

4. **测试建议**：
   - 先下载 2-3 个常用动画测试
   - 确认效果后再批量下载
   - 在实际场景中测试动画触发

---

**更新日期**：2025-12-05  
**维护者**：Ortensia Project Team











