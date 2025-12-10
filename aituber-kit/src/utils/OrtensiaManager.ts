/**
 * Ortensia 管理器
 * 
 * 统一管理 OrtensiaClient 的生命周期、事件订阅和消息分发
 * 解决 React Strict Mode 导致的时序问题
 */

import { OrtensiaClient, OrtensiaMessage, MessageType } from './OrtensiaClient'

type MessageHandler = (message: OrtensiaMessage) => void
type ReadyCallback = () => void

interface ManagerState {
  clientReady: boolean
  handlersRegistered: boolean
  discoveryRequested: boolean
}

export class OrtensiaManager {
  private static instance: OrtensiaManager | null = null
  
  private client: OrtensiaClient | null = null
  private handlers: Map<MessageType, Set<MessageHandler>> = new Map()
  private readyCallbacks: Set<ReadyCallback> = new Set()
  private isSubscribed: boolean = false  // 🔧 跟踪是否已订阅
  
  private state: ManagerState = {
    clientReady: false,
    handlersRegistered: false,
    discoveryRequested: false,
  }
  
  private constructor() {
    console.log('🎛️  [OrtensiaManager] 初始化')
  }
  
  /**
   * 获取单例实例
   */
  public static getInstance(): OrtensiaManager {
    if (!OrtensiaManager.instance) {
      OrtensiaManager.instance = new OrtensiaManager()
    }
    return OrtensiaManager.instance
  }
  
  /**
   * 初始化 Ortensia 客户端
   * 可以多次调用（幂等），但只订阅一次
   */
  public initialize(): void {
    // 创建客户端（如果还没创建）
    if (!this.client) {
      console.log('🔧 [OrtensiaManager] 创建 OrtensiaClient')
      this.client = OrtensiaClient.getInstance()
      
      if (!this.client) {
        this.client = new OrtensiaClient()
      }
      
      this.state.clientReady = true
      console.log('✅ [OrtensiaManager] 客户端已创建')
    } else {
      console.log('⚠️  [OrtensiaManager] 客户端已存在')
    }
    
    // 🔧 只订阅一次（幂等）
    if (!this.isSubscribed) {
      console.log('🔧 [OrtensiaManager] 设置消息分发器（首次）')
      this.client.subscribe((message: OrtensiaMessage) => {
        console.log(`📨 [OrtensiaManager] 收到消息: ${message.type}，准备分发`)
        this.dispatchMessage(message)
      })
      this.isSubscribed = true
      console.log('✅ [OrtensiaManager] 消息分发器已设置')
    } else {
      console.log('⚠️  [OrtensiaManager] 消息分发器已存在，跳过重复订阅')
    }
    
    // 通知所有等待的回调
    this.readyCallbacks.forEach(cb => cb())
    this.readyCallbacks.clear()
  }
  
  /**
   * 注册消息处理器
   */
  public on(messageType: MessageType, handler: MessageHandler): () => void {
    console.log(`➕ [OrtensiaManager] 注册处理器: ${messageType}`)
    
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, new Set())
    }
    
    this.handlers.get(messageType)!.add(handler)
    
    // 返回取消注册的函数
    return () => {
      console.log(`➖ [OrtensiaManager] 取消处理器: ${messageType}`)
      this.handlers.get(messageType)?.delete(handler)
    }
  }
  
  /**
   * 分发消息到所有已注册的处理器
   */
  private dispatchMessage(message: OrtensiaMessage): void {
    const handlers = this.handlers.get(message.type)
    
    if (!handlers || handlers.size === 0) {
      console.log(`📭 [OrtensiaManager] 无处理器: ${message.type}`)
      return
    }
    
    console.log(`📨 [OrtensiaManager] 分发消息: ${message.type} → ${handlers.size} 个处理器`)
    handlers.forEach(handler => {
      try {
        handler(message)
      } catch (error) {
        console.error(`❌ [OrtensiaManager] 处理器错误 (${message.type}):`, error)
      }
    })
  }
  
  /**
   * 标记处理器已注册完成
   * 当所有必要的处理器都注册后调用
   */
  public markHandlersReady(): void {
    if (this.state.handlersRegistered) {
      console.log('⚠️  [OrtensiaManager] 处理器已标记为就绪，跳过')
      return
    }
    
    this.state.handlersRegistered = true
    console.log('✅ [OrtensiaManager] 处理器已就绪')
    
    // 检查是否可以发送发现请求
    this.checkAndDiscoverConversations()
  }
  
  /**
   * 检查条件并发送发现对话请求
   * 只有当客户端就绪且处理器注册完成后才会发送
   */
  private checkAndDiscoverConversations(): void {
    // 检查所有前置条件
    if (!this.state.clientReady) {
      console.log('⏳ [OrtensiaManager] 等待客户端就绪...')
      return
    }
    
    if (!this.state.handlersRegistered) {
      console.log('⏳ [OrtensiaManager] 等待处理器注册...')
      return
    }
    
    if (this.state.discoveryRequested) {
      console.log('⚠️  [OrtensiaManager] 已发送发现请求，跳过')
      return
    }
    
    if (!this.client) {
      console.error('❌ [OrtensiaManager] 客户端未初始化')
      return
    }
    
    // 所有条件满足，发送发现请求
    console.log('🔍 [OrtensiaManager] 所有条件满足，发送发现对话请求')
    this.state.discoveryRequested = true
    
    // 延迟一下，确保 WebSocket 连接已稳定
    setTimeout(() => {
      if (this.client) {
        this.client.discoverExistingConversations()
      }
    }, 2000) // 2秒延迟，确保连接稳定
  }
  
  /**
   * 等待管理器就绪
   */
  public onReady(callback: ReadyCallback): void {
    if (this.state.clientReady) {
      // 已经就绪，立即执行
      callback()
    } else {
      // 还未就绪，加入等待队列
      this.readyCallbacks.add(callback)
    }
  }
  
  /**
   * 获取客户端实例（用于直接调用）
   */
  public getClient(): OrtensiaClient | null {
    return this.client
  }
  
  /**
   * 获取当前状态（用于调试）
   */
  public getState(): ManagerState {
    return { ...this.state }
  }
  
  /**
   * 重置状态（主要用于开发/测试）
   */
  public reset(): void {
    console.log('🔄 [OrtensiaManager] 重置状态')
    this.state = {
      clientReady: false,
      handlersRegistered: false,
      discoveryRequested: false,
    }
    this.handlers.clear()
    this.readyCallbacks.clear()
    // 注意：不重置 client，保持单例
  }
}

// 导出单例实例
export default OrtensiaManager.getInstance()

