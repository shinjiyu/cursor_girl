import type { NextApiRequest, NextApiResponse } from 'next'
import CryptoJS from 'crypto-js'

type Data = {
  audio?: ArrayBuffer
  error?: string
}

/**
 * 科大讯飞 WebAPI TTS
 * 文档: https://www.xfyun.cn/doc/tts/online_tts/API.html
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<Data>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const {
    text,
    appId,
    apiKey,
    apiSecret,
    voiceName = 'xiaoyan',
    speed = 50,
    volume = 50,
    pitch = 50,
  } = req.body

  if (!text || !appId || !apiKey || !apiSecret) {
    return res.status(400).json({ error: 'Missing required parameters' })
  }

  try {
    console.log('🎤 [Xunfei API] Starting TTS synthesis...')

    // 构建 WebSocket URL（讯飞使用 WebSocket 协议）
    const wsUrl = createXunfeiWebSocketUrl(appId, apiKey, apiSecret)
    
    // 由于 Next.js API 不支持 WebSocket，这里使用 HTTP API
    // 讯飞也提供 HTTP API，但需要额外配置
    
    // 这里使用简化版本：调用讯飞的 HTTP API（如果有的话）
    // 或者返回错误提示用户使用客户端直连
    
    // 实际实现中，可以：
    // 1. 使用 node-fetch + ws 库在服务端建立 WebSocket 连接
    // 2. 或者让前端直接连接讯飞 WebSocket（需要暴露密钥）
    // 3. 或者使用讯飞的 HTTP API（如果开通）
    
    console.log('⚠️ [Xunfei API] WebSocket TTS requires client-side implementation')
    return res.status(501).json({ 
      error: 'Xunfei WebSocket TTS not implemented in server-side API. Use client-side implementation instead.' 
    })
    
  } catch (error: any) {
    console.error('❌ [Xunfei API] Error:', error)
    return res.status(500).json({ 
      error: error.message || 'TTS synthesis failed' 
    })
  }
}

/**
 * 生成讯飞 WebSocket 鉴权 URL
 */
function createXunfeiWebSocketUrl(
  appId: string,
  apiKey: string,
  apiSecret: string
): string {
  const host = 'tts-api.xfyun.cn'
  const path = '/v2/tts'
  const date = new Date().toUTCString()
  
  // 生成签名
  const signatureOrigin = `host: ${host}\ndate: ${date}\nGET ${path} HTTP/1.1`
  const signature = CryptoJS.HmacSHA256(signatureOrigin, apiSecret)
  const signatureBase64 = CryptoJS.enc.Base64.stringify(signature)
  
  // 生成 authorization
  const authorizationOrigin = `api_key="${apiKey}", algorithm="hmac-sha256", headers="host date request-line", signature="${signatureBase64}"`
  const authorization = Buffer.from(authorizationOrigin).toString('base64')
  
  // 构建 URL
  const url = `wss://${host}${path}?authorization=${authorization}&date=${encodeURIComponent(date)}&host=${host}`
  
  return url
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '1mb',
    },
  },
}


