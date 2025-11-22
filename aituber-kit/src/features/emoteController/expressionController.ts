import * as THREE from 'three'
import {
  VRM,
  VRMExpressionManager,
  VRMExpressionPresetName,
} from '@pixiv/three-vrm'
import { AutoLookAt } from './autoLookAt'
import { AutoBlink } from './autoBlink'

/**
 * Expressionを管理するクラス
 *
 * 主に前の表情を保持しておいて次の表情を適用する際に0に戻す作業や、
 * 前の表情が終わるまで待ってから表情適用する役割を持っている。
 */
export class ExpressionController {
  private _autoLookAt: AutoLookAt
  private _autoBlink?: AutoBlink
  private _expressionManager?: VRMExpressionManager
  private _currentEmotion: VRMExpressionPresetName
  private _currentLipSync: {
    preset: VRMExpressionPresetName
    value: number
  } | null
  constructor(vrm: VRM, camera: THREE.Object3D) {
    this._autoLookAt = new AutoLookAt(vrm, camera)
    this._currentEmotion = 'neutral'
    this._currentLipSync = null
    if (vrm.expressionManager) {
      this._expressionManager = vrm.expressionManager
      this._autoBlink = new AutoBlink(vrm.expressionManager)
    }
  }

  public playEmotion(preset: VRMExpressionPresetName) {
    console.log('🎭 [ExpressionController.playEmotion] Called with preset:', preset)
    console.log('   - Current emotion:', this._currentEmotion)
    console.log('   - Expression manager exists:', !!this._expressionManager)
    
    if (this._currentEmotion != 'neutral') {
      console.log('   - Resetting previous emotion:', this._currentEmotion)
      this._expressionManager?.setValue(this._currentEmotion, 0)
    }

    if (preset == 'neutral') {
      console.log('   - Setting to neutral, enabling auto blink')
      this._autoBlink?.setEnable(true)
      this._currentEmotion = preset
      return
    }

    const t = this._autoBlink?.setEnable(false) || 0
    this._currentEmotion = preset
    console.log('   - Setting emotion after', t, 'seconds')
    
    setTimeout(() => {
      console.log('   - Actually setting emotion:', preset, 'to value 1')
      this._expressionManager?.setValue(preset, 1)
      
      // 验证是否设置成功
      if (this._expressionManager) {
        const currentValue = this._expressionManager.getValue(preset)
        console.log('   - Emotion value after setting:', currentValue)
        
        // 列出所有可用的表情
        try {
          const expressionMap = this._expressionManager.expressionMap
          if (expressionMap) {
            // expressionMap 是一个对象，不是 Map
            const availableExpressions = Object.keys(expressionMap)
            console.log('   - Available expressions:', availableExpressions)
          } else {
            console.log('   - No expression map found')
          }
        } catch (error) {
          console.log('   - Error getting expressions:', error)
        }
      }
    }, t * 1000)
  }

  public lipSync(preset: VRMExpressionPresetName, value: number) {
    if (this._currentLipSync) {
      this._expressionManager?.setValue(this._currentLipSync.preset, 0)
    }
    this._currentLipSync = {
      preset,
      value,
    }
  }

  public update(delta: number) {
    if (this._autoBlink) {
      this._autoBlink.update(delta)
    }

    if (this._currentLipSync) {
      const weight =
        this._currentEmotion === 'neutral'
          ? this._currentLipSync.value * 0.5
          : this._currentLipSync.value * 0.25
      this._expressionManager?.setValue(this._currentLipSync.preset, weight)
    }
  }
}
