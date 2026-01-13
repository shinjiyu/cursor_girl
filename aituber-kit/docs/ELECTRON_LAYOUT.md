# Electron 版本布局优化说明

## 问题描述

在 Electron 打包版本中，由于使用了透明窗口（`transparent: true`）和无边框（`frame: false`），可能导致以下布局问题：

1. **VRM 角色覆盖其他 UI 元素**
2. **窗口拖拽区域影响内容交互**
3. **z-index 层级问题**
4. **100vw/100vh 计算差异**

## 解决方案

### 1. Electron 环境检测

代码已添加 Electron 环境检测：

```typescript
const [isElectron, setIsElectron] = useState(false)

useEffect(() => {
  const checkElectron = () => {
    const hasElectronAPI = typeof window !== 'undefined' && (window as any).electronAPI
    const isElectronUserAgent = navigator.userAgent.toLowerCase().includes('electron')
    setIsElectron(hasElectronAPI || isElectronUserAgent)
  }
  checkElectron()
}, [])
```

### 2. 布局优化

#### 容器级别
- **背景色调整**：Electron 环境下使用更明显的背景色，避免内容被遮挡
- **WebkitAppRegion**：默认设置为 `no-drag`，只在特定区域允许拖拽

#### VRM 角色区域
- **拖拽区域**：仅在 Electron 桌面端允许拖拽（`WebkitAppRegion: 'drag'`）
- **z-index**：设置为 1，确保在正确层级
- **overflow**：设置为 `hidden`，防止内容溢出

#### 聊天区域
- **交互性**：明确设置为 `no-drag`，确保所有交互正常
- **z-index**：设置为 2，确保在 VRM 角色之上
- **背景**：使用半透明背景，在透明窗口中更清晰

### 3. 窗口控制按钮

窗口控制按钮（右上角）始终设置为 `no-drag`，确保按钮可点击。

## 布局结构

```
┌─────────────────────────────────────┐
│  Electron 透明窗口 (transparent)    │
│  ┌───────────────────────────────┐ │
│  │  容器 (100vw × 100vh)         │ │
│  │  WebkitAppRegion: no-drag     │ │
│  │  ┌──────────┬──────────────┐  │ │
│  │  │ VRM 区域 │  聊天区域    │  │ │
│  │  │ (50%)    │  (50%)       │  │ │
│  │  │ drag     │  no-drag     │  │ │
│  │  │ z: 1     │  z: 2        │  │ │
│  │  └──────────┴──────────────┘  │ │
│  │  ┌──────────────────────────┐ │ │
│  │  │  窗口控制按钮 (右上角)   │ │ │
│  │  │  no-drag, z: 9999       │ │ │
│  │  └──────────────────────────┘ │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 移动端适配

在移动端（`isMobile === true`）：
- 布局切换为垂直方向（`flexDirection: 'column'`）
- VRM 区域占 40% 高度
- 聊天区域占 60% 高度
- 所有区域都设置为 `no-drag`（移动端不支持窗口拖拽）

## 测试建议

### 1. Electron 开发模式测试

```bash
npm run assistant:dev
```

检查：
- [ ] VRM 角色正确显示，不遮挡聊天区域
- [ ] 可以通过 VRM 区域拖拽窗口
- [ ] 聊天区域可以正常交互（输入、滚动等）
- [ ] 窗口控制按钮可以点击

### 2. Electron 打包版本测试

```bash
npm run build:electron
# 运行打包后的应用
```

检查：
- [ ] 静态文件加载正常
- [ ] 布局与开发模式一致
- [ ] 透明窗口效果正常
- [ ] 所有交互功能正常

### 3. Web 浏览器测试

```bash
npm run dev
# 在浏览器中访问 http://localhost:3000/assistant
```

检查：
- [ ] 布局正常（不依赖 Electron 特性）
- [ ] 响应式设计正常
- [ ] 移动端访问正常

## 常见问题

### Q: VRM 角色覆盖了聊天内容

**A:** 检查：
1. `z-index` 是否正确设置（聊天区域应该更高）
2. `overflow: hidden` 是否设置
3. 容器宽度是否正确（应该是 50% 而不是 100%）

### Q: 无法拖拽窗口

**A:** 检查：
1. `isElectron` 是否正确检测
2. VRM 区域的 `WebkitAppRegion` 是否设置为 `drag`
3. 其他区域是否设置为 `no-drag`

### Q: 聊天区域无法交互

**A:** 检查：
1. `WebkitAppRegion` 是否设置为 `no-drag`
2. `z-index` 是否足够高
3. `pointerEvents` 是否设置为 `auto`

## 相关文件

- `src/pages/assistant.tsx` - 主页面组件
- `electron-assistant.mjs` - Electron 主进程配置
- `preload-assistant.js` - Electron 预加载脚本
