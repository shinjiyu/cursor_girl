import { useEffect, useState, useRef } from 'react'
import dynamic from 'next/dynamic'
import homeStore from '@/features/stores/home'
import settingsStore from '@/features/stores/settings'
import { OrtensiaClient } from '@/utils/OrtensiaClient'

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
  const [showChat, setShowChat] = useState(true) // 聊天窗口显示状态
  const [inputText, setInputText] = useState('') // 输入框文本
  const [chatLog, setChatLog] = useState<any[]>([]) // 本地聊天记录状态
  const chatLogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    console.log('🚀 Assistant page loaded')
    setIsLoaded(true)
    
    // 自动开启 WebSocket 外部连接模式 + macOS 系统 TTS
    settingsStore.setState({
      externalLinkageMode: true,
      selectVoice: 'google',  // 使用 macOS 系统 TTS（Google TTS API）
      selectLanguage: 'ja',
    })
    console.log('✅ External linkage mode enabled (TTS: macOS System)')
    
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
  
  // 订阅 homeStore 的 chatLog 变化
  useEffect(() => {
    // 初始化 chatLog
    setChatLog(homeStore.getState().chatLog)
    
    // 订阅 homeStore 的变化
    const unsubscribe = homeStore.subscribe((state) => {
      setChatLog(state.chatLog)
    })
    
    return () => unsubscribe()
  }, [])
  
  // 自动滚动到最新消息
  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight
    }
  }, [chatLog])

  // 鼠标悬停时显示控制按钮
  const handleMouseEnter = () => {
    setShowControls(true)
  }

  const handleMouseLeave = () => {
    if (!isDragging) {
      setShowControls(false)
    }
  }
  
  // 发送消息到 Cursor
  const handleSendMessage = () => {
    if (!inputText.trim()) return
    
    const text = inputText.trim()
    
    // 在本地聊天记录中添加用户消息
    homeStore.getState().upsertMessage({
      role: 'user',
      content: text,
    })
    
    // 获取当前 conversation_id
    const currentConversationId = homeStore.getState().currentConversationId
    
    // 通过 WebSocket 发送到 Cursor inject（默认执行）
    const client = OrtensiaClient.getInstance()
    if (client) {
      client.sendCursorInputText(text, currentConversationId, true)  // execute=true 表示立即执行
      console.log('⚡ [Assistant] 发送并执行命令到 Cursor:', text)
    } else {
      console.error('❌ [Assistant] OrtensiaClient 未初始化')
    }
    
    // 清空输入框
    setInputText('')
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

      {/* 聊天窗口（右侧）*/}
      <div
        style={{
          position: 'absolute',
          top: 0,
          right: showChat ? 0 : -350,
          width: 350,
          height: '100%',
          background: 'rgba(20, 20, 30, 0.95)',
          backdropFilter: 'blur(10px)',
          borderLeft: '1px solid rgba(157, 78, 221, 0.3)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'right 0.3s ease',
          zIndex: 500,
          WebkitAppRegion: 'no-drag',
        }}
      >
        {/* 聊天窗口头部 */}
        <div style={{
          padding: '12px 16px',
          background: 'rgba(157, 78, 221, 0.2)',
          borderBottom: '1px solid rgba(157, 78, 221, 0.3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span style={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>
            💬 Cursor 事件
          </span>
          <button
            onClick={() => setShowChat(false)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'rgba(255, 255, 255, 0.6)',
              cursor: 'pointer',
              fontSize: '16px',
              padding: '4px 8px',
            }}
          >
            ✕
          </button>
        </div>

        {/* 消息列表 */}
        <div
          ref={chatLogRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          {chatLog.map((msg, index) => {
            const isUser = msg.role === 'user'
            const isCode = msg.role === 'code'
            const content = typeof msg.content === 'string' ? msg.content : 
                           Array.isArray(msg.content) ? msg.content.find(c => c.type === 'text')?.text || '' : ''
            
            return (
              <div
                key={msg.id || index}
                style={{
                  padding: '8px 12px',
                  borderRadius: '8px',
                  background: isUser ? 'rgba(157, 78, 221, 0.2)' : 
                              isCode ? 'rgba(59, 130, 246, 0.2)' :
                              'rgba(255, 255, 255, 0.05)',
                  border: `1px solid ${isUser ? 'rgba(157, 78, 221, 0.3)' : 
                                       isCode ? 'rgba(59, 130, 246, 0.3)' :
                                       'rgba(255, 255, 255, 0.1)'}`,
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                }}
              >
                <div style={{
                  fontSize: '10px',
                  color: 'rgba(255, 255, 255, 0.5)',
                  marginBottom: '4px',
                }}>
                  {isUser ? '👤 User' : isCode ? '💻 Code' : '🤖 オルテンシア'}
                </div>
                <div style={{
                  color: 'white',
                  fontSize: '12px',
                  lineHeight: '1.4',
                  wordBreak: 'break-word',
                  whiteSpace: 'pre-wrap',
                }}>
                  {content.length > 200 ? content.slice(0, 200) + '...' : content}
                </div>
              </div>
            )
          })}
        </div>

        {/* 输入框 */}
        <div style={{
          padding: '12px',
          borderTop: '1px solid rgba(157, 78, 221, 0.3)',
          background: 'rgba(0, 0, 0, 0.3)',
        }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage()
                }
              }}
              placeholder="输入到 Cursor..."
              style={{
                flex: 1,
                padding: '8px 12px',
                borderRadius: '6px',
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(157, 78, 221, 0.3)',
                color: 'white',
                fontSize: '12px',
                outline: 'none',
              }}
            />
            <button
              onClick={handleSendMessage}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                background: 'rgba(157, 78, 221, 0.8)',
                border: 'none',
                color: 'white',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: 'bold',
              }}
            >
              发送
            </button>
          </div>
        </div>
      </div>

      {/* 聊天窗口开关按钮（右侧边缘）*/}
      {!showChat && (
        <button
          onClick={() => setShowChat(true)}
          style={{
            position: 'absolute',
            top: '50%',
            right: 10,
            transform: 'translateY(-50%)',
            width: 40,
            height: 80,
            borderRadius: '8px',
            background: 'rgba(157, 78, 221, 0.8)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(199, 125, 255, 0.5)',
            color: 'white',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            boxShadow: '0 4px 12px rgba(157, 78, 221, 0.4)',
            WebkitAppRegion: 'no-drag',
            zIndex: 500,
          }}
        >
          💬
        </button>
      )}

      {/* 状态指示器（右下角）*/}
      <div
        style={{
          position: 'absolute',
          bottom: 10,
          right: showChat ? 360 : 10,
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
          transition: 'right 0.3s ease, opacity 0.3s ease',
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

        /* 聊天窗口滚动条样式 */
        div[style*="overflowY: auto"]::-webkit-scrollbar {
          width: 6px;
        }

        div[style*="overflowY: auto"]::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }

        div[style*="overflowY: auto"]::-webkit-scrollbar-thumb {
          background: rgba(157, 78, 221, 0.5);
          border-radius: 3px;
        }

        div[style*="overflowY: auto"]::-webkit-scrollbar-thumb:hover {
          background: rgba(157, 78, 221, 0.8);
        }

        /* 其他元素隐藏滚动条 */
        body::-webkit-scrollbar {
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

