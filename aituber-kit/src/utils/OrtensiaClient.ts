/**
 * Ortensia 协议客户端
 * 
 * 用于与 Ortensia 中央服务器通信的 WebSocket 客户端
 * 实现了 Ortensia 协议的注册、心跳、消息格式等
 */

// ============================================================================
// 类型定义
// ============================================================================

export enum ClientType {
  CURSOR_HOOK = 'cursor_hook',
  COMMAND_CLIENT = 'command_client',
  AITUBER_CLIENT = 'aituber_client',
}

export enum MessageType {
  // 连接管理
  REGISTER = 'register',
  REGISTER_ACK = 'register_ack',
  HEARTBEAT = 'heartbeat',
  HEARTBEAT_ACK = 'heartbeat_ack',
  DISCONNECT = 'disconnect',
  
  // AITuber 专用消息
  AITUBER_SPEAK = 'aituber_speak',
  AITUBER_EMOTION = 'aituber_emotion',
  AITUBER_STATUS = 'aituber_status',
  AITUBER_RECEIVE_TEXT = 'aituber_receive_text',  // 接收文本消息（从 hooks）
  
  // Cursor 输入操作
  CURSOR_INPUT_TEXT = 'cursor_input_text',  // 向 Cursor 输入文本（不执行）
  CURSOR_INPUT_TEXT_RESULT = 'cursor_input_text_result',  // 输入文本结果

  // VNext: 多终端一致性（输入仲裁 / 事件流）
  INPUT_SUBMIT = 'input_submit',
  INPUT_ACK = 'input_ack',
  CLIENT_EVENT_SUBMIT = 'client_event_submit',
  SESSION_EVENT = 'session_event',
  
  // Conversation 发现
  GET_CONVERSATION_ID = 'get_conversation_id',  // 查询 conversation_id
  GET_CONVERSATION_ID_RESULT = 'get_conversation_id_result',  // conversation_id 查询结果
  
  // Agent 事件
  AGENT_COMPLETED = 'agent_completed',  // Agent 任务完成
  AGENT_STATUS_CHANGED = 'agent_status_changed',  // Agent 状态变化
  AGENT_ERROR = 'agent_error',  // Agent 错误
}

export interface OrtensiaMessage {
  type: MessageType
  from: string
  to: string
  timestamp: number
  payload: any
}

// ============================================================================
// Ortensia 协议客户端
// ============================================================================

export class OrtensiaClient {
  private ws: WebSocket | null = null
  private clientId: string
  private heartbeatInterval: number | null = null
  private discoveryTimer: number | null = null  // 🆕 用于存储发现对话的定时器
  private messageHandlers: Map<MessageType, (msg: OrtensiaMessage) => void> = new Map()
  private globalSubscribers: Set<(msg: OrtensiaMessage) => void> = new Set()
  
  // 🆕 消息去重（防止 React Strict Mode 多次订阅导致重复处理）
  private processedMessages: Set<string> = new Set()
  
  // 🆕 发现对话的重试机制
  private discoveryRetryCount = 0
  private maxDiscoveryRetries = 3
  
  // 单例模式
  private static instance: OrtensiaClient | null = null

  constructor() {
    this.clientId = this.generateClientId()
    // 设置单例
    OrtensiaClient.instance = this
  }
  
  /**
   * 获取全局单例实例
   */
  public static getInstance(): OrtensiaClient | null {
    return OrtensiaClient.instance
  }

  /**
   * 生成客户端 ID
   */
  private generateClientId(): string {
    const timestamp = Date.now().toString(36)
    const random = Math.random().toString(36).substring(2, 11)
    return `aituber-${timestamp}${random}`
  }

  /**
   * 连接到 Ortensia 中央服务器
   */
  public connect(url: string = 'ws://localhost:8765'): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`🌸 [Ortensia] 连接到中央服务器: ${url}`)
      
      // 🆕 清理旧的订阅者（避免页面刷新后残留）
      // 🔧 不清理订阅者！订阅者应该由各自的组件管理
      // React Strict Mode 会导致重复订阅，但通过消息去重机制处理
      if (this.globalSubscribers.size > 0) {
        console.log(`⚠️ [Ortensia] 已有 ${this.globalSubscribers.size} 个订阅者（保留）`)
      }
      
      try {
        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log('✅ [Ortensia] WebSocket 已连接')
          this.sendRegister()
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleMessage(event)
        }

        this.ws.onerror = (error) => {
          console.error('❌ [Ortensia] WebSocket 错误:', error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('🔌 [Ortensia] WebSocket 已断开')
          this.stopHeartbeat()
          
          // 🆕 清除发现定时器
          if (this.discoveryTimer !== null) {
            clearTimeout(this.discoveryTimer)
            this.discoveryTimer = null
          }
        }
      } catch (error) {
        console.error('❌ [Ortensia] 连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 发送注册消息（注册多个角色）
   */
  private sendRegister() {
    const message: OrtensiaMessage = {
      type: MessageType.REGISTER,
      from: this.clientId,
      to: 'server',
      timestamp: Date.now(),
      payload: {
        // 🆕 注册多个角色：aituber_client + command_client
        client_types: ['aituber_client', 'command_client'],
        platform: this.getPlatform(),
        pid: process.pid || 0,
        version: '1.0.0',
        metadata: {
          user_agent: navigator.userAgent,
          screen_resolution: `${window.screen.width}x${window.screen.height}`,
        },
      },
    }

    this.send(message)
    console.log('📤 [Ortensia] 发送注册消息 (多角色):', this.clientId, ['aituber_client', 'command_client'])
  }

  /**
   * 获取平台信息
   */
  private getPlatform(): string {
    const ua = navigator.userAgent.toLowerCase()
    if (ua.includes('mac')) return 'darwin'
    if (ua.includes('win')) return 'win32'
    if (ua.includes('linux')) return 'linux'
    return 'unknown'
  }

  /**
   * 开始心跳
   */
  private startHeartbeat() {
    this.stopHeartbeat()
    
    this.heartbeatInterval = window.setInterval(() => {
      const message: OrtensiaMessage = {
        type: MessageType.HEARTBEAT,
        from: this.clientId,
        to: 'server',
        timestamp: Date.now(),
        payload: {},
      }
      
      this.send(message)
    }, 30000) // 每 30 秒发送一次心跳
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(event: MessageEvent) {
    try {
      const message: OrtensiaMessage = JSON.parse(event.data)
      console.log('📨 [Ortensia] 收到消息:', message.type)

      // 🆕 对需要去重的消息类型进行去重检查
      const deduplicateTypes = [
        MessageType.AITUBER_RECEIVE_TEXT,
        MessageType.AGENT_COMPLETED,
        MessageType.AGENT_STATUS_CHANGED
      ]
      
      if (deduplicateTypes.includes(message.type)) {
        // 生成消息指纹
        const fingerprint = `${message.type}_${message.from}_${JSON.stringify(message.payload)}_${message.timestamp}`
        
        console.log(`🔍 [去重] 实例 ${this.clientId}: 检查消息`, {
          type: message.type,
          fingerprint: fingerprint.substring(0, 80),
          已处理数量: this.processedMessages.size,
          订阅者数量: this.globalSubscribers.size
        })
        
        // 检查是否已处理
        if (this.processedMessages.has(fingerprint)) {
          console.log(`🔕 [去重] 实例 ${this.clientId}: 跳过重复消息:`, message.type)
          return
        }
        
        // 标记为已处理
        this.processedMessages.add(fingerprint)
        console.log(`✅ [去重] 实例 ${this.clientId}: 标记为已处理 (共 ${this.processedMessages.size} 条)`)
        
        // 清理旧指纹（保留最近 50 条）
        if (this.processedMessages.size > 50) {
          const entries = Array.from(this.processedMessages)
          this.processedMessages = new Set(entries.slice(-25))
        }
      }

      // 通知所有全局订阅者
      console.log(`📢 [订阅] 实例 ${this.clientId}: 通知 ${this.globalSubscribers.size} 个订阅者`)
      let subscriberIndex = 0
      this.globalSubscribers.forEach((subscriber) => {
        try {
          subscriberIndex++
          console.log(`📢 [订阅] 实例 ${this.clientId}: 调用订阅者 ${subscriberIndex}`)
          subscriber(message)
        } catch (error) {
          console.error('❌ [Ortensia] 订阅者处理错误:', error)
        }
      })

      // 调用注册的处理器
      const handler = this.messageHandlers.get(message.type)
      if (handler) {
        handler(message)
      }

      // 处理系统消息
      switch (message.type) {
        case MessageType.REGISTER_ACK:
          console.log('✅ [Ortensia] 注册成功:', message.payload)
          
          // 🆕 注册成功后，延迟一下再发现已存在的对话（给 Inject 时间注册）
          // 清除旧的定时器（避免 React Strict Mode 双重挂载导致的问题）
          if (this.discoveryTimer !== null) {
            clearTimeout(this.discoveryTimer)
          }
          this.discoveryTimer = window.setTimeout(() => {
            this.discoverExistingConversations()
          }, 1500)
          break
        
        case MessageType.HEARTBEAT_ACK:
          // 心跳响应，不需要处理
          break
        
        case MessageType.AITUBER_RECEIVE_TEXT:
          console.log('📬 [Ortensia] 收到 AITuber 消息:', {
            text: message.payload.text,
            emotion: message.payload.emotion,
            audio_file: message.payload.audio_file,
            conversation_id: message.payload.conversation_id
          })
          break
        
        case MessageType.AGENT_COMPLETED:
          console.log('✅ [Ortensia] Agent 任务完成:', message.payload)
          break
        
        default:
          console.log('📬 [Ortensia] 其他消息:', message.type, message.payload)
      }
    } catch (error) {
      console.error('❌ [Ortensia] 消息解析错误:', error)
    }
  }

  /**
   * 发送消息
   */
  private send(message: OrtensiaMessage) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('❌ [Ortensia] WebSocket 未连接')
      return
    }

    try {
      const jsonStr = JSON.stringify(message)
      console.log(`🔍 [DEBUG] 准备发送消息: type=${message.type}, to=${message.to}, from=${message.from}`)
      console.log(`🔍 [DEBUG] JSON 内容 (前 200 字符): ${jsonStr.substring(0, 200)}`)
      this.ws.send(jsonStr)
      console.log(`✅ [DEBUG] 消息已发送到 WebSocket`)
    } catch (error) {
      console.error('❌ [Ortensia] 发送消息失败:', error)
    }
  }

  /**
   * 注册消息处理器
   */
  public on(type: MessageType, handler: (msg: OrtensiaMessage) => void) {
    this.messageHandlers.set(type, handler)
  }

  /**
   * 订阅所有消息（返回取消订阅函数）
   */
  public subscribe(handler: (msg: OrtensiaMessage) => void): () => void {
    console.log(`➕ [订阅] 实例 ${this.clientId}: 添加订阅者 (之前有 ${this.globalSubscribers.size} 个)`)
    this.globalSubscribers.add(handler)
    console.log(`✅ [订阅] 实例 ${this.clientId}: 现在有 ${this.globalSubscribers.size} 个订阅者`)
    
    return () => {
      console.log(`➖ [订阅] 实例 ${this.clientId}: 移除订阅者 (之前有 ${this.globalSubscribers.size} 个)`)
      const deleted = this.globalSubscribers.delete(handler)
      console.log(`${deleted ? '✅' : '❌'} [订阅] 实例 ${this.clientId}: 移除${deleted ? '成功' : '失败'}，现在有 ${this.globalSubscribers.size} 个订阅者`)
    }
  }

  /**
   * 取消订阅
   */
  public off(type: MessageType) {
    this.messageHandlers.delete(type)
  }

  /**
   * 发送 AITuber 说话消息
   */
  public sendSpeak(text: string, emotion: string = 'neutral', audioFile?: string) {
    const message: OrtensiaMessage = {
      type: MessageType.AITUBER_SPEAK,
      from: this.clientId,
      to: 'broadcast',
      timestamp: Date.now(),
      payload: {
        text,
        emotion,
        audio_file: audioFile,
      },
    }

    this.send(message)
    console.log('🎤 [Ortensia] 发送语音:', text)
  }

  /**
   * 发送 AITuber 情绪消息
   */
  public sendEmotion(emotion: string) {
    const message: OrtensiaMessage = {
      type: MessageType.AITUBER_EMOTION,
      from: this.clientId,
      to: 'broadcast',
      timestamp: Date.now(),
      payload: {
        emotion,
      },
    }

    this.send(message)
    console.log('😊 [Ortensia] 发送情绪:', emotion)
  }

  /**
   * 向 Cursor 发送文本输入请求（不执行）
   */
  public sendCursorInputText(text: string, conversationId?: string, execute: boolean = true) {
    // VNext: 统一提交给 Server，由 Server 做 session 队列仲裁与顺序一致性
    const clientEventId = `evt_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`
    const message: OrtensiaMessage = {
      type: MessageType.INPUT_SUBMIT,
      from: this.clientId,
      to: 'server',
      timestamp: Date.now(),
      payload: {
        client_event_id: clientEventId,
        text,
        conversation_id: conversationId,
        session_id: conversationId, // 默认用 conversation_id 作为 session_id
        execute,  // 是否立即执行
      },
    }

    this.send(message)
    const actionText = execute ? '输入并执行' : '输入'
    console.log(`⌨️  [Ortensia] ${actionText}文本到 Cursor:`, text.substring(0, 50))
  }

  /**
   * 🆕 发现已存在的 Cursor 对话
   * 向所有 Cursor Inject 广播请求，获取当前的 conversation_id
   */
  public discoverExistingConversations() {
    console.log(`🔍 [Ortensia] 正在发现已存在的 Cursor 对话 (尝试 ${this.discoveryRetryCount + 1}/${this.maxDiscoveryRetries})...`)
    console.log(`   WebSocket 状态: ${this.ws ? this.ws.readyState : 'null'}`)
    console.log(`   实例 ID: ${this.clientId}`)
    
    // 检查 WebSocket 连接状态
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️  [Ortensia] WebSocket 未连接')
      
      // 如果还有重试机会，延迟后重试
      if (this.discoveryRetryCount < this.maxDiscoveryRetries) {
        this.discoveryRetryCount++
        const retryDelay = 2000 * this.discoveryRetryCount  // 递增延迟：2s, 4s, 6s
        console.log(`   将在 ${retryDelay / 1000} 秒后重试...`)
        setTimeout(() => this.discoverExistingConversations(), retryDelay)
      } else {
        console.error('❌ [Ortensia] 发现对话失败：已达最大重试次数')
        console.log('   提示：请检查 WebSocket 服务器是否正常运行')
      }
      return
    }

    // 重置重试计数（成功连接）
    this.discoveryRetryCount = 0

    const message: OrtensiaMessage = {
      type: MessageType.GET_CONVERSATION_ID,
      from: this.clientId,
      to: 'cursor_inject',  // 广播给所有 inject 客户端
      timestamp: Date.now(),
      payload: {
        request_id: `discover_${Date.now()}`,
      },
    }

    this.send(message)
    console.log('📤 [Ortensia] 已发送 GET_CONVERSATION_ID 请求')
  }

  /**
   * 发送 AITuber 状态消息
   */
  public sendStatus(status: string, details?: any) {
    const message: OrtensiaMessage = {
      type: MessageType.AITUBER_STATUS,
      from: this.clientId,
      to: 'broadcast',
      timestamp: Date.now(),
      payload: {
        status,
        details,
      },
    }

    this.send(message)
    console.log('📊 [Ortensia] 发送状态:', status)
  }

  /**
   * 断开连接
   */
  public disconnect() {
    if (!this.ws) return

    const message: OrtensiaMessage = {
      type: MessageType.DISCONNECT,
      from: this.clientId,
      to: 'server',
      timestamp: Date.now(),
      payload: {
        reason: 'user_quit',
      },
    }

    this.send(message)
    this.stopHeartbeat()
    
    // 🆕 清除发现定时器
    if (this.discoveryTimer !== null) {
      clearTimeout(this.discoveryTimer)
      this.discoveryTimer = null
    }
    
    setTimeout(() => {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
    }, 100)

    console.log('👋 [Ortensia] 断开连接')
  }

  /**
   * 检查是否已连接
   */
  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * 获取客户端 ID
   */
  public getClientId(): string {
    return this.clientId
  }
}

