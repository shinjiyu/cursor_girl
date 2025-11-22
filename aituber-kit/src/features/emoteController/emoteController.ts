import * as THREE from 'three'
import { VRM, VRMExpressionPresetName } from '@pixiv/three-vrm'
import { ExpressionController } from './expressionController'
import { AnimationController } from './animationController'

/**
 * 感情表現としてExpressionとMotionを操作する為のクラス
 * 表情（Expression）と身体動画（Animation）の両方をサポート
 */
export class EmoteController {
  private _expressionController: ExpressionController
  private _animationController: AnimationController
  private _mixer: THREE.AnimationMixer

  constructor(vrm: VRM, camera: THREE.Object3D, mixer: THREE.AnimationMixer) {
    this._expressionController = new ExpressionController(vrm, camera)
    this._mixer = mixer
    this._animationController = new AnimationController(vrm, mixer)
    
    // 预加载动画
    this._animationController.preloadAnimations().catch(err => {
      console.log('⚠️  Animation preload error:', err)
    })
    
    console.log('✅ EmoteController initialized with animation support')
  }

  public playEmotion(preset: VRMExpressionPresetName) {
    // 尝试使用表情控制器（如果模型支持BlendShapes）
    this._expressionController.playEmotion(preset)
    
    // 同时播放身体动画作为补充或替代
    this._animationController.playEmotion(preset)
  }

  public lipSync(preset: VRMExpressionPresetName, value: number) {
    this._expressionController.lipSync(preset, value)
  }

  public update(delta: number) {
    this._expressionController.update(delta)
    this._animationController.update(delta)
  }
  
  public stopAllAnimations() {
    this._animationController.stopAll()
  }
}
