import { Talk } from './messages'

/**
 * 科大讯飞 TTS API 集成
 * 文档: https://www.xfyun.cn/doc/tts/online_tts/API.html
 */

interface XunfeiConfig {
  appId: string
  apiSecret: string
  apiKey: string
}

export async function synthesizeVoiceXunfeiApi(
  talk: Talk,
  appId: string,
  apiKey: string,
  apiSecret: string,
  voiceName: string = 'xiaoyan',  // 默认小燕（温柔女声）
  speed: number = 50,              // 语速 0-100
  volume: number = 50,             // 音量 0-100
  pitch: number = 50               // 音调 0-100
): Promise<ArrayBuffer | null> {
  const message = talk.message

  try {
    console.log(`🎤 [Xunfei TTS] Synthesizing: "${message}"`)

    // 调用 Next.js API 路由
    const response = await fetch('/api/tts-xunfei', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: message,
        appId,
        apiKey,
        apiSecret,
        voiceName,
        speed,
        volume,
        pitch,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('❌ [Xunfei TTS] API Error:', errorData)
      throw new Error(
        `Xunfei TTS failed: ${response.status} ${errorData.error || ''}`
      )
    }

    const arrayBuffer = await response.arrayBuffer()
    console.log(
      `✅ [Xunfei TTS] Success, audio size: ${arrayBuffer.byteLength} bytes`
    )
    return arrayBuffer
  } catch (error) {
    console.error('❌ [Xunfei TTS] Error:', error)
    return null
  }
}

/**
 * 讯飞语音支持的声音列表
 */
export const XUNFEI_VOICES = {
  // 中文普通话
  xiaoyan: { name: '小燕', gender: '女', language: 'zh-CN', description: '温柔甜美' },
  aisjiuxu: { name: '许久', gender: '男', language: 'zh-CN', description: '沉稳磁性' },
  aisxping: { name: '小萍', gender: '女', language: 'zh-CN', description: '知性优雅' },
  aisjinger: { name: '小婧', gender: '女', language: 'zh-CN', description: '温暖治愈' },
  aisbabyxu: { name: '许小宝', gender: '童声', language: 'zh-CN', description: '童真可爱' },
  
  // 方言
  vixying: { name: '小颖', gender: '女', language: 'zh-CN-粤语', description: '粤语女声' },
  vixy: { name: '小莹', gender: '女', language: 'zh-CN-四川话', description: '四川女声' },
  vixk: { name: '小坤', gender: '男', language: 'zh-CN-河南话', description: '河南男声' },
  
  // 英语
  vimary: { name: 'Mary', gender: '女', language: 'en-US', description: '美式英语' },
  vixiaoxin: { name: '晓欣', gender: '女', language: 'en-US', description: '中式英语' },
} as const

export type XunfeiVoiceName = keyof typeof XUNFEI_VOICES


