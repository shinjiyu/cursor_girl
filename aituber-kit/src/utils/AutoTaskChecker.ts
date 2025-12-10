export class AutoTaskChecker {
  private checkPrompt: string = '请检查是否还有计划中的任务可以完成，如果有请执行，如果没有，请回复"已结束"'
  private stopKeyword: string = '已结束'
  private lastCheckTimes: Map<string, number> = new Map()
  private minCheckInterval: number = 5000  // 最小检查间隔5秒
  
  // 🆕 允许触发停止检查的事件类型（只有 Agent 完成类事件才检查停止关键词）
  private stopEventTypes: string[] = ['stop', 'afterAgentResponse']
  
  canTriggerCheck(conversationId: string): boolean {
    const lastTime = this.lastCheckTimes.get(conversationId) || 0
    const now = Date.now()
    
    if (now - lastTime < this.minCheckInterval) {
      console.log(`[Auto Check] 跳过检查，距上次不足 ${this.minCheckInterval}ms`)
      return false
    }
    
    return true
  }
  
  recordCheck(conversationId: string) {
    this.lastCheckTimes.set(conversationId, Date.now())
  }
  
  getCheckPrompt(): string {
    return this.checkPrompt
  }
  
  /**
   * 🔧 修复：检查是否应该停止自动任务检查
   * 必须同时满足：
   * 1. 事件类型是 stop 或 afterAgentResponse（Agent 完成类事件）
   * 2. 文本包含"已结束"关键词
   */
  shouldStop(responseText: string, eventType?: string): boolean {
    // 如果没有事件类型，不停止（可能是用户输入）
    if (!eventType) {
      console.log(`[Auto Check] shouldStop: 无事件类型，跳过停止检查`)
      return false
    }
    
    // 检查是否是允许触发停止的事件类型
    const isStopEventType = this.stopEventTypes.includes(eventType)
    if (!isStopEventType) {
      console.log(`[Auto Check] shouldStop: 事件类型 "${eventType}" 不是完成类事件，跳过`)
      return false
    }
    
    // 检查文本是否包含停止关键词
    const hasStopKeyword = responseText.includes(this.stopKeyword)
    console.log(`[Auto Check] shouldStop: eventType="${eventType}", hasKeyword=${hasStopKeyword}`)
    
    return hasStopKeyword
  }
}



