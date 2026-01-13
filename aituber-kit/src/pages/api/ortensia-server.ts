import type { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import os from 'os'
import path from 'path'

type Data =
  | {
      url: string
      source: 'env' | 'file' | 'default'
      filePath?: string
    }
  | { error: string }

function readOrtensiaServerFromFile(): { url: string; filePath: string } | null {
  try {
    const home = os.homedir()
    const candidates = [
      // 1) macOS 推荐路径（与 injector/hooks 保持一致）
      path.join(home, 'Library', 'Application Support', 'Ortensia', 'central_server.txt'),
      // 2) 通用隐藏文件
      path.join(home, '.ortensia_server'),
      // 3) 通用 config 目录
      path.join(home, '.config', 'ortensia', 'central_server.txt'),
      // 4) 项目内（可选）
      path.join(process.cwd(), '.ortensia', 'central_server.txt'),
    ]

    for (const p of candidates) {
      try {
        if (!fs.existsSync(p)) continue
        const raw = fs.readFileSync(p, 'utf8')
        const url = (raw || '').trim()
        if (url) return { url, filePath: p }
      } catch {
        // ignore candidate read errors
      }
    }
  } catch {
    // ignore
  }

  return null
}

export default function handler(req: NextApiRequest, res: NextApiResponse<Data>) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method Not Allowed' })
    return
  }

  // 1) 仍然允许 env 覆盖（方便 Docker / 部署）
  const envUrl = (process.env.NEXT_PUBLIC_ORTENSIA_SERVER || '').trim()
  if (envUrl) {
    res.status(200).json({ url: envUrl, source: 'env' })
    return
  }

  // 2) 本地配置文件（你要的“本地配置”）
  const fileCfg = readOrtensiaServerFromFile()
  if (fileCfg?.url) {
    res.status(200).json({ url: fileCfg.url, source: 'file', filePath: fileCfg.filePath })
    return
  }

  // 3) 回退：保持当前前端的默认地址（避免无配置时行为变化）
  res.status(200).json({
    url: 'wss://mazda-commissioners-organised-perceived.trycloudflare.com/',
    source: 'default',
  })
}

