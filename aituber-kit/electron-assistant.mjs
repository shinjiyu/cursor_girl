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
  width: 800,        // 窗口宽度（增加一倍）
  height: 600,       // 窗口高度
  minWidth: 600,     // 最小宽度
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
    
    // 半透明悬浮窗配置
    transparent: true,           // 背景透明
    frame: false,                // 无边框
    alwaysOnTop: true,           // 始终置顶
    skipTaskbar: false,          // 显示在任务栏（方便切换）
    hasShadow: true,             // 有阴影（增强视觉效果）
    resizable: true,             // 允许调整大小
    opacity: 0.95,               // 半透明效果
    
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
    // 加载助手页面
    mainWindow.loadURL('http://localhost:3000/assistant')
  } else {
    // 生产模式：优先尝试加载静态文件，失败则回退到本地服务器
    const staticPath = path.join(__dirname, 'out', 'assistant.html')
    const fs = await import('fs')
    
    if (fs.existsSync(staticPath)) {
      // 静态文件存在，使用 file:// 协议加载
      mainWindow.loadFile(staticPath)
    } else {
      // 静态文件不存在，尝试启动本地服务器或使用远程服务器
      console.warn('⚠️ 静态文件不存在，尝试加载本地服务器...')
      try {
        await waitOn({ resources: ['http://localhost:3000'], timeout: 5000 })
        mainWindow.loadURL('http://localhost:3000/assistant')
      } catch (error) {
        console.error('❌ 无法连接到本地服务器，请确保 Next.js 服务器正在运行')
        // 可以显示错误页面或提示用户
        mainWindow.loadURL('data:text/html,<h1>应用启动失败</h1><p>请确保 Next.js 服务器正在运行</p>')
      }
    }
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
  // macOS 需要使用 PNG 格式，Windows 使用 ICO
  const iconName = process.platform === 'darwin' 
    ? 'images/setting-icons/logo2-2favicon.svg'  // macOS 使用 SVG/PNG
    : 'favicon.ico'
  const iconPath = path.join(__dirname, 'public', iconName)
  
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
    
    // 单击托盘图标显示/隐藏窗口（更方便）
    tray.on('click', () => {
      if (mainWindow) {
        if (mainWindow.isVisible()) {
          mainWindow.hide()
        } else {
          mainWindow.show()
          mainWindow.focus()
        }
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

// 保存窗口状态（用于最小化/恢复）
let savedWindowState = {
  width: WINDOW_CONFIG.width,
  height: WINDOW_CONFIG.height,
  x: 0,
  y: 0,
}

// 迷你模式配置
const MINI_CONFIG = {
  width: 80,
  height: 80,
}

// IPC 通信处理
ipcMain.on('minimize-to-tray', () => {
  if (mainWindow) {
    mainWindow.hide()
  }
})

// 🆕 切换到迷你模式（小图标浮窗）
ipcMain.on('toggle-mini-mode', (event, isMini) => {
  if (mainWindow) {
    if (isMini) {
      // 保存当前窗口状态
      const bounds = mainWindow.getBounds()
      savedWindowState = {
        width: bounds.width,
        height: bounds.height,
        x: bounds.x,
        y: bounds.y,
      }
      
      // 获取屏幕尺寸，将迷你窗口放到右下角
      const { width, height } = screen.getPrimaryDisplay().workAreaSize
      
      // 切换到迷你模式
      mainWindow.setMinimumSize(MINI_CONFIG.width, MINI_CONFIG.height)
      mainWindow.setSize(MINI_CONFIG.width, MINI_CONFIG.height)
      mainWindow.setPosition(width - MINI_CONFIG.width - 20, height - MINI_CONFIG.height - 20)
      mainWindow.setResizable(false)
    } else {
      // 恢复正常模式
      mainWindow.setMinimumSize(WINDOW_CONFIG.minWidth, WINDOW_CONFIG.minHeight)
      mainWindow.setSize(savedWindowState.width, savedWindowState.height)
      mainWindow.setPosition(savedWindowState.x, savedWindowState.y)
      mainWindow.setResizable(true)
    }
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

