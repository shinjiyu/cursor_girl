#!/usr/bin/env node
/**
 * stop (Node)
 */

const path = require("path");
const { StopHook } = require(path.join(__dirname, "..", "lib-node", "agent_hook_handler"));

class StopAgentHook extends StopHook {
  constructor() {
    super("stop");
  }

  shouldContinue() {
    const status = this.inputData.status || "";
    const loopCount = this.inputData.loop_count || 0;

    if (status === "completed") {
      this.sendToOrtensia("Agent 任务完成了！太棒了！🎉", "excited").catch(() => {});
    } else if (status === "aborted") {
      this.sendToOrtensia("Agent 任务被中止了", "neutral").catch(() => {});
    } else if (status === "error") {
      this.sendToOrtensia("Agent 遇到错误了...别担心，我们可以再试试", "sad").catch(() => {});
    }

    // Keep behavior identical to Python: no auto-followup by default.
    void loopCount;
    return null;
  }
}

process.exit(new StopAgentHook().run());

