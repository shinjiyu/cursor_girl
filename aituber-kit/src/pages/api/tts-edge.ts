import type { NextApiRequest, NextApiResponse } from 'next'

type Data = {
  audio?: Buffer
  error?: string
}

/**
 * Edge TTS API
 * 使用 edge-tts Python 库作为后端
 * 
 * 注意：这个实现需要调用 Python 脚本
 * 或者使用 edge-tts-node npm 包
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
    voiceName = 'zh-CN-XiaoxiaoNeural',
    rate = '+0%',
    volume = '+0%',
    pitch = '+0Hz',
  } = req.body

  if (!text) {
    return res.status(400).json({ error: 'Missing text parameter' })
  }

  try {
    console.log('🎤 [Edge TTS API] Synthesizing:', text)

    // 方案 1: 调用 Python 脚本（推荐）
    // 使用 edge-tts Python 库
    const { exec } = require('child_process')
    const { promisify } = require('util')
    const execAsync = promisify(exec)
    const fs = require('fs')
    const path = require('path')
    const os = require('os')

    // 创建临时文件
    const tempFile = path.join(os.tmpdir(), `edge-tts-${Date.now()}.mp3`)

    // 构建 edge-tts 命令
    const command = `cd "${process.cwd()}/../bridge" && source venv/bin/activate && edge-tts --voice "${voiceName}" --rate="${rate}" --volume="${volume}" --pitch="${pitch}" --text "${text.replace(/"/g, '\\"')}" --write-media "${tempFile}"`

    console.log('🔧 [Edge TTS] Executing:', command)

    try {
      await execAsync(command, { timeout: 10000 })
      
      // 读取生成的音频文件
      const audioBuffer = fs.readFileSync(tempFile)
      
      // 删除临时文件
      fs.unlinkSync(tempFile)
      
      console.log(`✅ [Edge TTS] Success, size: ${audioBuffer.length} bytes`)
      
      // 返回音频数据
      res.setHeader('Content-Type', 'audio/mpeg')
      return res.send(audioBuffer)
    } catch (execError: any) {
      console.error('❌ [Edge TTS] Exec error:', execError)
      
      // 清理临时文件
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile)
      }
      
      throw execError
    }

  } catch (error: any) {
    console.error('❌ [Edge TTS API] Error:', error)
    return res.status(500).json({ 
      error: error.message || 'TTS synthesis failed' 
    })
  }
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '1mb',
    },
    responseLimit: '10mb',
  },
}


