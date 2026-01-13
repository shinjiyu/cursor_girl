# Electron 打包和部署指南

## 概述

本指南说明如何打包 Electron 应用，以及如何确保 Web/移动端访问正常。

## Electron 打包

### 前置要求

1. **安装 electron-builder**
   ```bash
   npm install --save-dev electron-builder
   ```

2. **准备图标文件**（可选）
   - macOS: `build/icon.icns`
   - Windows: `build/icon.ico`
   - Linux: `build/icon.png`

### 打包命令

```bash
# 完整打包流程（构建静态文件 + 打包 Electron）
npm run build:electron

# 仅构建静态文件
npm run build:static

# 仅打包 Electron（需要先运行 build:static）
npm run pack:electron

# 平台特定打包
npm run pack:electron:mac      # macOS
npm run pack:electron:win       # Windows
npm run pack:electron:linux     # Linux
```

### 打包输出

打包后的文件位于 `dist/` 目录：

- **macOS**: `dist/Ortensia AITuber-x.x.x.dmg`
- **Windows**: `dist/Ortensia AITuber Setup x.x.x.exe`
- **Linux**: `dist/Ortensia AITuber-x.x.x.AppImage`

## 打包模式说明

### 模式 1: 静态文件模式（推荐用于分发）

**特点：**
- 不依赖本地 Next.js 服务器
- 应用体积较大（包含所有静态资源）
- 适合独立分发

**流程：**
1. `next build && next export` - 生成静态 HTML 文件
2. Electron 加载 `out/assistant.html`（file:// 协议）

**限制：**
- API 路由不可用（静态导出不支持）
- 需要将所有功能改为客户端实现或使用外部服务

### 模式 2: 本地服务器模式（推荐用于开发/测试）

**特点：**
- 需要运行 Next.js 服务器
- 功能完整（API 路由可用）
- 适合开发环境或用户自行部署

**流程：**
1. 用户启动应用
2. Electron 尝试加载静态文件，失败则回退到 `http://localhost:3000`
3. 需要用户手动启动 Next.js 服务器，或 Electron 自动启动

**实现：**
- 可以在 Electron 主进程中启动 Next.js 服务器
- 或提示用户先启动服务器

## Web/移动端访问

### 确保响应式设计

应用已包含移动端适配：

1. **Viewport Meta 标签**（`_document.tsx`）
   ```tsx
   <meta
     name="viewport"
     content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover"
   />
   ```

2. **移动端检测 Hook**（`useIsMobile`）
   - 检测屏幕宽度 <= 768px
   - 检测 User-Agent 中的移动设备标识

3. **响应式 CSS**（Tailwind CSS）
   - 使用 `md:`, `lg:` 等断点
   - 移动端自动调整布局

### 测试移动端访问

1. **本地测试**
   ```bash
   # 启动开发服务器
   npm run dev
   
   # 在移动设备上访问
   # http://your-local-ip:3000/assistant
   ```

2. **生产环境测试**
   ```bash
   # 构建并启动生产服务器
   npm run build && npm start
   
   # 在移动设备上访问
   # http://your-server-ip:3000/assistant
   ```

3. **浏览器开发者工具**
   - Chrome DevTools: 设备模拟器
   - 测试不同屏幕尺寸

### 移动端优化建议

1. **触摸交互**
   - 禁用拖拽（移动端已实现）
   - 增大点击区域
   - 支持手势操作

2. **性能优化**
   - 减少 VRM 模型复杂度（移动端）
   - 使用 WebGL 降级方案
   - 懒加载非关键资源

3. **布局调整**
   - 移动端使用垂直布局
   - 隐藏非必要元素
   - 优化字体大小

## 多终端/多设备访问

### 架构支持

系统已支持多终端访问：

1. **中央服务器协调**
   - 所有客户端连接到同一个中央服务器
   - 会话状态在服务器端管理
   - 事件广播到所有连接的客户端

2. **会话一致性**
   - 使用 `session_id` 标识会话
   - 所有设备共享同一会话状态
   - 输入仲裁确保顺序一致性

### 配置要点

1. **中央服务器地址**
   ```bash
   # 环境变量
   NEXT_PUBLIC_ORTENSIA_SERVER=wss://your-server.trycloudflare.com/
   ```

2. **跨设备访问**
   - PC: Electron 应用或浏览器
   - 手机: 浏览器访问 `http://server:3000/assistant`
   - 平板: 浏览器访问

3. **网络配置**
   - 确保中央服务器可从所有设备访问
   - 使用 HTTPS/WSS（生产环境）
   - 配置防火墙规则

### 测试多设备场景

1. **PC + 手机同时访问**
   ```bash
   # PC: Electron 应用
   # 手机: 浏览器访问 http://server:3000/assistant
   
   # 验证：
   # - 两个设备都能连接中央服务器
   # - 消息同步显示
   # - 输入不会冲突
   ```

2. **多浏览器标签页**
   ```bash
   # 打开多个标签页访问同一页面
   # 验证会话一致性
   ```

## 部署检查清单

### Electron 打包前

- [ ] 更新版本号（`package.json`）
- [ ] 准备图标文件
- [ ] 测试静态导出（`npm run build:static`）
- [ ] 检查 `out/` 目录内容
- [ ] 测试 Electron 加载静态文件

### Web/移动端部署前

- [ ] 配置 `NEXT_PUBLIC_ORTENSIA_SERVER`
- [ ] 测试响应式布局
- [ ] 测试移动端触摸交互
- [ ] 检查 viewport meta 标签
- [ ] 测试不同浏览器兼容性

### 多终端部署前

- [ ] 中央服务器可访问
- [ ] 配置正确的 WebSocket 地址
- [ ] 测试多设备连接
- [ ] 验证会话同步
- [ ] 检查输入仲裁

## 常见问题

### Q: Electron 打包后无法加载页面

**A:** 检查：
1. `out/assistant.html` 是否存在
2. 文件路径是否正确（`electron-assistant.mjs`）
3. 静态资源路径是否正确（使用相对路径）

### Q: 移动端显示异常

**A:** 检查：
1. Viewport meta 标签
2. CSS 响应式断点
3. 移动端检测逻辑
4. 浏览器兼容性

### Q: 多设备无法同步

**A:** 检查：
1. 中央服务器地址配置
2. WebSocket 连接状态
3. 会话 ID 是否一致
4. 网络连接是否正常

## 相关文档

- [架构说明](./docs/ARCHITECTURE.md)
- [Docker 部署](./DOCKER.md)
- [中央服务器配置](../bridge/README.md)
