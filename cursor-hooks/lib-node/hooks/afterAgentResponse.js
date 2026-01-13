#!/usr/bin/env node
/**
 * afterAgentResponse (Node)
 */

const path = require("path");
const { AuditHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class AfterAgentResponseHook extends AuditHook {
  constructor() {
    super("afterAgentResponse");
  }

  audit() {
    const text = this.inputData.text || "";
    if (!text) return;

    const lower = String(text).toLowerCase();
    if (["完成", "done", "finished", "success"].some((w) => lower.includes(w))) {
      this.sendToOrtensia("Agent 完成任务了！干得漂亮！", "happy").catch(() => {});
    } else if (["错误", "error", "failed", "失败"].some((w) => lower.includes(w))) {
      this.sendToOrtensia("Agent 遇到问题了...我们一起解决吧", "sad").catch(() => {});
    } else if (["开始", "starting", "正在"].some((w) => lower.includes(w))) {
      this.sendToOrtensia("Agent 正在工作中...", "neutral").catch(() => {});
    }
  }
}

process.exit(new AfterAgentResponseHook().run());

