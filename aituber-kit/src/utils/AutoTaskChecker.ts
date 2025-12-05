export class AutoTaskChecker {
  private checkPrompt: string = '请检查是否还有计划中的任务可以完成，如果有请执行，如果没有，请回复"已结束"'
  private stopKeyword: string = '已结束'
  private lastCheckTimes: Map<string, number> = new Map()
  private minCheckInterval: number = 5000  // 最小检查间隔5秒
  
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
  
  shouldStop(responseText: string): boolean {
    return responseText.includes(this.stopKeyword)
  }
}



