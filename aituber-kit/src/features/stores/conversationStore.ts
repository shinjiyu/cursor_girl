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
  getOrCreateConversation: (conversationId: string) => Conversation
  addMessage: (conversationId: string, message: Message) => void
  setActiveConversation: (conversationId: string) => void
  setAutoCheckEnabled: (conversationId: string, enabled: boolean) => void
  getAutoCheckEnabled: (conversationId: string) => boolean
}

export const useConversationStore = create<ConversationState>((set, get) => ({
  conversations: new Map(),
  activeConversationId: null,
  
  getOrCreateConversation: (conversationId: string) => {
    const { conversations } = get()
    
    if (!conversations.has(conversationId)) {
      const newConversation: Conversation = {
        id: conversationId,
        title: `Conversation ${conversationId.slice(0, 8)}`,
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
    set((state) => {
      const newConversations = new Map(state.conversations)
      const conversation = newConversations.get(conversationId)
      
      if (conversation) {
        conversation.autoCheckEnabled = enabled
      }
      
      return { conversations: newConversations }
    })
  },
  
  getAutoCheckEnabled: (conversationId: string) => {
    const conversation = get().conversations.get(conversationId)
    return conversation?.autoCheckEnabled ?? false
  },
}))



