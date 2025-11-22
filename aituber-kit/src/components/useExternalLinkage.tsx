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
  audio_file?: string  // TTS 音频文件路径（新增）
}

interface Params {
  handleReceiveTextFromWs: (
    text: string,
    role?: string,
    emotion?: EmotionType,
    type?: string,
    audio_file?: string  // TTS 音频文件路径（新增）
  ) => Promise<void>
}

const useExternalLinkage = ({ handleReceiveTextFromWs }: Params) => {
  const { t } = useTranslation()
  const externalLinkageMode = settingsStore((s) => s.externalLinkageMode)
  const [receivedMessages, setTmpMessages] = useState<TmpMessage[]>([])
  const ortensiaClientRef = useRef<OrtensiaClient | null>(null)

  const processMessage = useCallback(
    async (message: TmpMessage) => {
      console.log('🟢 [useExternalLinkage] Processing message:', {
        text: message.text,
        role: message.role,
        emotion: message.emotion,
        type: message.type,
        audio_file: message.audio_file
      })
      await handleReceiveTextFromWs(
        message.text,
        message.role,
        message.emotion,
        message.type,
        message.audio_file
      )
    },
    [handleReceiveTextFromWs]
  )

  useEffect(() => {
    if (receivedMessages.length > 0) {
      const message = receivedMessages[0]
      if (
        message.role === 'output' ||
        message.role === 'executing' ||
        message.role === 'console'
      ) {
        message.role = 'code'
      }
      setTmpMessages((prev) => prev.slice(1))
      processMessage(message)
    }
  }, [receivedMessages, processMessage])

  useEffect(() => {
    const ss = settingsStore.getState()
    if (!ss.externalLinkageMode) return

    // 创建 Ortensia 客户端
    const client = new OrtensiaClient()
    ortensiaClientRef.current = client

    // 注册消息处理器
    client.on(MessageType.AITUBER_RECEIVE_TEXT, (msg: OrtensiaMessage) => {
      console.log('📨 [Ortensia] 收到文本消息:', msg.payload)
      
      const tmpMessage: TmpMessage = {
        text: msg.payload.text || '',
        role: msg.payload.role || 'assistant',
        emotion: (msg.payload.emotion || 'neutral') as EmotionType,
        type: msg.payload.type || 'text',
        audio_file: msg.payload.audio_file,
      }
      
      setTmpMessages((prevMessages) => [...prevMessages, tmpMessage])
    })

    // 连接到中央服务器
    client.connect('ws://localhost:8765')
      .then(() => {
        console.log('✅ [Ortensia] 连接成功')
        homeStore.setState({ chatProcessing: false })
      })
      .catch((error) => {
        console.error('❌ [Ortensia] 连接失败:', error)
      })

    // 重连逻辑
    const reconnectInterval = setInterval(() => {
      const ss = settingsStore.getState()
      if (ss.externalLinkageMode && client && !client.isConnected()) {
        console.log('🔄 [Ortensia] 尝试重连...')
        homeStore.setState({ chatProcessing: false })
        
        client.connect('ws://localhost:8765')
          .then(() => console.log('✅ [Ortensia] 重连成功'))
          .catch((error) => console.error('❌ [Ortensia] 重连失败:', error))
      }
    }, 5000)

    return () => {
      clearInterval(reconnectInterval)
      if (client) {
        client.disconnect()
      }
    }
  }, [externalLinkageMode])

  return null
}

export default useExternalLinkage
