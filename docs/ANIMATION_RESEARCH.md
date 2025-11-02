# VRM 动作系统研究

## 📋 当前状态分析

### ✅ 已实现功能

1. **口型同步（Lip Sync）**
   - 通过 `lipSync()` 方法实现
   - 基于音频播放控制嘴部 BlendShape
   - 工作正常 ✅

2. **自动眨眼（Auto Blink）**
   - `AutoBlink` 类实现
   - 随机眨眼效果
   - 增加真实感 ✅

3. **基础身体动画**
   - `AnimationController` 类
   - 支持加载 `.vrma` 动画文件
   - 目前只有 `idle_loop.vrma`（站立循环）

4. **表情系统**
   - `ExpressionController` 类
   - 支持 7 种情绪表情
   - 依赖模型的 BlendShape 数据

### ❌ 缺失的功能

1. **丰富的身体动作**
   - ❌ 挥手
   - ❌ 点头/摇头
   - ❌ 鞠躬
   - ❌ 庆祝动作
   - ❌ 思考动作
   - ❌ 打招呼

2. **程序化动画**
   - ❌ 不依赖预制动画文件
   - ❌ 实时生成动作
   - ❌ 参数化控制

3. **动作组合**
   - ❌ 多个动作的平滑过渡
   - ❌ 动作队列系统
   - ❌ 动作优先级

4. **闲置行为**
   - ❌ 随机小动作
   - ❌ 视线移动
   - ❌ 身体摇晃

---

## 🎯 VRM 动画系统详解

### 1. VRM 动画格式 (.vrma)

**官方规范**: [VRMC_vrm_animation](https://github.com/vrm-c/vrm-specification/blob/master/specification/VRMC_vrm_animation-1.0/README.ja.md)

#### 特点：
- 基于 glTF 扩展
- 包含骨骼动画（骨架变换）
- 包含表情动画（BlendShape）
- 可以包含视线控制

#### 优点：
- ✅ 专门为 VRM 模型设计
- ✅ 可以在 3D 软件中制作（Blender, Unity）
- ✅ 支持完整的身体动画
- ✅ 文件格式标准化

#### 缺点：
- ❌ 需要预先制作
- ❌ 文件大小较大
- ❌ 不够灵活

### 2. THREE.js 动画系统

#### AnimationMixer
- 动画播放器
- 支持多个动画轨道
- 自动插值和混合

#### AnimationClip
- 动画剪辑（一段完整动画）
- 包含多个 KeyframeTrack

#### AnimationAction
- 动画动作（可控制的播放实例）
- 可以设置循环、速度、权重等

---

## 💡 改进方案

### 方案 A: 使用预制 .vrma 动画文件

**优点**: 
- 动画质量高
- 容易制作（在 Blender/Unity 中）
- 可以有复杂的全身动作

**缺点**:
- 需要外部工具制作
- 文件体积大
- 不够灵活

**实现步骤**:
1. 在 Blender 中为 VRM 模型制作动画
2. 导出为 .vrma 格式
3. 加载到应用中
4. 创建动作库

**所需动画列表**:
- ✅ idle_loop.vrma（已有）
- 🎯 wave_hello.vrma（挥手打招呼）
- 🎯 nod.vrma（点头）
- 🎯 shake_head.vrma（摇头）
- 🎯 bow.vrma（鞠躬）
- 🎯 celebrate.vrma（庆祝）
- 🎯 think.vrma（思考）
- 🎯 joy.vrma（高兴跳跃）
- 🎯 sad.vrma（难过）
- 🎯 surprised.vrma（惊讶后退）

### 方案 B: 程序化动画（Procedural Animation）

**优点**:
- 实时生成，无需文件
- 灵活可调
- 文件体积小
- 可以响应实时数据

**缺点**:
- 实现复杂
- 可能不够自然
- 需要精细调整

**实现方式**:

#### 1. 直接操作骨骼（Bone Manipulation）

```typescript
// 示例：让角色点头
const neck = vrm.humanoid.getNormalizedBoneNode('neck')
if (neck) {
  // 使用 sin 函数创建平滑的点头动作
  const angle = Math.sin(time * 2) * 0.2  // 摇晃角度
  neck.rotation.x = angle
}
```

**可控制的骨骼**:
- `head` - 头部
- `neck` - 脖子
- `leftUpperArm`, `rightUpperArm` - 上臂
- `leftLowerArm`, `rightLowerArm` - 下臂
- `leftHand`, `rightHand` - 手
- `spine`, `chest` - 躯干
- `hips` - 臀部
- `leftUpperLeg`, `rightUpperLeg` - 大腿
- `leftLowerLeg`, `rightLowerLeg` - 小腿

#### 2. 使用 IK (Inverse Kinematics)

让手、脚等末端骨骼移动到目标位置，自动计算中间骨骼的旋转。

```typescript
// 示例：让右手移动到目标位置
const targetPosition = new THREE.Vector3(0.3, 1.2, 0.2)
moveHandToPosition(vrm, 'right', targetPosition)
```

#### 3. 参数化动作系统

```typescript
// 定义动作参数
interface ActionParams {
  emotion: string      // 情绪
  intensity: number    // 强度 0-1
  duration: number     // 持续时间（秒）
  easing: string       // 缓动函数
}

// 使用参数生成动作
playProceduralAction('wave', {
  emotion: 'happy',
  intensity: 0.8,
  duration: 2.0,
  easing: 'easeInOut'
})
```

### 方案 C: 混合方案（推荐）

结合两种方案的优点：

1. **重要动作使用 .vrma**
   - 复杂的全身动作
   - 质量要求高的动画
   - 例如：跳跃、鞠躬、庆祝

2. **简单动作使用程序化生成**
   - 点头、摇头
   - 挥手
   - 闲置小动作
   - 视线跟踪

3. **动作混合系统**
   - 上半身和下半身分离控制
   - 叠加动作（例如：走路 + 挥手）

---

## 🚀 实施计划

### Phase 1: 程序化动作基础 (1-2天)

#### 目标
实现几个简单的程序化动作，不需要外部文件。

#### 任务
1. ✅ 创建 `ProceduralAnimationController` 类
2. ✅ 实现点头动作
3. ✅ 实现摇头动作
4. ✅ 实现挥手动作
5. ✅ 实现身体摇晃（闲置动作）
6. ✅ 集成到 EmoteController

#### 技术细节
```typescript
class ProceduralAnimationController {
  // 点头：Head 骨骼的 X 轴旋转
  playNod(duration: number, intensity: number)
  
  // 摇头：Head 骨骼的 Y 轴旋转
  playShakeHead(duration: number, intensity: number)
  
  // 挥手：RightUpperArm, RightLowerArm 的旋转
  playWave(hand: 'left' | 'right', duration: number)
  
  // 身体摇晃：Spine, Chest 的轻微旋转
  playIdleSway(intensity: number)
}
```

### Phase 2: 动作库系统 (1-2天)

#### 目标
创建一个可扩展的动作库，方便添加新动作。

#### 任务
1. ✅ 设计动作定义接口
2. ✅ 创建动作注册系统
3. ✅ 实现动作播放队列
4. ✅ 实现动作混合（blend）
5. ✅ 添加动作事件系统

#### 技术细节
```typescript
interface ActionDefinition {
  name: string
  type: 'procedural' | 'vrma'
  category: 'gesture' | 'emotion' | 'idle'
  bones: BoneAnimation[]
  duration: number
  loop: boolean
  blend: {
    in: number   // 淡入时间
    out: number  // 淡出时间
  }
}

class ActionLibrary {
  register(action: ActionDefinition)
  get(name: string): ActionDefinition
  play(name: string, params?: ActionParams)
  queue(actions: string[])  // 排队播放
}
```

### Phase 3: 情绪驱动动作 (1天)

#### 目标
根据情绪自动触发合适的动作。

#### 任务
1. ✅ 创建情绪-动作映射表
2. ✅ 实现动作选择逻辑
3. ✅ 添加随机性（同一情绪多种动作）
4. ✅ 集成到 WebSocket 消息处理

#### 技术细节
```typescript
const emotionActions = {
  happy: ['wave', 'jump', 'nod'],
  sad: ['lookDown', 'shake_head'],
  surprised: ['stepBack', 'hands_up'],
  excited: ['celebrate', 'jump', 'wave'],
  // ...
}

// 自动选择动作
function selectActionForEmotion(emotion: string): string {
  const actions = emotionActions[emotion]
  return actions[Math.floor(Math.random() * actions.length)]
}
```

### Phase 4: 闲置行为系统 (1天)

#### 目标
角色在无操作时的自然行为。

#### 任务
1. ✅ 创建 IdleBehaviorController
2. ✅ 实现随机小动作
3. ✅ 实现视线移动
4. ✅ 实现呼吸动画
5. ✅ 集成到主循环

#### 技术细节
```typescript
class IdleBehaviorController {
  private timers: Map<string, number>
  private vrm: VRM
  
  update(delta: number) {
    // 每 5-10 秒触发一个随机小动作
    if (this.shouldTriggerIdle()) {
      const action = this.randomIdleAction()
      this.play(action)
    }
    
    // 持续的呼吸动画
    this.updateBreathing(delta)
    
    // 随机视线移动
    this.updateGaze(delta)
  }
  
  private randomIdleActions = [
    'slight_nod',      // 轻微点头
    'look_around',     // 环顾四周
    'adjust_posture',  // 调整姿势
    'blink',          // 眨眼
    'sway',           // 轻微摇晃
  ]
}
```

### Phase 5: .vrma 动画集成（可选，2-3天）

如果需要更复杂的动作：

#### 任务
1. 学习 Blender VRM 插件
2. 制作关键动画
3. 导出为 .vrma 格式
4. 集成到应用中
5. 创建动画管理器

---

## 🎨 动作设计指南

### 1. 打招呼（Greeting）

**场景**: 
- 开始对话
- Agent 首次响应
- 用户进入

**动作组合**:
1. 挥手（2秒）
2. 微笑表情
3. 轻微点头（1秒）

**情绪**: happy, excited

### 2. 思考（Thinking）

**场景**:
- Agent 正在处理
- 复杂任务执行中

**动作组合**:
1. 手托下巴
2. 视线向上
3. 轻微摇头

**情绪**: neutral

### 3. 庆祝（Celebrate）

**场景**:
- 任务完成
- 测试通过
- Git 提交成功

**动作组合**:
1. 双手举起
2. 轻微跳跃
3. 开心表情

**情绪**: excited, happy

### 4. 鞠躬（Bow）

**场景**:
- 道歉
- 感谢
- 请求

**动作组合**:
1. 上半身前倾 45°
2. 保持 1-2 秒
3. 缓慢起身

**情绪**: neutral, sad

### 5. 惊讶（Surprised）

**场景**:
- 错误发生
- 意外结果

**动作组合**:
1. 后退半步
2. 双手抬起
3. 惊讶表情

**情绪**: surprised

---

## 📊 技术参考

### VRM Humanoid Bones

VRM 1.0 标准骨骼：
```
- hips (root)
  - spine
    - chest
      - upperChest (optional)
        - neck
          - head
            - leftEye, rightEye
        - leftShoulder, rightShoulder
          - leftUpperArm, rightUpperArm
            - leftLowerArm, rightLowerArm
              - leftHand, rightHand
                - (手指骨骼...)
  - leftUpperLeg, rightUpperLeg
    - leftLowerLeg, rightLowerLeg
      - leftFoot, rightFoot
```

### 常用旋转角度参考

```typescript
// 点头
head.rotation.x = THREE.MathUtils.degToRad(15)  // 向下 15°

// 摇头
head.rotation.y = THREE.MathUtils.degToRad(30)  // 左右 30°

// 鞠躬
spine.rotation.x = THREE.MathUtils.degToRad(-45) // 前倾 45°

// 挥手
upperArm.rotation.z = THREE.MathUtils.degToRad(45)  // 抬起 45°
lowerArm.rotation.x = THREE.MathUtils.degToRad(90)  // 弯曲 90°
```

### 缓动函数（Easing）

```typescript
// 平滑进出
function easeInOutSine(t: number): number {
  return -(Math.cos(Math.PI * t) - 1) / 2
}

// 弹性效果
function easeOutElastic(t: number): number {
  const c4 = (2 * Math.PI) / 3
  return t === 0 ? 0 : t === 1 ? 1 :
    Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1
}
```

---

## 🔗 相关资源

- [VRM 规范](https://github.com/vrm-c/vrm-specification)
- [three-vrm 文档](https://github.com/pixiv/three-vrm)
- [VRMAnimation 规范](https://github.com/vrm-c/vrm-specification/tree/master/specification/VRMC_vrm_animation-1.0)
- [Three.js Animation 文档](https://threejs.org/docs/#api/en/animation/AnimationMixer)
- [Blender VRM 插件](https://vrm-addon-for-blender.info/)

---

## 📝 开发笔记

### 当前优先级

1. **Phase 1**: 程序化基础动作 ⭐⭐⭐
   - 最快见效
   - 不需要外部工具
   - 立即改善用户体验

2. **Phase 3**: 情绪驱动动作 ⭐⭐⭐
   - 与现有系统集成
   - 增加表现力

3. **Phase 4**: 闲置行为 ⭐⭐
   - 增加自然感
   - 提升沉浸感

4. **Phase 2**: 动作库系统 ⭐⭐
   - 为未来扩展打基础

5. **Phase 5**: .vrma 动画 ⭐
   - 可选项
   - 需要额外工具和技能

---

**文档版本**: 1.0  
**创建日期**: 2025-11-02  
**分支**: feature/rich-animations
