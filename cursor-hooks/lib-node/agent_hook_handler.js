/**
 * Cursor Agent Hooks handler (Node.js)
 *
 * Contract:
 * - Reads JSON from stdin (Cursor passes event payload)
 * - For permission hooks: write JSON to stdout: { permission: "allow"|"deny"|"ask", ... }
 * - For audit hooks: usually no stdout output
 *
 * Logging:
 * - Writes to CURSOR_AGENT_HOOKS_LOG if set, else os.tmpdir()/cursor-agent-hooks.log
 */

const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");

function expandUser(p) {
  if (!p) return p;
  if (p.startsWith("~")) {
    const home = process.env.HOME || process.env.USERPROFILE || "";
    return path.join(home, p.slice(1));
  }
  return p;
}

function getLogFilePath() {
  const env = process.env.CURSOR_AGENT_HOOKS_LOG;
  if (env && env.trim()) return expandUser(env.trim());
  return path.join(os.tmpdir(), "cursor-agent-hooks.log");
}

function ensureDirExists(filePath) {
  try {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
  } catch {
    // ignore; file write will surface errors if needed
  }
}

function nowTs() {
  const d = new Date();
  // YYYY-MM-DD HH:mm:ss
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

class Logger {
  constructor(logFile) {
    this.logFile = logFile;
    ensureDirExists(logFile);
  }
  _write(level, message) {
    const line = `[${nowTs()}] [${level}] ${message}\n`;
    try {
      fs.appendFileSync(this.logFile, line, { encoding: "utf8" });
    } catch {
      // ignore
    }
    try {
      process.stderr.write(line);
    } catch {
      // ignore
    }
  }
  info(msg) {
    this._write("INFO", msg);
  }
  warn(msg) {
    this._write("WARN", msg);
  }
  error(msg) {
    this._write("ERROR", msg);
  }
  debug(msg) {
    if (process.env.DEBUG_HOOKS === "1" || process.env.DEBUG_HOOKS === "true") {
      this._write("DEBUG", msg);
    }
  }
}

class AgentHookHandler {
  constructor(hookName) {
    this.hookName = hookName;
    this.inputData = {};
    this.wsServer = resolveOrtensiaServer();
    this.logFile = getLogFilePath();
    this.logger = new Logger(this.logFile);
    this.logger.info(`🎣 [${hookName}] Agent Hook 启动`);
    this.logger.info(`🌐 Ortensia Server: ${this.wsServer}`);
  }

  readInput() {
    try {
      const inputText = fs.readFileSync(0, "utf8");
      this.logger.info("=".repeat(70));
      this.logger.info(`📥 [${this.hookName}] 接收到 Cursor 调用`);
      this.logger.info("=".repeat(70));
      this.logger.debug(`原始输入: ${inputText.slice(0, 500)}...`);

      if (!inputText.trim()) {
        this.logger.warn("⚠️  输入为空");
        this.inputData = {};
        return this.inputData;
      }
      this.inputData = JSON.parse(inputText);

      this.logger.info("📋 输入数据摘要:");
      for (const [k, v] of Object.entries(this.inputData)) {
        if (typeof v === "string" && v.length > 100) {
          this.logger.info(`   • ${k}: ${v.slice(0, 100)}...`);
        } else {
          this.logger.info(`   • ${k}: ${JSON.stringify(v)}`);
        }
      }
      this.logger.info("✅ 输入数据解析成功");
      return this.inputData;
    } catch (e) {
      this.logger.error(`❌ 读取输入失败: ${e && e.message ? e.message : String(e)}`);
      this.inputData = {};
      return this.inputData;
    }
  }

  writeOutput(output) {
    try {
      const text = JSON.stringify(output);
      process.stdout.write(text);
      this.logger.info("📤 输出响应给 Cursor:");
      for (const [k, v] of Object.entries(output)) {
        if (typeof v === "string" && v.length > 100) {
          this.logger.info(`   • ${k}: ${v.slice(0, 100)}...`);
        } else {
          this.logger.info(`   • ${k}: ${JSON.stringify(v)}`);
        }
      }
    } catch (e) {
      this.logger.error(`❌ 输出响应失败: ${e && e.message ? e.message : String(e)}`);
    }
  }

  _summarizeInput() {
    const summary = {};
    const keys = [
      "conversation_id",
      "generation_id",
      "hook_event_name",
      "workspace_roots",
      "command",
      "file_path",
      "tool_name",
      "status",
      "loop_count",
    ];
    for (const k of keys) {
      if (Object.prototype.hasOwnProperty.call(this.inputData, k)) {
        const v = this.inputData[k];
        if (typeof v === "string" && v.length > 100) summary[k] = `${v.slice(0, 100)}...`;
        else summary[k] = v;
      }
    }
    return summary;
  }

  async sendToOrtensia(text, emotion = "neutral", eventType = null) {
    const conversationId = this.inputData.conversation_id || "unknown";
    const workspace =
      Array.isArray(this.inputData.workspace_roots) && this.inputData.workspace_roots.length > 0
        ? this.inputData.workspace_roots[0]
        : "unknown";
    const workspaceName = workspace !== "unknown" ? path.basename(workspace) : "unknown";

    let clientId;
    if (conversationId && conversationId !== "unknown") {
      clientId = `hook-${conversationId}`;
      this.logger.info(`✅ 使用 conversation_id: ${conversationId}`);
    } else {
      const hash = crypto.createHash("md5").update(String(workspace)).digest("hex").slice(0, 8);
      clientId = `hook-${hash}`;
      this.logger.warn(`⚠️  未找到 conversation_id，使用 workspace hash: ${clientId}`);
    }

    this.logger.info("💬 准备发送消息到オルテンシア:");
    this.logger.info(`   • Hook ID: ${clientId}`);
    this.logger.info(`   • Conversation ID: ${conversationId}`);
    this.logger.info(`   • Workspace: ${workspaceName}`);
    this.logger.info(`   • 文本: ${text}`);
    this.logger.info(`   • 情绪: ${emotion}`);
    this.logger.info(`   • 事件类型: ${eventType || this.hookName}`);
    this.logger.info(`   • WebSocket: ${this.wsServer}`);

    const wsUrl = this.wsServer;
    const WebSocketImpl = globalThis.WebSocket;
    if (typeof WebSocketImpl !== "function") {
      this.logger.error("❌ Node.js WebSocket 不可用（需要 Node 18+ 或提供 WebSocket 实现）");
      return;
    }

    const registerMsg = {
      type: "register",
      from: clientId,
      to: null,
      timestamp: Date.now(),
      payload: { client_type: "agent_hook" },
    };

    const messageData = {
      type: "aituber_receive_text",
      from: clientId,
      to: "aituber",
      timestamp: Date.now(),
      payload: {
        text,
        emotion,
        source: "hook",
        hook_name: this.hookName,
        event_type: eventType || this.hookName,
        workspace,
        workspace_name: workspaceName,
        conversation_id: conversationId,
        event_summary: this._summarizeInput(),
      },
    };

    await new Promise((resolve) => {
      let settled = false;
      const done = () => {
        if (settled) return;
        settled = true;
        resolve();
      };

      const timeout = setTimeout(() => {
        this.logger.warn("⚠️  WebSocket 发送超时（跳过）");
        done();
      }, 3000);

      try {
        const ws = new WebSocketImpl(wsUrl);

        ws.addEventListener("open", () => {
          try {
            ws.send(JSON.stringify(registerMsg));
            ws.send(JSON.stringify(messageData));
            this.logger.info("✅ 消息已发送到オルテンシア");
          } catch (e) {
            this.logger.error(`❌ 发送到オルテンシア失败: ${e && e.message ? e.message : String(e)}`);
          } finally {
            try {
              ws.close();
            } catch {
              // ignore
            }
            clearTimeout(timeout);
            done();
          }
        });

        ws.addEventListener("error", (ev) => {
          this.logger.error(`❌ WebSocket 连接失败: ${ev && ev.message ? ev.message : "error"}`);
          try {
            ws.close();
          } catch {
            // ignore
          }
          clearTimeout(timeout);
          done();
        });
      } catch (e) {
        this.logger.error(`❌ WebSocket 初始化失败: ${e && e.message ? e.message : String(e)}`);
        clearTimeout(timeout);
        done();
      }
    });
  }

  // override in subclasses
  process() {
    throw new Error("Subclasses must implement process()");
  }

  run() {
    const start = Date.now();
    try {
      this.logger.info("⏳ 步骤 1/3: 读取输入数据...");
      this.readInput();

      this.logger.info("⏳ 步骤 2/3: 执行 Hook 逻辑...");
      const output = this.process();

      this.logger.info("⏳ 步骤 3/3: 输出响应...");
      if (output && typeof output === "object" && Object.keys(output).length > 0) {
        this.writeOutput(output);
      } else {
        this.logger.info("   ℹ️  无需返回响应（审计类 hook）");
      }

      const elapsed = (Date.now() - start) / 1000;
      this.logger.info("=".repeat(70));
      this.logger.info(`✅ [${this.hookName}] Hook 执行成功`);
      this.logger.info(`⏱️  执行耗时: ${elapsed.toFixed(3)} 秒`);
      this.logger.info("=".repeat(70));
      this.logger.info("");
      return 0;
    } catch (e) {
      const elapsed = (Date.now() - start) / 1000;
      this.logger.error("=".repeat(70));
      this.logger.error(`❌ [${this.hookName}] Hook 执行失败`);
      this.logger.error(`⏱️  执行耗时: ${elapsed.toFixed(3)} 秒`);
      this.logger.error(`错误: ${e && e.message ? e.message : String(e)}`);
      this.logger.error("=".repeat(70));
      this.logger.error("");
      return 1;
    }
  }
}

class PermissionHook extends AgentHookHandler {
  // override in subclass
  makeDecision() {
    throw new Error("Subclasses must implement makeDecision()");
  }
  process() {
    this.logger.info("🔐 执行权限检查...");
    const [permission, userMsg, agentMsg] = this.makeDecision();
    this.logger.info("🔐 权限决策结果:");
    this.logger.info(`   • 决策: ${permission}`);
    if (userMsg) this.logger.info(`   • 用户消息: ${userMsg}`);
    if (agentMsg) this.logger.info(`   • Agent 消息: ${agentMsg}`);
    const out = { permission };
    if (userMsg) out.user_message = userMsg;
    if (agentMsg) out.agent_message = agentMsg;
    return out;
  }
}

class AuditHook extends AgentHookHandler {
  // override in subclass
  audit() {
    throw new Error("Subclasses must implement audit()");
  }
  process() {
    this.logger.info("📊 执行审计逻辑...");
    this.audit();
    this.logger.info("📊 审计完成");
    return {};
  }
}

class StopHook extends AgentHookHandler {
  // override in subclass
  shouldContinue() {
    throw new Error("Subclasses must implement shouldContinue()");
  }
  process() {
    const followup = this.shouldContinue();
    if (followup) return { followup_message: followup };
    return {};
  }
}

module.exports = {
  AgentHookHandler,
  PermissionHook,
  AuditHook,
  StopHook,
  getLogFilePath,
};

function readServerUrlFromFile() {
  try {
    const home = process.env.HOME || process.env.USERPROFILE || "";
    const appData = process.env.APPDATA || "";
    const localAppData = process.env.LOCALAPPDATA || "";

    const candidates = [];
    // macOS recommended path
    if (home) candidates.push(path.join(home, "Library", "Application Support", "Ortensia", "central_server.txt"));
    // Windows recommended paths
    if (appData) candidates.push(path.join(appData, "Ortensia", "central_server.txt"));
    if (localAppData) candidates.push(path.join(localAppData, "Ortensia", "central_server.txt"));
    // legacy/simple paths
    if (home) candidates.push(path.join(home, ".ortensia_server"));
    if (home) candidates.push(path.join(home, ".config", "ortensia", "central_server.txt"));

    for (const p of candidates) {
      try {
        if (!p) continue;
        if (!fs.existsSync(p)) continue;
        const url = fs.readFileSync(p, "utf8").trim();
        if (url) return url;
      } catch {
        // continue
      }
    }
  } catch {
    // ignore
  }
  return null;
}

function resolveOrtensiaServer() {
  return (
    process.env.WS_SERVER ||
    process.env.ORTENSIA_SERVER ||
    readServerUrlFromFile() ||
    "ws://localhost:8765"
  );
}

