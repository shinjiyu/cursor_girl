import { Talk } from './messages'

/**
 * Edge TTS API 集成（免费、无需注册、支持中文）
 * 使用 Microsoft Edge 浏览器的 TTS API
 */

export async function synthesizeVoiceEdgeTTSApi(
  talk: Talk,
  voiceName: string = 'zh-CN-XiaoxiaoNeural',  // 默认晓晓女声
  rate: string = '+0%',      // 语速 -50% 到 +100%
  volume: string = '+0%',    // 音量 -50% 到 +50%
  pitch: string = '+0Hz'     // 音调 -50Hz 到 +50Hz
): Promise<ArrayBuffer | null> {
  const message = talk.message

  try {
    console.log(`🎤 [Edge TTS] Synthesizing: "${message}"`)

    // 调用 Next.js API 路由
    const response = await fetch('/api/tts-edge', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: message,
        voiceName,
        rate,
        volume,
        pitch,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('❌ [Edge TTS] API Error:', errorData)
      throw new Error(
        `Edge TTS failed: ${response.status} ${errorData.error || ''}`
      )
    }

    const arrayBuffer = await response.arrayBuffer()
    console.log(
      `✅ [Edge TTS] Success, audio size: ${arrayBuffer.byteLength} bytes`
    )
    return arrayBuffer
  } catch (error) {
    console.error('❌ [Edge TTS] Error:', error)
    return null
  }
}

/**
 * Edge TTS 支持的中文声音列表
 */
export const EDGE_TTS_VOICES = {
  // 中文普通话（大陆）
  'zh-CN-XiaoxiaoNeural': { name: '晓晓', gender: '女', description: '温柔甜美' },
  'zh-CN-XiaoyiNeural': { name: '晓伊', gender: '女', description: '知性优雅' },
  'zh-CN-YunjianNeural': { name: '云健', gender: '男', description: '体育解说' },
  'zh-CN-YunxiNeural': { name: '云希', gender: '男', description: '沉稳专业' },
  'zh-CN-YunxiaNeural': { name: '云霞', gender: '男', description: '年轻活力' },
  'zh-CN-YunyangNeural': { name: '云扬', gender: '男', description: '新闻播报' },
  
  // 中文（台湾）
  'zh-TW-HsiaoChenNeural': { name: '小陈', gender: '女', description: '台湾女声' },
  'zh-TW-YunJheNeural': { name: '云哲', gender: '男', description: '台湾男声' },
  
  // 中文（香港）
  'zh-HK-HiuMaanNeural': { name: '曉曼', gender: '女', description: '香港女声' },
  'zh-HK-WanLungNeural': { name: '雲龍', gender: '男', description: '香港男声' },
} as const

export type EdgeTTSVoiceName = keyof typeof EDGE_TTS_VOICES


