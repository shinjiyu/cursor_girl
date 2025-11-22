import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

/**
 * API 路由：提供 TTS 音频文件访问
 * 
 * 这个路由从 bridge/tts_output 目录提供音频文件
 */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { filename } = req.query

  if (!filename || typeof filename !== 'string') {
    return res.status(400).json({ error: 'Filename is required' })
  }

  try {
    // 构建音频文件路径（使用绝对路径）
    const projectRoot = path.resolve(process.cwd(), '..')
    const bridgePath = path.join(projectRoot, 'bridge', 'tts_output', filename)
    
    console.log('🎤 [TTS Audio API] Requesting file:', filename)
    console.log('🎤 [TTS Audio API] Process CWD:', process.cwd())
    console.log('🎤 [TTS Audio API] Project root:', projectRoot)
    console.log('🎤 [TTS Audio API] Full path:', bridgePath)

    // 检查文件是否存在
    if (!fs.existsSync(bridgePath)) {
      console.error('❌ [TTS Audio API] File not found:', bridgePath)
      return res.status(404).json({ error: 'Audio file not found' })
    }

    // 读取文件
    const fileBuffer = fs.readFileSync(bridgePath)
    
    // 根据文件扩展名设置 Content-Type
    const ext = path.extname(filename).toLowerCase()
    let contentType = 'audio/wav'  // 默认使用 WAV
    
    if (ext === '.wav') {
      contentType = 'audio/wav'
    } else if (ext === '.aiff' || ext === '.aif') {
      contentType = 'audio/aiff'
    } else if (ext === '.mp3') {
      contentType = 'audio/mpeg'
    } else if (ext === '.ogg') {
      contentType = 'audio/ogg'
    }

    console.log('✅ [TTS Audio API] Serving file:', filename, 'Type:', contentType, 'Size:', fileBuffer.length)

    // 设置响应头并返回文件
    res.setHeader('Content-Type', contentType)
    res.setHeader('Content-Length', fileBuffer.length)
    res.setHeader('Cache-Control', 'no-cache')  // 不缓存以便实时更新
    res.status(200).send(fileBuffer)
  } catch (error) {
    console.error('❌ [TTS Audio API] Error serving file:', error)
    res.status(500).json({ error: 'Failed to serve audio file' })
  }
}

