import { useEffect, useState, useRef, useCallback } from 'react'
import dynamic from 'next/dynamic'
import homeStore from '@/features/stores/home'
import settingsStore from '@/features/stores/settings'
import { OrtensiaClient, MessageType, type OrtensiaMessage } from '@/utils/OrtensiaClient'
import OrtensiaManager from '@/utils/OrtensiaManager'
import { resolveOrtensiaServerUrl } from '@/utils/resolveOrtensiaServerUrl'
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

// 🚀 目标 VRM 模型路径（オルテンシア）
const TARGET_VRM_PATH = '/vrm/ortensia.vrm'

/**
 * 透明悬浮窗助手页面
 * 只显示 VRM 角色，背景透明
 */
export default function AssistantPage() {
  const [isDragging, setIsDragging] = useState(false)
  const [showControls, setShowControls] = useState(false)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isMiniMode, setIsMiniMode] = useState(false)  // 🆕 迷你模式状态
  const [isMobile, setIsMobile] = useState(false)  // 🆕 移动端检测
  const [isElectron, setIsElectron] = useState(false)  // 🆕 Electron 环境检测
  const conversationStore = useConversationStore()
  const [autoChecker] = useState(() => new AutoTaskChecker())
  
  // ✅ 在组件渲染前设置目标模型路径（避免双重加载）
  // 这样 VrmViewer 初始化时就会直接使用目标模型
  if (typeof window !== 'undefined') {
    const currentPath = settingsStore.getState().selectedVrmPath
    if (currentPath !== TARGET_VRM_PATH) {
      console.log(`🎭 [Pre-init] 设置目标模型: ${currentPath} → ${TARGET_VRM_PATH}`)
      settingsStore.setState({ selectedVrmPath: TARGET_VRM_PATH })
    }
  }
  
  // 🆕 切换迷你模式
  const toggleMiniMode = useCallback(() => {
    const newMiniMode = !isMiniMode
    setIsMiniMode(newMiniMode)
    
    // 通知 Electron 切换窗口大小
    if (typeof window !== 'undefined') {
      const electronAPI = (window as any).electronAPI
      if (electronAPI && typeof electronAPI.toggleMiniMode === 'function') {
        electronAPI.toggleMiniMode(newMiniMode)
      } else {
        console.warn('⚠️ electronAPI.toggleMiniMode 不可用，请重启应用')
      }
    }
  }, [isMiniMode])

  useEffect(() => {
    console.log('🚀 Assistant page loaded')
    setIsLoaded(true)
    
    // 🎛️  使用 OrtensiaManager 统一管理
    const manager = OrtensiaManager
    manager.initialize()
    
    // 自动开启 WebSocket 外部连接模式（渲染由终端决定：文本/动作等）
    settingsStore.setState({
      externalLinkageMode: true,
      selectLanguage: 'ja',
    })
    console.log('✅ External linkage mode enabled')
    console.log(`✅ VRM 模型将直接使用: ${TARGET_VRM_PATH}（无需二次加载）`)

    // 启用外部连接模式
    settingsStore.setState({ externalLinkageMode: true })
    console.log('🔌 外部连接模式已启用')
    
    // 🔧 连接到中央服务器（WebSocketManager 也会连接，但这里确保连接）
    // 注意：WebSocketManager 使用 useExternalLinkage，它也会连接
    // 这里添加额外的连接检查，确保连接成功
    const checkAndConnect = () => {
      const client = manager.getClient()
      if (client) {
        if (!client.isConnected()) {
          void resolveOrtensiaServerUrl().then((ortensiaServer) => {
            console.log('🔌 [Assistant] 检测到未连接，尝试连接中央服务器:', ortensiaServer)
            client
              .connect(ortensiaServer)
              .then(() => {
                console.log('✅ [Assistant] 中央服务器连接成功')
              })
              .catch((error) => {
                console.error('❌ [Assistant] 中央服务器连接失败:', error)
              })
          })
        } else {
          console.log('✅ [Assistant] 中央服务器已连接')
        }
      } else {
        console.warn('⚠️ [Assistant] OrtensiaClient 未初始化，等待初始化...')
        // 延迟重试
        setTimeout(checkAndConnect, 500)
      }
    }
    
    // 延迟一下，确保 WebSocketManager 的 useExternalLinkage 先执行
    setTimeout(checkAndConnect, 1000)
  }, [])
  
  // 处理接收文本
  const handleAituberReceiveText = useCallback((message: OrtensiaMessage) => {
    const { text, emotion, audio_file, conversation_id, event_type, hook_name } = message.payload
    
    // 🆕 获取事件类型（优先使用 event_type，其次 hook_name）
    const msgEventType = event_type || hook_name
    
    console.log('✅ 处理消息:', text.substring(0, 50), `(event: ${msgEventType})`)
    
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
    
    // audio_file 为旧版字段：中央已去掉 TTS，端侧可自行实现渲染器
    if (audio_file) {
      console.log('ℹ️ [Assistant] 收到旧版 audio_file（已废弃）:', audio_file)
    }
    
    // 🔧 修复：检查是否应该停止（同时检查事件类型和关键词）
    const autoEnabled = conversationStore.getAutoCheckEnabled(convId)

    if (autoEnabled) {
      // 1) 频控熔断（避免无限循环扣费）
      const guard = autoChecker.canTriggerCheck(convId)
      if (!guard.ok && guard.shouldAutoStop) {
        console.log(`🛑 [Auto Check] ${convId.substring(0, 8)}: 触发频率熔断，自动停止`)
        conversationStore.setAutoCheckEnabled(convId, false)
        conversationStore.addMessage(convId, {
          role: 'system',
          content: '🛑 自动检查触发过于频繁，已自动停止以避免无限循环',
          timestamp: Date.now()
        })
        return
      }

      // 2) 只在收到“已结束/已完成”时停止（stop/afterAgentResponse 都可能出现）
      if (autoChecker.shouldStop(text, msgEventType)) {
        console.log(`[Auto Check] ${convId}: 命中停止关键词，自动检查已停止`)
        conversationStore.setAutoCheckEnabled(convId, false)
        conversationStore.addMessage(convId, {
          role: 'system',
          content: '✅ 所有任务已完成，自动检查已停止',
          timestamp: Date.now()
        })
        return
      }

      // 3) stop 事件：触发“继续检查”提示（而不是直接停止）
      if (msgEventType === 'stop') {
        // 再次确认频控（未通过则不发送）
        if (!guard.ok) {
          console.log(`⚠️  [Auto Check] ${convId.substring(0, 8)}: 防抖/频控未通过，跳过继续检查`)
          return
        }

        const checkPrompt = autoChecker.getCheckPrompt()
        console.log(`📤 [Auto Check] ${convId.substring(0, 8)}: stop 触发继续检查 "${checkPrompt}"`)

        conversationStore.addMessage(convId, {
          role: 'user',
          content: `[自动检查] ${checkPrompt}`,
          timestamp: Date.now()
        })

        const client = OrtensiaClient.getInstance()
        if (client) {
          client.sendCursorInputText(checkPrompt, convId, true)
        }

        autoChecker.recordCheck(convId)
      }
    }
  }, [conversationStore, autoChecker])
  
  // 处理 Agent 完成
  const handleAgentCompleted = useCallback((message: OrtensiaMessage) => {
    console.log('🎯 [Auto Check] ============ handleAgentCompleted 被调用 ============')
    console.log('🎯 [Auto Check] 完整消息:', JSON.stringify(message, null, 2))
    
    // 从 message.from 提取 conversation_id
    const hookId = message.from
    let convId = 'default'
    
    if (hookId.startsWith('hook-')) {
      convId = hookId.substring(5)
    }
    
    console.log(`🎯 [Auto Check] Hook ID: ${hookId}`)
    console.log(`🎯 [Auto Check] 提取的 Conversation ID: ${convId}`)
    
    // 打印所有对话的 ID 和状态
    const allConvs = Array.from(conversationStore.conversations.entries())
    console.log(`🎯 [Auto Check] 当前所有对话 (共 ${allConvs.length} 个):`)
    allConvs.forEach(([id, conv]) => {
      console.log(`  - ${id}: autoCheck=${conv.autoCheckEnabled}, title="${conv.title}"`)
    })
    
    // 🔧 使用短 ID 匹配（前 8 个字符）
    const shortConvId = convId.substring(0, 8)
    const matchedConv = allConvs.find(([id]) => id.startsWith(shortConvId))
    
    if (!matchedConv) {
      console.log(`⚠️  [Auto Check] 未找到匹配的对话: ${shortConvId}`)
      return
    }
    
    const [matchedId, conv] = matchedConv
    console.log(`✅ [Auto Check] 找到匹配: ${shortConvId} → ${matchedId}`)
    
    const autoEnabled = conversationStore.getAutoCheckEnabled(matchedId)
    console.log(`🎯 [Auto Check] 自动检查状态: ${autoEnabled}`)
    
    if (!autoEnabled) {
      console.log(`⚠️  [Auto Check] ${matchedId.substring(0, 8)}: 自动检查未启用`)
      return
    }
    
    const guard = autoChecker.canTriggerCheck(matchedId)
    console.log(`🎯 [Auto Check] 是否可以触发: ${guard.ok} (reason=${guard.reason || 'none'})`)
    
    if (!guard.ok) {
      if (guard.shouldAutoStop) {
        console.log(`🛑 [Auto Check] ${matchedId.substring(0, 8)}: 触发频率/次数熔断，自动停止`)
        conversationStore.setAutoCheckEnabled(matchedId, false)
        conversationStore.addMessage(matchedId, {
          role: 'system',
          content: '🛑 自动检查触发过于频繁，已自动停止以避免无限循环',
          timestamp: Date.now()
        })
      } else {
        console.log(`⚠️  [Auto Check] ${matchedId.substring(0, 8)}: 防抖检查未通过`)
      }
      return
    }
    
    console.log(`✅ [Auto Check] 将在 1 秒后发送检查提示`)
    
    // 延迟1秒后发送检查
    setTimeout(() => {
      const checkPrompt = autoChecker.getCheckPrompt()
      console.log(`📤 [Auto Check] ${matchedId.substring(0, 8)}: 发送检查提示 "${checkPrompt}"`)
      
      conversationStore.addMessage(matchedId, {
        role: 'user',
        content: `[自动检查] ${checkPrompt}`,
        timestamp: Date.now()
      })
      
      // 发送到对应的 Cursor（使用原始的 convId）
      const client = OrtensiaClient.getInstance()
      if (client) {
        client.sendCursorInputText(checkPrompt, convId, true)
      }
      
      autoChecker.recordCheck(matchedId)
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

  // 🎛️  使用 OrtensiaManager 统一管理消息订阅
  // 不再需要处理时序和竞争问题
  useEffect(() => {
    console.log('🔧 [Setup] 注册消息处理器到 OrtensiaManager')
    
    const manager = OrtensiaManager
    
    // 注册各类消息处理器
    const unsubscribe1 = manager.on(MessageType.AITUBER_RECEIVE_TEXT, (message) => {
      console.log('→ 调用 handleAituberReceiveText')
      handleAituberReceiveText(message)
    })
    
    const unsubscribe2 = manager.on(MessageType.AGENT_COMPLETED, (message) => {
      console.log('→ 调用 handleAgentCompleted')
      handleAgentCompleted(message)
    })
    
    const unsubscribe3 = manager.on(MessageType.GET_CONVERSATION_ID_RESULT, (message) => {
      console.log('→ 调用 handleConversationDiscovered')
      handleConversationDiscovered(message)
    })
    
    // 标记处理器已就绪，触发发现对话请求
    manager.markHandlersReady()
    console.log('✅ [Setup] 所有处理器已注册并标记为就绪')
    
    return () => {
      console.log('🔌 [Cleanup] 清理消息处理器')
      unsubscribe1()
      unsubscribe2()
      unsubscribe3()
    }
  }, [handleAituberReceiveText, handleAgentCompleted, handleConversationDiscovered])

  // Electron 环境检测
  useEffect(() => {
    const checkElectron = () => {
      // 检测是否在 Electron 环境中
      const hasElectronAPI = typeof window !== 'undefined' && (window as any).electronAPI
      const isElectronUserAgent = typeof navigator !== 'undefined' && 
        navigator.userAgent.toLowerCase().includes('electron')
      setIsElectron(hasElectronAPI || isElectronUserAgent)
    }
    checkElectron()
  }, [])

  // 移动端检测
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(
        window.innerWidth <= 768 ||
        /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
      )
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
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
        // Electron 透明窗口优化：使用更明显的背景，避免内容被遮挡
        background: isElectron ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 0, 0, 0.05)',
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',  // 移动端垂直布局
        // Electron 环境下的布局优化
        boxSizing: 'border-box',
        // 确保在 Electron 透明窗口中内容正确显示
        ...(isElectron && {
          WebkitAppRegion: 'no-drag',  // 默认不允许拖拽，特定区域才允许
          pointerEvents: 'auto',
        }),
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

      {/* WebSocket 管理器（始终加载） */}
      {isLoaded && <WebSocketManager />}

      {/* 正常模式内容 */}
      {!isMiniMode && (
        <>
          {/* VRM 角色显示区域（左侧/顶部） */}
          <div 
            style={{
              width: isMobile ? '100%' : '50%',  // 移动端全宽，桌面端50%
              height: isMobile ? '40%' : '100%',  // 移动端40%高度，桌面端全高
              position: 'relative',
              background: 'linear-gradient(135deg, rgba(10, 10, 20, 0.4) 0%, rgba(20, 10, 30, 0.5) 100%)',
              backdropFilter: 'blur(10px)',
              borderRight: isMobile ? 'none' : '2px solid rgba(157, 78, 221, 0.3)',
              borderBottom: isMobile ? '2px solid rgba(157, 78, 221, 0.3)' : 'none',
              boxShadow: isMobile 
                ? '0 2px 20px rgba(157, 78, 221, 0.2)' 
                : '2px 0 20px rgba(157, 78, 221, 0.2)',
              // Electron 环境：允许拖拽窗口（仅桌面端非移动端）
              // Web 环境：不允许拖拽
              WebkitAppRegion: (isElectron && !isMobile ? 'drag' : 'no-drag') as any,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              // Electron 环境下确保内容不被遮挡
              zIndex: isElectron ? 1 : 'auto',
              overflow: 'hidden',
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
        </>
      )}

      {/* 迷你模式：显示一个可爱的小图标 */}
      {isMiniMode ? (
        <div
          onClick={toggleMiniMode}
          style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            background: 'linear-gradient(135deg, rgba(157, 78, 221, 0.9) 0%, rgba(199, 125, 255, 0.9) 100%)',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(157, 78, 221, 0.5)',
            WebkitAppRegion: 'drag' as any,
            transition: 'all 0.3s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.05)'
            e.currentTarget.style.boxShadow = '0 6px 24px rgba(157, 78, 221, 0.7)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)'
            e.currentTarget.style.boxShadow = '0 4px 20px rgba(157, 78, 221, 0.5)'
          }}
        >
          <span style={{ 
            fontSize: '36px',
            WebkitAppRegion: 'no-drag' as any,
            filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))',
          }}>
            🌸
          </span>
        </div>
      ) : (
        /* 正常模式：窗口控制按钮（右上角固定显示） */
        <div 
          className="window-controls"
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            display: 'flex',
            gap: '6px',
            WebkitAppRegion: 'no-drag' as any,
            zIndex: 9999,
          }}
        >
          {/* 最小化成小图标按钮 */}
          <button
            title="缩小为图标"
            onClick={toggleMiniMode}
            style={{
              width: 28,
              height: 28,
              borderRadius: '8px',
              background: 'rgba(59, 130, 246, 0.8)',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              boxShadow: '0 2px 8px rgba(59, 130, 246, 0.4)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(96, 165, 250, 0.95)'
              e.currentTarget.style.transform = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.8)'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            🌸
          </button>

          {/* 关闭按钮 */}
          <button
            title="关闭窗口"
            onClick={() => {
              if (typeof window !== 'undefined') {
                window.close()
              }
            }}
            style={{
              width: 28,
              height: 28,
              borderRadius: '8px',
              background: 'rgba(239, 68, 68, 0.8)',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              boxShadow: '0 2px 8px rgba(239, 68, 68, 0.4)',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(248, 113, 113, 0.95)'
              e.currentTarget.style.transform = 'scale(1.1)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.8)'
              e.currentTarget.style.transform = 'scale(1)'
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* 正常模式：聊天UI和装饰元素 */}
      {!isMiniMode && (
        <>
          {/* 聊天区域（右侧/底部） */}
          <div 
            style={{
              width: isMobile ? '100%' : '50%',  // 移动端全宽，桌面端50%
              height: isMobile ? '60%' : '100%',  // 移动端60%高度，桌面端全高
              position: 'relative',  // 相对定位，作为 MultiConversationChat 的定位参考
              background: 'rgba(255, 255, 255, 0.02)',
              backdropFilter: 'blur(5px)',
              overflow: 'hidden',
              // Electron 环境：确保聊天区域可交互且不被遮挡
              WebkitAppRegion: 'no-drag' as any,
              zIndex: isElectron ? 2 : 'auto',
              boxSizing: 'border-box',  // 确保宽度计算正确
            }}
          >
            <MultiConversationChat />
          </div>

          {/* 中间分隔线装饰（仅桌面端） */}
          {!isMobile && (
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
          )}

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
        </>
      )}

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

