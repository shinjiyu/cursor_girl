#!/usr/bin/env node
/**
 * beforeShellExecution (Node)
 */

const path = require("path");
const { PermissionHook } = require(path.join(__dirname, "..", "lib-node", "agent_hook_handler"));

class BeforeShellExecutionHook extends PermissionHook {
  constructor() {
    super("beforeShellExecution");
    this.command = "";
    this.cwd = "";
  }

  static DANGEROUS_PATTERNS = [
    String.raw`rm\s+-rf\s+/`,
    String.raw`rm\s+-rf\s+\*`,
    String.raw`:\(\)\{.*;\};`,
    String.raw`>\s*/dev/sd[a-z]`,
    String.raw`dd\s+if=.*of=/dev/`,
    String.raw`mkfs\.`,
    String.raw`chmod\s+-R\s+777\s+/`,
    String.raw`curl.*\|\s*sh`,
    String.raw`wget.*\|\s*sh`,
  ];

  static RISKY_PATTERNS = [
    String.raw`rm\s+-rf`,
    String.raw`DROP\s+DATABASE`,
    String.raw`DROP\s+TABLE`,
    String.raw`DELETE\s+FROM.*WHERE\s+1=1`,
    String.raw`git\s+push\s+.*--force`,
    String.raw`npm\s+publish`,
    String.raw`docker\s+rm\s+-f`,
  ];

  makeDecision() {
    this.command = this.inputData.command || "";
    this.cwd = this.inputData.cwd || "";

    this.logger.info(`🔍 检查命令: ${this.command}`);
    this.logger.info(`📁 工作目录: ${this.cwd}`);

    if (!this.command) {
      this.logger.warn("⚠️  命令为空，允许执行");
      return ["allow", null, null];
    }

    this.logger.info("🔍 步骤 1/3: 检查危险命令模式...");
    for (const pattern of BeforeShellExecutionHook.DANGEROUS_PATTERNS) {
      const re = new RegExp(pattern, "i");
      if (re.test(this.command)) {
        this.logger.warn(`🚨 匹配到危险命令模式: ${pattern}`);
        this.logger.warn(`🚫 拒绝执行命令: ${this.command}`);
        // fire-and-forget
        this.sendToOrtensia(`检测到危险命令！已阻止：${this.command.slice(0, 50)}...`, "angry").catch(() => {});
        return ["deny", `🚫 危险命令已被阻止：${this.command}`, `命令 '${this.command}' 被安全策略阻止`];
      }
    }
    this.logger.info("✅ 未检测到危险命令");

    this.logger.info("🔍 步骤 2/3: 检查风险命令模式...");
    for (const pattern of BeforeShellExecutionHook.RISKY_PATTERNS) {
      const re = new RegExp(pattern, "i");
      if (re.test(this.command)) {
        this.logger.warn(`⚠️  匹配到风险命令模式: ${pattern}`);
        this.logger.warn(`❓ 需要用户确认: ${this.command}`);
        this.sendToOrtensia(`检测到风险命令，需要确认：${this.command.slice(0, 50)}...`, "surprised").catch(() => {});
        return ["ask", `⚠️  风险命令需要确认：${this.command}`, null];
      }
    }
    this.logger.info("✅ 未检测到风险命令");

    this.logger.info("🔍 步骤 3/3: 发送命令通知...");
    const cmdPreview = this.command.length > 40 ? `${this.command.slice(0, 40)}...` : this.command;
    this.logger.info(`💬 发送命令通知: ${cmdPreview}`);
    this.sendToOrtensia(`执行命令：${cmdPreview}`, "neutral").catch(() => {});
    this.logger.info("✅ 允许执行命令");
    return ["allow", null, null];
  }
}

process.exit(new BeforeShellExecutionHook().run());

