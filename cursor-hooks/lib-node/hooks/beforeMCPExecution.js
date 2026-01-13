#!/usr/bin/env node
/**
 * beforeMCPExecution (Node)
 */

const path = require("path");
const { PermissionHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class BeforeMCPExecutionHook extends PermissionHook {
  constructor() {
    super("beforeMCPExecution");
  }

  static SENSITIVE_TOOLS = [
    "delete_file",
    "delete_directory",
    "execute_command",
    "write_file",
    "database_query",
  ];

  makeDecision() {
    const toolName = this.inputData.tool_name || "";
    if (!toolName) return ["allow", null, null];

    if (BeforeMCPExecutionHook.SENSITIVE_TOOLS.includes(toolName)) {
      this.sendToOrtensia(`Agent 要使用工具：${toolName}，需要确认`, "surprised").catch(() => {});
      return ["ask", `⚠️  MCP 工具需要确认：${toolName}`, null];
    }

    this.sendToOrtensia(`Agent 正在使用工具：${toolName}`, "neutral").catch(() => {});
    return ["allow", null, null];
  }
}

process.exit(new BeforeMCPExecutionHook().run());

