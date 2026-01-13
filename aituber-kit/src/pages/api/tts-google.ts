import type { NextApiRequest, NextApiResponse } from 'next'
import textToSpeech from '@google-cloud/text-to-speech'
import { google } from '@google-cloud/text-to-speech/build/protos/protos'

type Data = {
  audio?: string | Uint8Array // Base64 encoded string or Uint8Array
  error?: string
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  const message = req.body.message
  const ttsType = req.body.ttsType
  const languageCode = req.body.languageCode || 'ja-JP'

  try {
    // Check if GOOGLE_TTS_KEY exists
    if (process.env.GOOGLE_TTS_KEY) {
      // Use API Key based authentication
      const response = await fetch(
        `https://texttospeech.googleapis.com/v1/text:synthesize?key=${process.env.GOOGLE_TTS_KEY}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            input: { text: message },
            voice: { languageCode: languageCode, name: ttsType },
            audioConfig: { audioEncoding: 'MP3' },
          }),
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(errorData)}`)
      }

      const data = await response.json()
      res.status(200).json({ audio: data.audioContent })
    } else {
      // 检查是否有服务账号凭据文件路径
      const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS
      
      if (!credentialsPath) {
        // 没有配置任何认证方式，返回友好错误
        console.warn('⚠️ Google TTS 未配置：需要设置 GOOGLE_TTS_KEY 或 GOOGLE_APPLICATION_CREDENTIALS')
        return res.status(400).json({ 
          error: 'Google TTS 未配置。请设置环境变量 GOOGLE_TTS_KEY 或 GOOGLE_APPLICATION_CREDENTIALS。详情请参考 env.template 文件。' 
        })
      }

      // Use credentials based authentication
      const client = new textToSpeech.TextToSpeechClient()

      const request: google.cloud.texttospeech.v1.ISynthesizeSpeechRequest = {
        input: { text: message },
        voice: { languageCode: languageCode, name: ttsType },
        audioConfig: { audioEncoding: 'MP3' },
      }

      const [response] = await client.synthesizeSpeech(request)
      const audio = response.audioContent

      // Convert Uint8Array to Base64 if needed
      const audioContent = Buffer.from(audio as Uint8Array).toString('base64')

      res.status(200).json({ audio: audioContent })
    }
  } catch (error: any) {
    console.error('Error in Google Text-to-Speech:', error)
    
    // 提供更友好的错误信息
    let errorMessage = 'Google TTS 服务错误'
    if (error?.message?.includes('Could not load the default credentials')) {
      errorMessage = 'Google TTS 凭据未配置。请设置 GOOGLE_TTS_KEY 环境变量或配置服务账号凭据。'
    } else if (error?.message) {
      errorMessage = error.message
    }
    
    res.status(500).json({ error: errorMessage })
  }
}
