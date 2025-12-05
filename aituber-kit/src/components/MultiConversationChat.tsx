import { useState } from 'react'
import { useConversationStore } from '@/features/stores/conversationStore'
import { OrtensiaClient } from '@/utils/OrtensiaClient'

export function MultiConversationChat() {
  const conversationStore = useConversationStore()
  const { conversations, activeConversationId } = conversationStore
  const [inputText, setInputText] = useState('')
  
  const activeConversation = activeConversationId 
    ? conversations.get(activeConversationId)
    : null
  
  return (
    <div style={{ 
      position: 'fixed', 
      right: 0, 
      top: 0, 
      width: '50%',  // 右侧占50%
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'rgba(15, 15, 25, 0.75)',  // 半透明背景
      backdropFilter: 'blur(12px)',
      boxShadow: '-8px 0 24px rgba(0, 0, 0, 0.4)',
      borderLeft: '2px solid rgba(157, 78, 221, 0.3)',
    }}>
      {/* Conversation 标签栏 */}
      <div style={{ 
        display: 'flex', 
        borderBottom: '1px solid rgba(255,255,255,0.2)', 
        background: 'rgba(20,20,30,0.95)',
        overflowX: 'auto',
      }}>
        {Array.from(conversations.values()).map((conv) => (
          <button
            key={conv.id}
            onClick={() => conversationStore.setActiveConversation(conv.id)}
            style={{
              padding: '8px 12px',
              background: activeConversationId === conv.id ? 'rgba(157,78,221,0.3)' : 'transparent',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              fontSize: '12px',
              whiteSpace: 'nowrap',
            }}
          >
            {conv.title}
          </button>
        ))}
      </div>
      
      {/* 自动检查开关（每个窗口独立） */}
      {activeConversation && (
        <div style={{ 
          padding: '12px', 
          borderBottom: '1px solid rgba(255,255,255,0.1)', 
          background: 'rgba(0,0,0,0.2)' 
        }}>
          <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={activeConversation.autoCheckEnabled}
              onChange={(e) => {
                conversationStore.setAutoCheckEnabled(activeConversation.id, e.target.checked)
                console.log(`[Auto Check] ${activeConversation.id}: ${e.target.checked ? '启用' : '禁用'}`)
              }}
              style={{ marginRight: '8px' }}
            />
            <span style={{ fontSize: '12px' }}>
              自动任务检查 {activeConversation.autoCheckEnabled ? '✅' : '⏸️'}
            </span>
          </label>
          <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.5)', marginTop: '4px' }}>
            默认关闭，启用后自动询问下一步
          </div>
        </div>
      )}
      
      {/* 消息列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
        {activeConversation?.messages.map((msg, idx) => (
          <div key={idx} style={{ 
            marginBottom: '12px', 
            color: msg.role === 'user' ? '#9D4EDD' : 'white' 
          }}>
            <div style={{ fontSize: '10px', opacity: 0.6 }}>
              {msg.role === 'user' ? '👤 You' : msg.role === 'system' ? '⚙️ System' : '🤖 Assistant'}
            </div>
            <div style={{ fontSize: '14px' }}>{msg.content}</div>
          </div>
        ))}
      </div>
      
      {/* 输入框 */}
      <div style={{ padding: '12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
        <input
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="输入命令..."
          style={{ 
            width: '100%', 
            padding: '8px', 
            background: 'rgba(255,255,255,0.1)', 
            border: 'none', 
            color: 'white',
            borderRadius: '4px',
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (inputText.trim() && activeConversationId) {
                conversationStore.addMessage(activeConversationId, {
                  role: 'user',
                  content: inputText.trim(),
                  timestamp: Date.now()
                })
                
                const client = OrtensiaClient.getInstance()
                client.sendCursorInputText(inputText.trim(), activeConversationId, true)
                setInputText('')
              }
            }
          }}
        />
      </div>
    </div>
  )
}

