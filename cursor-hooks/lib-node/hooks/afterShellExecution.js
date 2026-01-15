#!/usr/bin/env node
/**
 * afterShellExecution (Node)
 */

const path = require("path");
const { AuditHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class AfterShellExecutionHook extends AuditHook {
  constructor() {
    super("afterShellExecution");
  }

  async audit() {
    const command = this.inputData.command || "";
    const output = this.inputData.output || "";
    const exitCode = typeof this.inputData.exit_code === "number" ? this.inputData.exit_code : 0;

    if (!command) return;

    const cmdPreview = command.length > 30 ? `${command.slice(0, 30)}...` : command;
    const lowerOut = String(output).toLowerCase();
    const hasError =
      exitCode !== 0 ||
      ["error", "failed", "exception", "traceback"].some((k) => lowerOut.includes(k));

    if (hasError) {
      try {
        await this.sendToOrtensia(`命令失败：${cmdPreview}`, "sad");
      } catch {}
    } else {
      try {
        await this.sendToOrtensia(`命令完成：${cmdPreview}`, "happy");
      } catch {}
    }
  }
}

module.exports = (async () => {
  const code = await new AfterShellExecutionHook().run();
  return code;
})();

