import { useEffect, useState, useRef, useCallback } from 'react'
import dynamic from 'next/dynamic'
import homeStore from '@/features/stores/home'
import settingsStore from '@/features/stores/settings'
import { OrtensiaClient, MessageType, type OrtensiaMessage } from '@/utils/OrtensiaClient'
import { useConversationStore } from '@/features/stores/conversationStore'
import { AutoTaskChecker } from '@/utils/AutoTaskChecker'
import { MultiConversationChat } from '@/components/MultiConversationChat'

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
  const conversationStore = useConversationStore()
  const [autoChecker] = useState(() => new AutoTaskChecker())

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
  
  // 处理接收文本
  const handleAituberReceiveText = useCallback((message: OrtensiaMessage) => {
    const { text, emotion, audio_file, conversation_id } = message.payload
    
    console.log('✅ 处理消息:', text.substring(0, 50))
    
    // 如果没有 conversation_id，使用默认值
    const convId = conversation_id || 'default'
    
    // 确保 conversation 存在
    conversationStore.getOrCreateConversation(convId)
    
    // 添加消息到对应的 conversation
    conversationStore.addMessage(convId, {
      role: 'assistant',
      content: text,
      timestamp: Date.now()
    })
    
    // 同时添加到 homeStore（保持向后兼容）
    homeStore.getState().upsertMessage({
      role: 'assistant',
      content: text,
    })
    
    // 播放音频（如果有）
    if (audio_file) {
      // 音频播放逻辑保持不变
      console.log('🎵 [Assistant] 播放音频:', audio_file)
    }
    
    // 检查是否包含停止关键词
    const autoEnabled = conversationStore.getAutoCheckEnabled(convId)
    if (autoEnabled && autoChecker.shouldStop(text)) {
      console.log(`[Auto Check] ${convId}: 检测到停止关键词`)
      conversationStore.setAutoCheckEnabled(convId, false)
      conversationStore.addMessage(convId, {
        role: 'system',
        content: '✅ 所有任务已完成，自动检查已停止',
        timestamp: Date.now()
      })
    }
  }, [conversationStore, autoChecker])
  
  // 处理 Agent 完成
  const handleAgentCompleted = useCallback((message: OrtensiaMessage) => {
    console.log('🎯 [Auto Check] handleAgentCompleted 被调用', message)
    
    // 从 message.from 提取 conversation_id
    const hookId = message.from
    let convId = 'default'
    
    if (hookId.startsWith('hook-')) {
      convId = hookId.substring(5)
    }
    
    console.log(`🎯 [Auto Check] Hook ID: ${hookId}`)
    console.log(`🎯 [Auto Check] Conversation ID: ${convId}`)
    
    const autoEnabled = conversationStore.getAutoCheckEnabled(convId)
    console.log(`🎯 [Auto Check] 自动检查状态: ${autoEnabled}`)
    
    if (!autoEnabled) {
      console.log(`⚠️  [Auto Check] ${convId.substring(0, 8)}: 自动检查未启用`)
      return
    }
    
    const canTrigger = autoChecker.canTriggerCheck(convId)
    console.log(`🎯 [Auto Check] 是否可以触发: ${canTrigger}`)
    
    if (!canTrigger) {
      console.log(`⚠️  [Auto Check] ${convId.substring(0, 8)}: 防抖检查未通过`)
      return
    }
    
    console.log(`✅ [Auto Check] 将在 1 秒后发送检查提示`)
    
    // 延迟1秒后发送检查
    setTimeout(() => {
      const checkPrompt = autoChecker.getCheckPrompt()
      console.log(`📤 [Auto Check] ${convId.substring(0, 8)}: 发送检查提示 "${checkPrompt}"`)
      
      conversationStore.addMessage(convId, {
        role: 'user',
        content: `[自动检查] ${checkPrompt}`,
        timestamp: Date.now()
      })
      
      // 发送到对应的 Cursor
      const client = OrtensiaClient.getInstance()
      if (client) {
        client.sendCursorInputText(checkPrompt, convId, true)
      }
      
      autoChecker.recordCheck(convId)
    }, 1000)
  }, [conversationStore, autoChecker])
  
  // 🆕 处理发现的对话
  const handleConversationDiscovered = useCallback((message: OrtensiaMessage) => {
    console.log('🔍 [Discovery] handleConversationDiscovered 被调用', message.payload)
    
    const { conversation_id, title, success } = message.payload
    
    if (!success || !conversation_id) {
      console.log('⚠️  [Discovery] 未找到有效的 conversation_id', { success, conversation_id })
      return
    }
    
    console.log(`🔍 [Discovery] 正在创建对话: ${title || conversation_id}`)
    
    // 创建对话 tab（如果不存在），使用服务器返回的标题
    const conv = conversationStore.getOrCreateConversation(conversation_id, title)
    console.log(`🔍 [Discovery] 对话已创建/获取:`, conv)
    
    // 如果已存在但标题不同，更新标题
    if (title && conv.title !== title) {
      console.log(`🔍 [Discovery] 更新标题: "${conv.title}" → "${title}"`)
      conversationStore.updateConversationTitle(conversation_id, title)
    }
    
    // 如果是新创建的对话，添加一条欢迎消息
    if (conv.messages.length === 0) {
      console.log(`🔍 [Discovery] 添加欢迎消息`)
      conversationStore.addMessage(conversation_id, {
        role: 'system',
        content: `✅ 已连接到 Cursor 对话: ${title || conversation_id.substring(0, 8)}`,
        timestamp: Date.now()
      })
    } else {
      console.log(`🔍 [Discovery] 对话已有 ${conv.messages.length} 条消息，跳过欢迎消息`)
    }
    
    console.log(`✅ [Discovery] 发现对话完成: ${title} (${conversation_id.substring(0, 8)})`)
  }, [conversationStore])

  // 🔧 使用 useRef 确保只订阅一次（防止 React Strict Mode 双重挂载）
  const isSubscribedRef = useRef(false)
  
  // 监听 Ortensia 消息（延迟等待 OrtensiaClient 初始化）
  useEffect(() => {
    console.log('🔧 [Setup] 准备设置消息订阅')
    
    // 🔒 如果已订阅，跳过
    if (isSubscribedRef.current) {
      console.log('⚠️  [Setup] 已经订阅过了，跳过重复订阅')
      return
    }
    
    let unsubscribe: (() => void) | null = null
    let retryCount = 0
    const maxRetries = 10
    
    const setupSubscription = () => {
      const client = OrtensiaClient.getInstance()
      
      if (!client) {
        retryCount++
        if (retryCount <= maxRetries) {
          console.log(`⏳ [Setup] OrtensiaClient 尚未初始化，${100}ms 后重试 (${retryCount}/${maxRetries})`)
          setTimeout(setupSubscription, 100)
        } else {
          console.error('❌ [Setup] OrtensiaClient 初始化超时')
        }
        return
      }
      
      console.log('✅ [Setup] OrtensiaClient 已找到，设置订阅')
      
      unsubscribe = client.subscribe((message: OrtensiaMessage) => {
        console.log('📬 [Subscribe] 收到消息类型:', message.type)
        
        // 处理 AITUBER_RECEIVE_TEXT
        if (message.type === MessageType.AITUBER_RECEIVE_TEXT) {
          console.log('→ 调用 handleAituberReceiveText')
          handleAituberReceiveText(message)
        }
        
        // 处理 AGENT_COMPLETED
        if (message.type === MessageType.AGENT_COMPLETED) {
          console.log('→ 调用 handleAgentCompleted')
          handleAgentCompleted(message)
        }
        
        // 🆕 处理 GET_CONVERSATION_ID_RESULT（发现已存在的对话）
        if (message.type === MessageType.GET_CONVERSATION_ID_RESULT) {
          console.log('→ 调用 handleConversationDiscovered')
          handleConversationDiscovered(message)
        }
      })
      
      isSubscribedRef.current = true
      console.log('✅ [Setup] 消息订阅已设置，标记为已订阅')
    }
    
    // 开始尝试设置订阅
    setupSubscription()
    
    return () => {
      console.log('🔌 [Cleanup] 取消消息订阅')
      if (unsubscribe) {
        unsubscribe()
      }
      // 注意：不要在 cleanup 中重置 isSubscribedRef，因为 Strict Mode 会导致这个问题
    }
  }, [handleAituberReceiveText, handleAgentCompleted, handleConversationDiscovered])

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
        background: 'rgba(0, 0, 0, 0.05)',  // 轻微背景色
        display: 'flex',
        flexDirection: 'row',
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

      {/* VRM 角色显示区域（左侧） */}
      <div 
        style={{
          width: '50%',  // 左侧占50%
          height: '100%',
          position: 'relative',
          background: 'linear-gradient(135deg, rgba(10, 10, 20, 0.4) 0%, rgba(20, 10, 30, 0.5) 100%)',
          backdropFilter: 'blur(10px)',
          borderRight: '2px solid rgba(157, 78, 221, 0.3)',
          boxShadow: '2px 0 20px rgba(157, 78, 221, 0.2)',
          // 允许拖拽窗口
          WebkitAppRegion: 'drag' as any,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {isLoaded && <VrmViewer />}
        
        {/* 左侧标题 */}
        <div style={{
          position: 'absolute',
          top: 16,
          left: 16,
          color: 'rgba(255, 255, 255, 0.8)',
          fontSize: '14px',
          fontWeight: 'bold',
          textShadow: '0 2px 8px rgba(0, 0, 0, 0.5)',
          WebkitAppRegion: 'no-drag',
        }}>
          🎭 オルテンシア
        </div>
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

      {/* 多窗口聊天UI（右侧固定显示） */}
      <MultiConversationChat />

      {/* 中间分隔线装饰 */}
      <div style={{
        position: 'absolute',
        left: '50%',
        top: 0,
        width: '2px',
        height: '100%',
        background: 'linear-gradient(180deg, rgba(157, 78, 221, 0) 0%, rgba(157, 78, 221, 0.5) 50%, rgba(157, 78, 221, 0) 100%)',
        pointerEvents: 'none',
        zIndex: 10,
      }} />

      {/* 状态指示器（左下角）*/}
      <div
        style={{
          position: 'absolute',
          bottom: 10,
          left: 10,
          padding: '8px 12px',
          borderRadius: '12px',
          background: 'rgba(157, 78, 221, 0.7)',
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

