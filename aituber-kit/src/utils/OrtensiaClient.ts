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
  private messageHandlers: Map<MessageType, (msg: OrtensiaMessage) => void> = new Map()

  constructor() {
    this.clientId = this.generateClientId()
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
        }
      } catch (error) {
        console.error('❌ [Ortensia] 连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 发送注册消息
   */
  private sendRegister() {
    const message: OrtensiaMessage = {
      type: MessageType.REGISTER,
      from: this.clientId,
      to: 'server',
      timestamp: Date.now(),
      payload: {
        client_type: ClientType.AITUBER_CLIENT,
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
    console.log('📤 [Ortensia] 发送注册消息:', this.clientId)
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

      // 调用注册的处理器
      const handler = this.messageHandlers.get(message.type)
      if (handler) {
        handler(message)
      }

      // 处理系统消息
      switch (message.type) {
        case MessageType.REGISTER_ACK:
          console.log('✅ [Ortensia] 注册成功:', message.payload)
          break
        
        case MessageType.HEARTBEAT_ACK:
          // 心跳响应，不需要处理
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
      this.ws.send(JSON.stringify(message))
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

