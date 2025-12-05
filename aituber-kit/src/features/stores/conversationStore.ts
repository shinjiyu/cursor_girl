import { create } from 'zustand'

export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

export interface Conversation {
  id: string  // conversation_id
  title: string
  messages: Message[]
  autoCheckEnabled: boolean  // 每个窗口独立的自动检查开关
  lastActivity: number
}

interface ConversationState {
  conversations: Map<string, Conversation>
  activeConversationId: string | null
  
  // 操作方法
  getOrCreateConversation: (conversationId: string, title?: string) => Conversation
  updateConversationTitle: (conversationId: string, title: string) => void
  addMessage: (conversationId: string, message: Message) => void
  setActiveConversation: (conversationId: string) => void
  setAutoCheckEnabled: (conversationId: string, enabled: boolean) => void
  getAutoCheckEnabled: (conversationId: string) => boolean
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversations: new Map(),
  activeConversationId: null,
  
  getOrCreateConversation: (conversationId: string, title?: string) => {
    const { conversations } = get()
    
    if (!conversations.has(conversationId)) {
      const newConversation: Conversation = {
        id: conversationId,
        title: title || `Conversation ${conversationId.slice(0, 8)}`,
        messages: [],
        autoCheckEnabled: false,  // 默认关闭
        lastActivity: Date.now(),
      }
      
      set((state) => {
        const newConversations = new Map(state.conversations)
        newConversations.set(conversationId, newConversation)
        return {
          conversations: newConversations,
          activeConversationId: state.activeConversationId || conversationId
        }
      })
      
      return newConversation
    }
    
    return conversations.get(conversationId)!
  },
  
  updateConversationTitle: (conversationId: string, title: string) => {
    set((state) => {
      const newConversations = new Map(state.conversations)
      const conversation = newConversations.get(conversationId)
      if (conversation) {
        newConversations.set(conversationId, {
          ...conversation,
          title: title
        })
      }
      return { conversations: newConversations }
    })
  },
  
  addMessage: (conversationId: string, message: Message) => {
    set((state) => {
      const newConversations = new Map(state.conversations)
      const conversation = newConversations.get(conversationId)
      
      if (conversation) {
        conversation.messages.push({
          ...message,
          timestamp: Date.now()
        })
        conversation.lastActivity = Date.now()
      }
      
      return { conversations: newConversations }
    })
  },
  
  setActiveConversation: (conversationId: string) => {
    set({ activeConversationId: conversationId })
  },
  
  setAutoCheckEnabled: (conversationId: string, enabled: boolean) => {
    console.log(`📝 [Store] setAutoCheckEnabled: ${conversationId} = ${enabled}`)
    set((state) => {
      const newConversations = new Map(state.conversations)
      const conversation = newConversations.get(conversationId)
      
      if (conversation) {
        conversation.autoCheckEnabled = enabled
        console.log(`✅ [Store] 设置成功，当前值: ${conversation.autoCheckEnabled}`)
      } else {
        console.warn(`⚠️ [Store] 找不到对话: ${conversationId}`)
      }
      
      return { conversations: newConversations }
    })
  },
  
  getAutoCheckEnabled: (conversationId: string) => {
    const conversation = get().conversations.get(conversationId)
    const result = conversation?.autoCheckEnabled ?? false
    console.log(`🔍 [Store] getAutoCheckEnabled(${conversationId}): ${result}`)
    return result
  },
}))



