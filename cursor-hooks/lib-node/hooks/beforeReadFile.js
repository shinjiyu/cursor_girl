#!/usr/bin/env node
/**
 * beforeReadFile (Node)
 */

const path = require("path");
const { PermissionHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class BeforeReadFileHook extends PermissionHook {
  constructor() {
    super("beforeReadFile");
  }

  static SENSITIVE_PATTERNS = [
    String.raw`\.env`,
    String.raw`\.env\..*`,
    String.raw`id_rsa`,
    String.raw`\.pem$`,
    String.raw`\.key$`,
    "password",
    "secret",
    "token",
    "credentials",
    String.raw`\.ssh/`,
    String.raw`\.aws/`,
    String.raw`\.kube/config`,
  ];

  makeDecision() {
    const filePath = this.inputData.file_path || "";
    if (!filePath) return ["allow", null, null];

    const fileName = path.basename(filePath);
    const lower = String(filePath).toLowerCase();

    for (const pattern of BeforeReadFileHook.SENSITIVE_PATTERNS) {
      const re = new RegExp(pattern, "i");
      if (re.test(lower)) {
        this.sendToOrtensia(`Agent 要读取敏感文件：${fileName}，需要确认`, "surprised").catch(() => {});
        return ["ask", `⚠️  Agent 要读取敏感文件：${fileName}\n是否允许？`, null];
      }
    }

    if (["config", "setting"].some((k) => lower.includes(k))) {
      this.sendToOrtensia(`Agent 正在读取配置：${fileName}`, "neutral").catch(() => {});
    }
    return ["allow", null, null];
  }
}

process.exit(new BeforeReadFileHook().run());

