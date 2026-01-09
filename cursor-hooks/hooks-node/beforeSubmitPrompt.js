#!/usr/bin/env node
/**
 * beforeSubmitPrompt (Node)
 *
 * Contract: returns { continue: true }
 */

const path = require("path");
const { AgentHookHandler } = require(path.join(__dirname, "..", "lib-node", "agent_hook_handler"));

class BeforeSubmitPromptHook extends AgentHookHandler {
  constructor() {
    super("beforeSubmitPrompt");
  }

  static SENSITIVE_PATTERNS = [
    [/\b[A-Za-z0-9]{20,}\b/gi, "API Key"],
    [/\b(?:\d{1,3}\.){3}\d{1,3}\b/gi, "IP 地址"],
    [/password\s*[:=]\s*[^\s]+/gi, "密码"],
    [/token\s*[:=]\s*[^\s]+/gi, "Token"],
  ];

  process() {
    const prompt = this.inputData.prompt || "";
    if (!prompt) return { continue: true };

    for (const [re, name] of BeforeSubmitPromptHook.SENSITIVE_PATTERNS) {
      if (re.test(prompt)) {
        this.sendToOrtensia(`检测到 Prompt 中可能包含${name}，请注意安全！`, "surprised").catch(() => {});
      }
    }

    const words = String(prompt).split(/\s+/).slice(0, 10);
    const preview = `${words.join(" ")}${words.length >= 10 ? "..." : ""}`;
    this.sendToOrtensia(`开始新的 Agent 任务：${preview}`, "happy").catch(() => {});
    return { continue: true };
  }
}

process.exit(new BeforeSubmitPromptHook().run());

