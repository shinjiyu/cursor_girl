// ============================================================================
// Ortensia Cursor Injector (main-process sidecar)
// Loaded by a tiny loader prepended into Cursor's main entry JS.
// ============================================================================
(async function () {
  const fs = await import("fs");
  const os = await import("os");
  const path = await import("path");

  const LOG =
    (process.env.CURSOR_ORTENSIA_LOG && String(process.env.CURSOR_ORTENSIA_LOG).trim()) ||
    path.join(os.tmpdir(), "cursor_ortensia.log");

  function log(msg) {
    const line = `[${new Date().toISOString()}] [PID:${process.pid}] ${msg}\n`;
    try {
      fs.appendFileSync(LOG, line);
      console.log(`[ORTENSIA] ${msg}`);
    } catch (e) {
      try {
        console.error("[ORTENSIA] Log error:", e);
      } catch {
        // ignore
      }
    }
  }

  // Wait Electron to initialize a bit
  await new Promise((resolve) => setTimeout(resolve, 3000));

  // --------------------------------------------------------------------------
  // Central server URL resolution (aligned with hooks)
  // Priority: WS_SERVER > ORTENSIA_SERVER > global file > default
  // --------------------------------------------------------------------------
  function readCentralServerFromFile() {
    try {
      const home = os.homedir();
      const appData = process.env.APPDATA ? String(process.env.APPDATA) : null;
      const localAppData = process.env.LOCALAPPDATA ? String(process.env.LOCALAPPDATA) : null;

      const candidates = [
        // macOS recommended
        path.join(home, "Library", "Application Support", "Ortensia", "central_server.txt"),
        // Windows recommended
        ...(appData ? [path.join(appData, "Ortensia", "central_server.txt")] : []),
        ...(localAppData ? [path.join(localAppData, "Ortensia", "central_server.txt")] : []),
        // generic
        path.join(home, ".ortensia_server"),
        path.join(home, ".config", "ortensia", "central_server.txt"),
        // project-local (optional)
        path.join(process.cwd(), ".ortensia", "central_server.txt"),
      ];

      for (const p of candidates) {
        try {
          if (!fs.existsSync(p)) continue;
          const raw = fs.readFileSync(p, "utf8");
          const url = (raw || "").trim();
          if (url) return { url, path: p };
        } catch {
          // ignore
        }
      }
    } catch {
      // ignore
    }
    return null;
  }

  const DEFAULT_CENTRAL_SERVER_URL = "ws://localhost:8765";
  let CENTRAL_SERVER_URL = null;
  let CENTRAL_SERVER_SOURCE = null;

  if (process.env.WS_SERVER && String(process.env.WS_SERVER).trim()) {
    CENTRAL_SERVER_URL = String(process.env.WS_SERVER).trim();
    CENTRAL_SERVER_SOURCE = "env:WS_SERVER";
  } else if (process.env.ORTENSIA_SERVER && String(process.env.ORTENSIA_SERVER).trim()) {
    CENTRAL_SERVER_URL = String(process.env.ORTENSIA_SERVER).trim();
    CENTRAL_SERVER_SOURCE = "env:ORTENSIA_SERVER";
  } else {
    const fileCfg = readCentralServerFromFile();
    if (fileCfg && fileCfg.url) {
      CENTRAL_SERVER_URL = fileCfg.url;
      CENTRAL_SERVER_SOURCE = `file:${fileCfg.path}`;
    }
  }

  if (!CENTRAL_SERVER_URL) {
    CENTRAL_SERVER_URL = DEFAULT_CENTRAL_SERVER_URL;
    CENTRAL_SERVER_SOURCE = "default";
  }

  log("========================================");
  log("🎉 Ortensia Injector 启动中...");
  log(`进程 ID: ${process.pid}`);
  log(`🌐 Central Server: ${CENTRAL_SERVER_URL} (${CENTRAL_SERVER_SOURCE})`);
  log(`📝 Log file: ${LOG}`);

  // --------------------------------------------------------------------------
  // WebSocket plumbing (kept compatible with existing v10/v11.x tooling)
  // - local WS server: 9876 (dev/debug)
  // - central WS client: 8765 (routing)
  // --------------------------------------------------------------------------
  try {
    const ws_module = await import("ws");
    const WebSocketServer = ws_module.WebSocketServer || ws_module.Server;
    const WebSocketClient = ws_module.default || ws_module.WebSocket || ws_module;

    log("✅ WebSocket 模块加载成功");

    // Local server (9876)
    log("📡 启动本地 WebSocket Server (端口 9876)...");
    const localServer = new WebSocketServer({ port: 9876 });

    localServer.on("listening", () => {
      log("");
      log("══════════════════════════════════════════════════════════════");
      log("  ✅ 本地 WebSocket Server 启动成功！");
      log("  📍 端口: 9876");
      log("══════════════════════════════════════════════════════════════");
      log("");
    });

    localServer.on("connection", (ws) => {
      log("🔗 [本地] 客户端已连接");

      ws.on("message", async (message) => {
        try {
          const code = message.toString();
          log(`📥 [本地] 收到代码: ${code.substring(0, 50)}...`);

          let result = eval(code);
          if (result && typeof result.then === "function") {
            result = await result;
          }

          ws.send(JSON.stringify({ success: true, result: String(result) }));
          log(`✅ [本地] 执行成功: ${String(result).substring(0, 100)}`);
        } catch (error) {
          log(`❌ [本地] 执行错误: ${error.message}`);
          ws.send(JSON.stringify({ success: false, error: error.message }));
        }
      });

      ws.on("close", () => log("🔌 [本地] 客户端断开连接"));
    });

    localServer.on("error", (error) => {
      if (error.code === "EADDRINUSE") {
        log("⚠️  [本地] 端口 9876 已被占用，跳过本地Server");
      } else {
        log(`❌ [本地] Server 错误: ${error.message}`);
      }
    });

    // Central client (8765)
    let centralWs = null;
    const injectId = `inject-${process.pid}`;

    function sendToCentral(message) {
      if (centralWs && centralWs.readyState === 1) {
        try {
          const messageStr = typeof message === "string" ? message : JSON.stringify(message);
          centralWs.send(messageStr);
          log(`📤 [中央] 发送: ${messageStr.substring(0, 100)}...`);
          return true;
        } catch (error) {
          log(`❌ [中央] 发送失败: ${error.message}`);
          return false;
        }
      } else {
        log(`⚠️  [中央] WebSocket 未连接 (readyState: ${centralWs ? centralWs.readyState : "null"})`);
        return false;
      }
    }

    async function getWorkspacePath() {
      try {
        const electron = await import("electron");
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length > 0) return process.cwd();
      } catch {
        // ignore
      }
      return process.cwd();
    }

    async function register() {
      const workspace = await getWorkspacePath();
      const registerMessage = {
        type: "register",
        from: injectId,
        to: "server",
        timestamp: Math.floor(Date.now() / 1000),
        payload: {
          client_type: "cursor_inject",
          inject_id: injectId,
          workspace: workspace,
          platform: process.platform,
          pid: process.pid,
          ws_port: 9876,
          capabilities: ["composer", "editor", "terminal", "conversation_id"],
        },
      };
      sendToCentral(registerMessage);
    }

    async function handleExecuteJs(fromId, payload) {
      const code = payload.code || "";
      const requestId = payload.request_id || "unknown";
      const windowIndex = payload.window_index;
      const conversationId = payload.conversation_id;

      log(
        `🔧 [ExecuteJS] 收到执行请求: ${String(requestId).substring(0, 30)}... (from=${fromId}, window_index=${windowIndex}, conversation_id=${conversationId ? String(conversationId).substring(0, 8) : "null"})`
      );

      try {
        const electron = await import("electron");
        const windows = electron.BrowserWindow.getAllWindows();
        if (windows.length === 0) throw new Error("没有打开的窗口");

        let result;
        let targetIndex = null;

        if (windowIndex !== null && windowIndex !== undefined) {
          if (windowIndex < 0 || windowIndex >= windows.length) {
            throw new Error(`窗口索引超出范围: ${windowIndex} (总共 ${windows.length} 个窗口)`);
          }
          targetIndex = windowIndex;
          log(`📍 [单播-索引] 使用窗口 [${targetIndex}]`);
        } else if (conversationId) {
          log(`🔍 [单播-查找] 查找 conversation_id: ${conversationId}`);
          const extractConvIdCode =
            '(() => { const el = document.querySelector(\'[id^="composer-bottom-add-context-"]\'); if (!el) return JSON.stringify({ found: false }); const match = el.id.match(/composer-bottom-add-context-([a-f0-9-]+)/); return JSON.stringify({ found: true, conversation_id: match ? match[1] : null }); })()';

          for (let i = 0; i < windows.length; i++) {
            try {
              const convResult = await windows[i].webContents.executeJavaScript(extractConvIdCode);
              const convData = JSON.parse(convResult);
              const windowConvId = convData.found && convData.conversation_id ? convData.conversation_id : null;
              log(`  窗口 [${i}]: conversation_id = ${windowConvId}`);
              if (windowConvId === conversationId) {
                targetIndex = i;
                log(`✅ [单播-查找] 找到匹配窗口: [${i}]`);
                break;
              }
            } catch (err) {
              log(`  ⚠️  窗口 [${i}] 查询失败: ${err.message}`);
            }
          }

          if (targetIndex === null) throw new Error(`未找到 conversation_id 为 ${conversationId} 的窗口`);
        }

        if (targetIndex !== null) {
          const targetWindow = windows[targetIndex];
          result = await targetWindow.webContents.executeJavaScript(code);
        } else {
          log(`📢 [广播模式] 在所有 ${windows.length} 个窗口执行`);
          const results = {};
          for (let i = 0; i < windows.length; i++) {
            try {
              const windowResult = await windows[i].webContents.executeJavaScript(code);
              results[i] = windowResult;
              log(`  ✅ 窗口 [${i}] 执行成功`);
            } catch (err) {
              results[i] = { error: err.message };
              log(`  ❌ 窗口 [${i}] 执行失败: ${err.message}`);
            }
          }
          result = results;
        }

        let parsedResult;
        try {
          parsedResult = JSON.parse(result);
        } catch {
          parsedResult = result;
        }

        sendToCentral({
          type: "execute_js_result",
          from: injectId,
          to: fromId,
          timestamp: Math.floor(Date.now() / 1000),
          payload: { success: true, result: parsedResult, request_id: requestId },
        });

        log(`✅ [ExecuteJS] 执行成功: ${requestId}`);
      } catch (error) {
        log(`❌ [ExecuteJS] 执行错误: ${error.message}`);
        sendToCentral({
          type: "execute_js_result",
          from: injectId,
          to: fromId,
          timestamp: Math.floor(Date.now() / 1000),
          payload: { success: false, error: error.message, request_id: requestId },
        });
      }
    }

    async function handleCommand(message) {
      const { type, from, payload } = message;
      if (type === "execute_js") {
        await handleExecuteJs(from, payload || {});
      } else {
        // ignore unknown messages for now
      }
    }

    let reconnectTimeout = null;
    let reconnectDelay = 1000;
    const MAX_RECONNECT_DELAY = 60000;

    function scheduleReconnect() {
      if (reconnectTimeout) return;
      reconnectTimeout = setTimeout(() => {
        reconnectTimeout = null;
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
        connectToCentral();
      }, reconnectDelay);
      log(`⏳ [中央] ${reconnectDelay}ms 后重连...`);
    }

    function connectToCentral() {
      try {
        log("");
        log("══════════════════════════════════════════════════════════════");
        log("  🌐 连接到中央Server...");
        log(`  📍 地址: ${CENTRAL_SERVER_URL}`);
        log("══════════════════════════════════════════════════════════════");
        log("");

        centralWs = new WebSocketClient(CENTRAL_SERVER_URL);

        centralWs.on("open", async () => {
          reconnectDelay = 1000;
          await register();
        });

        centralWs.on("message", async (data) => {
          try {
            const text = data.toString();
            const msg = JSON.parse(text);
            await handleCommand(msg);
          } catch (e) {
            log(`❌ [中央] 消息处理失败: ${e.message}`);
          }
        });

        centralWs.on("close", () => {
          log("🔌 [中央] 连接已断开");
          scheduleReconnect();
        });

        centralWs.on("error", (error) => {
          log(`❌ [中央] 连接错误: ${error.message}`);
        });
      } catch (error) {
        log(`❌ [中央] 连接失败: ${error.message}`);
        scheduleReconnect();
      }
    }

    connectToCentral();

    log("");
    log("══════════════════════════════════════════════════════════════");
    log("  🎉 Ortensia Injector 初始化完成！");
    log("  ✅ 本地 Server: ws://localhost:9876");
    log(`  ✅ 中央 Server: ${CENTRAL_SERVER_URL}`);
    log(`  ✅ Inject ID: ${injectId}`);
    log("══════════════════════════════════════════════════════════════");
    log("");
  } catch (error) {
    log(`❌ 初始化失败: ${error.message}`);
    log(error.stack || String(error));
  }
})();

