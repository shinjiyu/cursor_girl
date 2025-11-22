import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import homeStore from '@/features/stores/home'
import settingsStore from '@/features/stores/settings'

// 动态导入组件，避免 SSR 问题
const VrmViewer = dynamic(
  () => import('@/components/vrmViewer'),
  { ssr: false }
)

const WebSocketManager = dynamic(
  () => import('@/components/websocketManager').then(mod => mod.WebSocketManager),
  { ssr: false }
)

/**
 * 透明悬浮窗助手页面
 * 只显示 VRM 角色，背景透明
 */
export default function AssistantPage() {
  const [isDragging, setIsDragging] = useState(false)
  const [showControls, setShowControls] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)

  useEffect(() => {
    console.log('🚀 Assistant page loaded')
    setIsLoaded(true)
    
    // 自动开启 WebSocket 外部连接模式（暂时禁用 TTS，仅显示动画）
    settingsStore.setState({
      externalLinkageMode: true,
      selectVoice: 'voicevox',  // 暂时使用 voicevox（会因为服务未启动而跳过，只播放动画）
      selectLanguage: 'ja',
    })
    console.log('✅ External linkage mode enabled (TTS disabled for testing)')
    
    // 自动加载オルテンシア模型 - 增强版本，带重试
    let retryCount = 0
    const maxRetries = 10
    
    const loadModel = async () => {
      const viewer = homeStore.getState().viewer
      console.log(`📦 尝试 ${retryCount + 1}/${maxRetries}: Viewer ${viewer ? 'exists' : 'not found'}`)
      
      if (viewer) {
        try {
          console.log('⏳ 开始加载 VRM 模型...')
          viewer.loadVrm('/vrm/ortensia.vrm')  // 注意：这是同步调用
          console.log('✅ オルテンシア模型已加载！')
        } catch (error) {
          console.error('❌ 模型加载失败:', error)
          // 尝试加载备用模型
          console.log('🔄 尝试加载备用模型...')
          try {
            viewer.loadVrm('/vrm/AvatarSample_A.vrm')
            console.log('✅ 备用模型加载成功')
          } catch (err) {
            console.error('❌ 备用模型也失败:', err)
          }
        }
      } else {
        retryCount++
        if (retryCount < maxRetries) {
          console.log(`⏳ 等待 viewer 初始化... (${retryCount}/${maxRetries})`)
          setTimeout(loadModel, 1000) // 每秒重试一次
        } else {
          console.error('❌ Viewer 初始化超时，请刷新页面')
        }
      }
    }

    // 延迟 3 秒开始加载
    setTimeout(loadModel, 3000)

    // 启用外部连接模式
    settingsStore.setState({ externalLinkageMode: true })
    console.log('🔌 外部连接模式已启用')
  }, [])

  // 鼠标悬停时显示控制按钮
  const handleMouseEnter = () => {
    setShowControls(true)
  }

  const handleMouseLeave = () => {
    if (!isDragging) {
      setShowControls(false)
    }
  }

  return (
    <div 
      className="assistant-container"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        width: '100vw',
        height: '100vh',
        position: 'relative',
        overflow: 'hidden',
        // 完全透明背景
        background: 'transparent',
      }}
    >
      {/* 调试信息 */}
      {/* 调试信息 - 生产环境可删除 */}
      {false && <div style={{
        position: 'absolute',
        top: 50,
        left: 50,
        color: 'white',
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '12px 16px',
        borderRadius: '12px',
        zIndex: 9999,
        fontSize: '14px',
        lineHeight: '1.6',
      }}>
        <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '8px' }}>
          🎨 オルテンシア助手
        </div>
        <div>✅ 页面加载: {isLoaded ? 'Yes' : 'No'}</div>
        <div>🎭 VRM 模型: ortensia.vrm (19MB)</div>
        <div>🔌 WebSocket: Ready</div>
      </div>}

      {/* WebSocket 管理器 */}
      {isLoaded && <WebSocketManager />}

      {/* VRM 角色显示区域 */}
      <div 
        style={{
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
          // 允许拖拽窗口
          WebkitAppRegion: 'drag' as any,
        }}
      >
        {isLoaded && <VrmViewer />}
      </div>

      {/* 浮动控制按钮（鼠标悬停时显示）- 暂时隐藏 */}
      {false && showControls && (
        <div 
          className="floating-controls"
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            display: 'flex',
            gap: '8px',
            // 禁止拖拽此区域
            WebkitAppRegion: 'no-drag',
            zIndex: 1000,
          }}
        >
          {/* 设置按钮 */}
          <button
            className="control-button"
            onClick={() => {
              // 打开设置（可以弹出一个小窗口）
              window.open('/', '_blank', 'width=800,height=600')
            }}
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'rgba(157, 78, 221, 0.9)',
              border: '2px solid rgba(199, 125, 255, 0.5)',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(157, 78, 221, 0.4)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(199, 125, 255, 0.9)'
              e.currentTarget.style.transform = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(157, 78, 221, 0.9)'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            ⚙️
          </button>

          {/* 最小化按钮 */}
          <button
            className="control-button"
            onClick={() => {
              if (typeof window !== 'undefined' && (window as any).electronAPI) {
                (window as any).electronAPI.minimizeToTray()
              }
            }}
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'rgba(157, 78, 221, 0.9)',
              border: '2px solid rgba(199, 125, 255, 0.5)',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(157, 78, 221, 0.4)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(199, 125, 255, 0.9)'
              e.currentTarget.style.transform = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(157, 78, 221, 0.9)'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            ➖
          </button>

          {/* 关闭按钮 */}
          <button
            className="control-button"
            onClick={() => {
              window.close()
            }}
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              background: 'rgba(239, 68, 68, 0.9)',
              border: '2px solid rgba(252, 165, 165, 0.5)',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(239, 68, 68, 0.4)',
              transition: 'all 0.3s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(252, 165, 165, 0.9)'
              e.currentTarget.style.transform = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.9)'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* 状态指示器（右下角）*/}
      <div
        style={{
          position: 'absolute',
          bottom: 10,
          right: 10,
          padding: '8px 12px',
          borderRadius: '12px',
          background: 'rgba(157, 78, 221, 0.8)',
          backdropFilter: 'blur(10px)',
          color: 'white',
          fontSize: '12px',
          fontWeight: 'bold',
          boxShadow: '0 4px 12px rgba(157, 78, 221, 0.4)',
          WebkitAppRegion: 'no-drag',
          opacity: showControls ? 1 : 0,
          transition: 'opacity 0.3s ease',
        }}
      >
        オルテンシア
      </div>

      {/* 全局样式 */}
      <style jsx global>{`
        body {
          background: transparent !important;
          margin: 0;
          padding: 0;
          overflow: hidden;
        }

        /* 隐藏滚动条 */
        ::-webkit-scrollbar {
          display: none;
        }

        /* 平滑动画 */
        * {
          transition: opacity 0.3s ease, transform 0.3s ease;
        }
      `}</style>
    </div>
  )
}

