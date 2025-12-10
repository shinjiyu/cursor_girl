const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 最小化到托盘
  minimizeToTray: () => {
    ipcRenderer.send('minimize-to-tray')
  },
  
  // 🆕 切换迷你模式（小图标浮窗）
  toggleMiniMode: (isMini) => {
    ipcRenderer.send('toggle-mini-mode', isMini)
  },
  
  // 设置窗口大小
  setWindowSize: (width, height) => {
    ipcRenderer.send('set-window-size', width, height)
  },
  
  // 切换始终置顶
  toggleAlwaysOnTop: (alwaysOnTop) => {
    ipcRenderer.send('toggle-always-on-top', alwaysOnTop)
  },
  
  // 监听设置打开事件
  onOpenSettings: (callback) => {
    ipcRenderer.on('open-settings', callback)
  },
})

