export class AutoTaskChecker {
  private checkPrompt: string =
    '请检查是否还有计划中的任务可以完成，如果有请执行，如果没有，请回复"已结束"或"已完成"'

  // ✅ 停止关键词：只接受明确的“已结束/已完成”
  // 不要用“任务完成”等泛化文案，否则 stop 事件会导致自动检查立刻停止。
  private stopKeywords: string[] = ['已结束', '已完成']
  private lastCheckTimes: Map<string, number> = new Map()
  private minCheckInterval: number = 5000  // 最小检查间隔5秒
  
  // ✅ 允许触发停止检查的事件类型：
  // 只信任 afterAgentResponse（Agent 原始输出）。
  // 不使用 stop 事件作为停止依据，否则 stop hook 的“任务完成”提示会误触发停止。
  private stopEventTypes: string[] = ['afterAgentResponse']

  // ✅ 防刷：自动检查频率/次数熔断（避免无限循环扣费）
  private checkWindowMs: number = 10 * 60_000
  private maxChecksPerWindow: number = 4
  private recentCheckTimes: Map<string, number[]> = new Map()
  
  canTriggerCheck(conversationId: string): { ok: boolean; shouldAutoStop: boolean; reason?: string } {
    const lastTime = this.lastCheckTimes.get(conversationId) || 0
    const now = Date.now()

    // 1) 最小间隔限制
    if (now - lastTime < this.minCheckInterval) {
      console.log(`[Auto Check] 跳过检查，距上次不足 ${this.minCheckInterval}ms`)
      return { ok: false, shouldAutoStop: false, reason: 'min_interval' }
    }

    // 2) 窗口频率限制
    const times = this.recentCheckTimes.get(conversationId) || []
    const windowStart = now - this.checkWindowMs
    const recent = times.filter((t) => t >= windowStart)
    if (recent.length >= this.maxChecksPerWindow) {
      console.log(`[Auto Check] 触发熔断：${this.checkWindowMs}ms 内已检查 ${recent.length} 次`)
      return { ok: false, shouldAutoStop: true, reason: 'rate_limit' }
    }

    // 回写裁剪后的数组（避免无限增长）
    this.recentCheckTimes.set(conversationId, recent)
    return { ok: true, shouldAutoStop: false }
  }
  
  recordCheck(conversationId: string) {
    const now = Date.now()
    this.lastCheckTimes.set(conversationId, now)
    const times = this.recentCheckTimes.get(conversationId) || []
    times.push(now)
    // 裁剪窗口内数据
    const windowStart = now - this.checkWindowMs
    this.recentCheckTimes.set(conversationId, times.filter((t) => t >= windowStart))
  }
  
  getCheckPrompt(): string {
    return this.checkPrompt
  }
  
  /**
   * 🔧 修复：检查是否应该停止自动任务检查
   * 必须同时满足：
   * 1. 事件类型是 stop 或 afterAgentResponse（Agent 完成类事件）
   * 2. 文本包含停止关键词（如“已结束/任务完成”等）
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
    const hitKeyword = this.stopKeywords.find((kw) => responseText.includes(kw))
    const hasStopKeyword = Boolean(hitKeyword)
    console.log(`[Auto Check] shouldStop: eventType="${eventType}", hitKeyword=${hitKeyword || 'none'}`)
    
    return hasStopKeyword
  }
}



