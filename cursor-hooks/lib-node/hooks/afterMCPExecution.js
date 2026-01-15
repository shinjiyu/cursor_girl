#!/usr/bin/env node
/**
 * afterMCPExecution (Node)
 */

const path = require("path");
const { AuditHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class AfterMCPExecutionHook extends AuditHook {
  constructor() {
    super("afterMCPExecution");
  }

  async audit() {
    const toolName = this.inputData.tool_name || "";
    const resultJson = this.inputData.result_json || "";
    if (!toolName) return;

    const hasError = String(resultJson).includes('"error"') || String(resultJson).includes('"success": false');
    if (hasError) {
      try {
        await this.sendToOrtensia(`工具失败：${toolName}`, "sad");
      } catch {}
    } else {
      try {
        await this.sendToOrtensia(`工具完成：${toolName}`, "happy");
      } catch {}
    }
  }
}

module.exports = (async () => {
  const code = await new AfterMCPExecutionHook().run();
  return code;
})();

