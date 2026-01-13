const FALLBACK_ORTENSIA_SERVER =
  'wss://mazda-commissioners-organised-perceived.trycloudflare.com/'

/**
 * 运行时解析中央服务器地址（用于“本地配置文件”场景）。
 *
 * 优先级：
 * 1) NEXT_PUBLIC_ORTENSIA_SERVER（构建/运行时 env）
 * 2) /api/ortensia-server（Node 侧读取 ~/Library/.../central_server.txt 等）
 * 3) fallback（保持旧行为）
 */
export async function resolveOrtensiaServerUrl(): Promise<string> {
  const envUrl = (process.env.NEXT_PUBLIC_ORTENSIA_SERVER || '').trim()
  if (envUrl) return envUrl

  // 只在浏览器侧请求 API（SSR 不做这一步）
  if (typeof window === 'undefined') return FALLBACK_ORTENSIA_SERVER

  try {
    const resp = await fetch('/api/ortensia-server', { method: 'GET' })
    if (!resp.ok) return FALLBACK_ORTENSIA_SERVER
    const data = (await resp.json()) as { url?: unknown }
    const url = typeof data?.url === 'string' ? data.url.trim() : ''
    return url || FALLBACK_ORTENSIA_SERVER
  } catch {
    return FALLBACK_ORTENSIA_SERVER
  }
}

