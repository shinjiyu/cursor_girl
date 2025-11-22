import { app, BrowserWindow, screen, Menu, Tray, ipcMain } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import isDev from 'electron-is-dev'
import waitOn from 'wait-on'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

let mainWindow
let tray

// 悬浮窗配置
const WINDOW_CONFIG = {
  width: 400,        // 窗口宽度
  height: 600,       // 窗口高度
  minWidth: 300,     // 最小宽度
  minHeight: 400,    // 最小高度
}

async function createAssistantWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize
  
  // 计算初始位置（右下角）
  const x = width - WINDOW_CONFIG.width - 50
  const y = height - WINDOW_CONFIG.height - 50

  mainWindow = new BrowserWindow({
    width: WINDOW_CONFIG.width,
    height: WINDOW_CONFIG.height,
    minWidth: WINDOW_CONFIG.minWidth,
    minHeight: WINDOW_CONFIG.minHeight,
    x: x,
    y: y,
    show: false,
    
    // 透明悬浮窗关键配置
    transparent: true,           // 背景透明
    frame: false,                // 无边框
    alwaysOnTop: true,           // 始终置顶
    skipTaskbar: true,           // 不显示在任务栏
    hasShadow: false,            // 无阴影
    resizable: true,             // 允许调整大小
    
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,        // 避免 CORS 错误
      preload: path.join(__dirname, 'preload-assistant.js'),
      devTools: isDev,           // 仅开发模式显示开发者工具
    },
  })

  if (isDev) {
    // 开发模式：等待本地服务器
    await waitOn({ resources: ['http://localhost:3000'] })
    // 加载助手页面（我们会创建一个专门的页面）
    mainWindow.loadURL('http://localhost:3000/assistant')
  } else {
    // 生产模式
    mainWindow.loadFile(path.join(__dirname, 'out', 'assistant.html'))
  }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    if (isDev) {
      mainWindow.webContents.openDevTools({ mode: 'detach' })
    }
  })

  // 窗口关闭时的处理
  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 创建系统托盘
function createTray() {
  // 使用一个图标文件（你可以替换为自己的图标）
  const iconPath = path.join(__dirname, 'public', 'favicon.ico')
  
  try {
    tray = new Tray(iconPath)
    
    const contextMenu = Menu.buildFromTemplate([
      {
        label: '显示/隐藏',
        click: () => {
          if (mainWindow) {
            if (mainWindow.isVisible()) {
              mainWindow.hide()
            } else {
              mainWindow.show()
            }
          }
        }
      },
      {
        label: '始终置顶',
        type: 'checkbox',
        checked: true,
        click: (menuItem) => {
          if (mainWindow) {
            mainWindow.setAlwaysOnTop(menuItem.checked)
          }
        }
      },
      { type: 'separator' },
      {
        label: '设置',
        click: () => {
          // 打开设置窗口
          if (mainWindow) {
            mainWindow.webContents.send('open-settings')
          }
        }
      },
      {
        label: '重新加载',
        click: () => {
          if (mainWindow) {
            mainWindow.reload()
          }
        }
      },
      { type: 'separator' },
      {
        label: '退出',
        click: () => {
          app.quit()
        }
      }
    ])
    
    tray.setToolTip('オルテンシア编程助手')
    tray.setContextMenu(contextMenu)
    
    // 双击托盘图标显示窗口
    tray.on('double-click', () => {
      if (mainWindow) {
        mainWindow.show()
      }
    })
  } catch (error) {
    console.log('Tray creation skipped:', error.message)
  }
}

// 应用就绪时创建窗口
app.on('ready', async () => {
  await createAssistantWindow()
  createTray()
})

// 所有窗口关闭时的行为（macOS 特殊处理）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// macOS 激活时重新创建窗口
app.on('activate', () => {
  if (mainWindow === null) {
    createAssistantWindow()
  }
})

// 防止应用退出时关闭所有窗口
app.on('before-quit', () => {
  if (mainWindow) {
    mainWindow.removeAllListeners('close')
  }
})

// IPC 通信处理
ipcMain.on('minimize-to-tray', () => {
  if (mainWindow) {
    mainWindow.hide()
  }
})

ipcMain.on('set-window-size', (event, width, height) => {
  if (mainWindow) {
    mainWindow.setSize(width, height)
  }
})

ipcMain.on('toggle-always-on-top', (event, alwaysOnTop) => {
  if (mainWindow) {
    mainWindow.setAlwaysOnTop(alwaysOnTop)
  }
})

