import { useEffect, useState, useCallback, useRef } from 'react'
import { useTranslation } from 'react-i18next'

import homeStore from '@/features/stores/home'
import settingsStore from '@/features/stores/settings'
import { EmotionType } from '@/features/messages/messages'
import { OrtensiaClient, MessageType, OrtensiaMessage } from '@/utils/OrtensiaClient'

///取得したコメントをストックするリストの作成（receivedMessages）
interface TmpMessage {
  text: string
  role: string
  emotion: EmotionType
  type: string
  audio_file?: string  // TTS 音频文件路径
  conversation_id?: string  // 对话ID（新增）
}

interface Params {
  handleReceiveTextFromWs: (
    text: string,
    role?: string,
    emotion?: EmotionType,
    type?: string,
    audio_file?: string,  // TTS 音频文件路径
    conversation_id?: string  // 对话ID（新增）
  ) => Promise<void>
}

const useExternalLinkage = ({ handleReceiveTextFromWs }: Params) => {
  const { t } = useTranslation()
  const externalLinkageMode = settingsStore((s) => s.externalLinkageMode)
  const ortensiaClientRef = useRef<OrtensiaClient | null>(null)
  const handleReceiveRef = useRef(handleReceiveTextFromWs)
  
  // 保持 ref 更新
  useEffect(() => {
    handleReceiveRef.current = handleReceiveTextFromWs
  }, [handleReceiveTextFromWs])

  useEffect(() => {
    const ss = settingsStore.getState()
    if (!ss.externalLinkageMode) return

    // 🎛️  使用 OrtensiaManager 获取客户端
    const OrtensiaManager = require('@/utils/OrtensiaManager').default
    const manager = OrtensiaManager
    
    // 确保管理器已初始化
    manager.initialize()
    
    const client = manager.getClient()
    if (!client) {
      console.error('❌ [useExternalLinkage] OrtensiaClient 未初始化')
      return
    }
    ortensiaClientRef.current = client

    // 注册消息处理器 - 直接处理消息，不使用状态队列
    const handler = async (msg: OrtensiaMessage) => {
      console.log('📨 [Ortensia] 收到文本消息:', msg.payload)
      
      const tmpMessage: TmpMessage = {
        text: msg.payload.text || '',
        role: msg.payload.role || 'assistant',
        emotion: (msg.payload.emotion || 'neutral') as EmotionType,
        type: msg.payload.type || 'text',
        audio_file: msg.payload.audio_file,
        conversation_id: msg.payload.conversation_id,  // 提取 conversation_id
      }
      
      console.log('🟢 [useExternalLinkage] Processing message:', {
        text: tmpMessage.text,
        role: tmpMessage.role,
        emotion: tmpMessage.emotion,
        type: tmpMessage.type,
        audio_file: tmpMessage.audio_file,
        conversation_id: tmpMessage.conversation_id
      })
      
      // 转换角色名称
      let processedRole = tmpMessage.role
      if (
        tmpMessage.role === 'output' ||
        tmpMessage.role === 'executing' ||
        tmpMessage.role === 'console'
      ) {
        processedRole = 'code'
      }
      
      // 直接处理消息，避免状态更新死循环
      await handleReceiveRef.current(
        tmpMessage.text,
        processedRole,
        tmpMessage.emotion,
        tmpMessage.type,
        tmpMessage.audio_file,
        tmpMessage.conversation_id
      )
    }
    
    client.on(MessageType.AITUBER_RECEIVE_TEXT, handler)

    // 连接到中央服务器（如果还没连接）
    if (!client.isConnected()) {
      client.connect('ws://localhost:8765')
      .then(() => {
        console.log('✅ [Ortensia] 连接成功')
        homeStore.setState({ chatProcessing: false })
        // 🆕 discoverExistingConversations 现在在 register_ack 后自动调用（OrtensiaClient 内部处理）
      })
      .catch((error) => {
        console.error('❌ [Ortensia] 连接失败:', error)
      })
    }

    // 重连逻辑
    const reconnectInterval = setInterval(() => {
      const ss = settingsStore.getState()
      if (ss.externalLinkageMode && client && !client.isConnected()) {
        console.log('🔄 [Ortensia] 尝试重连...')
        homeStore.setState({ chatProcessing: false })
        
        client.connect('ws://localhost:8765')
          .then(() => {
            console.log('✅ [Ortensia] 重连成功')
            // 🆕 重连后也要重新发现对话
            setTimeout(() => {
              client.discoverExistingConversations()
            }, 1000)
          })
          .catch((error) => console.error('❌ [Ortensia] 重连失败:', error))
      }
    }, 5000)

    return () => {
      console.log('🔌 [useExternalLinkage] Cleanup: 移除消息处理器')
      clearInterval(reconnectInterval)
      if (client) {
        client.off(MessageType.AITUBER_RECEIVE_TEXT)
        // 注意：不要在这里 disconnect，因为其他组件可能还在使用
      }
    }
  }, [externalLinkageMode])

  return null
}

export default useExternalLinkage
