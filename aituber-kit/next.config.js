/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  assetPrefix: process.env.BASE_PATH || '',
  basePath: process.env.BASE_PATH || '',
  trailingSlash: true,
  publicRuntimeConfig: {
    root: process.env.BASE_PATH || '',
  },
  optimizeFonts: false,
  // Docker 容器化支持：启用 standalone 输出模式
  output: process.env.NEXT_STANDALONE === 'true' ? 'standalone' : undefined,
  // Electron 打包支持：静态导出
  // 注意：如果使用静态导出，某些动态功能（如 API 路由）将不可用
  // 对于 Electron，可以考虑使用 file:// 协议加载静态文件，或继续使用本地服务器
}

module.exports = nextConfig
