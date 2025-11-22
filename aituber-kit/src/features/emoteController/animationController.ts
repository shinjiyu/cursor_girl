import * as THREE from 'three'
import { VRM } from '@pixiv/three-vrm'
import { VRMAnimation } from '../../lib/VRMAnimation/VRMAnimation'

/**
 * 动画控制器 - 管理 VRM 身体动画
 * 
 * 用于没有 BlendShape 表情的模型，通过身体动画表达情绪
 */
export class AnimationController {
  private vrm: VRM
  private mixer: THREE.AnimationMixer
  private currentAnimation: THREE.AnimationAction | null = null
  private animationCache: Map<string, THREE.AnimationClip> = new Map()
  
  // 情绪到动画的映射
  private emotionAnimations: Record<string, string> = {
    neutral: 'idle',
    happy: 'joy',
    sad: 'sad',
    angry: 'angry',
    relaxed: 'relax',
    surprised: 'surprise',
  }
  
  constructor(vrm: VRM, mixer: THREE.AnimationMixer) {
    this.vrm = vrm
    this.mixer = mixer
    console.log('🎬 [AnimationController] Initialized')
  }
  
  /**
   * 加载动画文件
   */
  async loadAnimation(name: string, url: string): Promise<boolean> {
    try {
      console.log(`🎬 [AnimationController] Loading animation: ${name} from ${url}`)
      
      const response = await fetch(url)
      if (!response.ok) {
        console.log(`⚠️  Animation file not found: ${url}`)
        return false
      }
      
      const arrayBuffer = await response.arrayBuffer()
      const vrmAnimation = await VRMAnimation.deserialize(arrayBuffer)
      const clip = vrmAnimation.createAnimationClip(this.vrm)
      
      this.animationCache.set(name, clip)
      console.log(`✅ Animation loaded: ${name}`)
      return true
    } catch (error) {
      console.log(`⚠️  Failed to load animation ${name}:`, error)
      return false
    }
  }
  
  /**
   * 预加载所有动画
   */
  async preloadAnimations() {
    console.log('🎬 [AnimationController] Preloading animations...')
    
    const animations = [
      { name: 'idle', url: '/idle_loop.vrma' },
      // 可以添加更多动画文件
      // { name: 'joy', url: '/joy.vrma' },
      // { name: 'sad', url: '/sad.vrma' },
    ]
    
    const results = await Promise.all(
      animations.map(anim => this.loadAnimation(anim.name, anim.url))
    )
    
    const loadedCount = results.filter(r => r).length
    console.log(`✅ Preloaded ${loadedCount}/${animations.length} animations`)
  }
  
  /**
   * 播放情绪动画
   */
  playEmotion(emotion: string) {
    console.log(`🎬 [AnimationController] Playing emotion: ${emotion}`)
    
    // 获取对应的动画名称
    const animationName = this.emotionAnimations[emotion] || 'idle'
    console.log(`   - Mapped to animation: ${animationName}`)
    
    // 如果动画已加载，播放它
    const clip = this.animationCache.get(animationName)
    if (clip) {
      this.playAnimation(clip)
    } else {
      console.log(`   - Animation not loaded: ${animationName}, using default pose`)
      // 使用默认的 idle 动画或姿势
      this.playDefaultPose(emotion)
    }
  }
  
  /**
   * 播放动画
   */
  private playAnimation(clip: THREE.AnimationClip) {
    // 停止当前动画
    if (this.currentAnimation) {
      this.currentAnimation.fadeOut(0.3)
    }
    
    // 播放新动画
    const action = this.mixer.clipAction(clip)
    action.reset()
    action.fadeIn(0.3)
    action.play()
    
    this.currentAnimation = action
    console.log(`✅ Playing animation: ${clip.name}`)
  }
  
  /**
   * 播放默认姿势（简单的关键帧动画）
   */
  private playDefaultPose(emotion: string) {
    console.log(`🎬 [AnimationController] Using default pose for: ${emotion}`)
    
    // 根据情绪设置简单的身体姿势
    switch (emotion) {
      case 'happy':
        this.animateHead(0.1, 0, 0, 1.0) // 微微上扬
        break
      case 'sad':
        this.animateHead(-0.1, 0, 0, 1.0) // 低头
        break
      case 'surprised':
        this.animateHead(0.05, 0, 0, 0.5) // 轻微后仰
        break
      case 'angry':
        this.animateHead(0, 0.05, 0, 0.8) // 稍微倾斜
        break
      default:
        this.animateHead(0, 0, 0, 1.0) // 中立姿势
    }
  }
  
  /**
   * 动画化头部旋转
   */
  private animateHead(x: number, y: number, z: number, duration: number) {
    const headBone = this.vrm.humanoid?.getNormalizedBoneNode('head')
    if (!headBone) return
    
    // 保存初始旋转
    const startRotation = headBone.rotation.clone()
    const endRotation = new THREE.Euler(x, y, z)
    
    // 创建简单的补间动画
    const start = Date.now()
    const animate = () => {
      const elapsed = (Date.now() - start) / 1000
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用缓动函数
      const t = this.easeInOutCubic(progress)
      
      headBone.rotation.setFromQuaternion(
        new THREE.Quaternion().setFromEuler(startRotation).slerp(
          new THREE.Quaternion().setFromEuler(endRotation),
          t
        )
      )
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        // 动画结束后，缓慢回到中立位置
        setTimeout(() => {
          this.animateHead(0, 0, 0, duration * 1.5)
        }, 500)
      }
    }
    
    animate()
  }
  
  /**
   * 缓动函数
   */
  private easeInOutCubic(t: number): number {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2
  }
  
  /**
   * 停止所有动画
   */
  stopAll() {
    if (this.currentAnimation) {
      this.currentAnimation.stop()
      this.currentAnimation = null
    }
  }
  
  /**
   * 更新动画（每帧调用）
   */
  update(delta: number) {
    // mixer 会自动更新所有动画
    // 这里可以添加额外的更新逻辑
  }
}



