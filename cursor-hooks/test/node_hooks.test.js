const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

function mkTmpFile(name) {
  return path.join(os.tmpdir(), `${name}-${Date.now()}-${Math.random().toString(16).slice(2)}.json`);
}

function runHook({ hookScriptRel, input }) {
  const repoRoot = path.resolve(__dirname, "..");
  const runner = path.join(repoRoot, "run_hook_node.js");
  const hookScript = path.join(repoRoot, hookScriptRel);
  const capturePath = mkTmpFile("ortensia-fakews");

  const fakeWs = path.join(__dirname, "fake_ws.js");

  const env = {
    ...process.env,
    // Force the hook to use our in-memory WS and a known URL
    WS_SERVER: "ws://unit-test.local:8765",
    // Prevent polluting user's main temp log (still ok if it writes)
    CURSOR_AGENT_HOOKS_LOG: mkTmpFile("cursor-agent-hooks-test.log"),
    // Where our fake WebSocket will dump captured send() calls on process exit
    FAKE_WS_CAPTURE_PATH: capturePath,
    // Inject fake WebSocket into the hook process
    NODE_OPTIONS: `--require ${fakeWs}`,
  };

  const res = spawnSync(process.execPath, [runner, hookScript], {
    env,
    input: JSON.stringify(input),
    encoding: "utf8",
    timeout: 10_000,
    windowsHide: true,
  });

  let capture = null;
  if (fs.existsSync(capturePath)) {
    capture = JSON.parse(fs.readFileSync(capturePath, "utf8"));
  }

  // #region agent log (debug)
  fetch('http://127.0.0.1:7242/ingest/bdd4517c-4845-494b-847d-45eb44c85416',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'cursor-hooks/test/node_hooks.test.js:46',message:'runHook result',data:{status:res.status,signal:res.signal,stderrBytes:res.stderr?res.stderr.length:0,stdoutBytes:res.stdout?res.stdout.length:0,hasCapture:!!capture,captureEvents:capture&&Array.isArray(capture.events)?capture.events.length:null,firstEvent:capture&&Array.isArray(capture.events)&&capture.events[0]?capture.events[0].type:null,runner,hookScript,wsServer:env.WS_SERVER,nodeOptions:env.NODE_OPTIONS?true:false},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H1'})}).catch(()=>{});
  // #endregion

  return { res, capture, capturePath };
}

function getSentMessages(capture) {
  if (!capture || !Array.isArray(capture.events)) return [];
  return capture.events
    .filter((e) => e && e.type === "send" && typeof e.data === "string")
    .map((e) => {
      try {
        return JSON.parse(e.data);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

test("hook sends register + aituber_receive_text before exit (afterShellExecution)", () => {
  const conversationId = "5709fb54-1dc1-453c-8261-b26b86a85a5d";
  const { res, capture } = runHook({
    hookScriptRel: path.join("lib-node", "hooks", "afterShellExecution.js"),
    input: {
      conversation_id: conversationId,
      hook_event_name: "afterShellExecution",
      command: "echo hello",
      output: "hello",
      exit_code: 0,
      workspace_roots: ["C:\\Users\\Administrator\\Documents\\workspace\\cursor_girl"],
    },
  });

  assert.equal(res.status, 0, `hook exited non-zero. stderr=${res.stderr}`);

  const sent = getSentMessages(capture);
  assert.ok(sent.length >= 2, "expected at least 2 websocket send() calls (register + message)");

  const types = sent.map((m) => m.type);
  assert.ok(types.includes("register"), "missing register message");
  assert.ok(types.includes("aituber_receive_text"), "missing aituber_receive_text message");

  const msg = sent.find((m) => m.type === "aituber_receive_text");
  assert.equal(msg.from, `hook-${conversationId}`);
  assert.equal(msg.to, "aituber");
  assert.equal(typeof msg.timestamp, "number");
  assert.equal(msg.payload.conversation_id, conversationId);
  assert.equal(msg.payload.source, "hook");
});

test("stop hook awaits sendToOrtensia (completed)", () => {
  const conversationId = "5709fb54-1dc1-453c-8261-b26b86a85a5d";
  const { res, capture } = runHook({
    hookScriptRel: path.join("lib-node", "hooks", "stop.js"),
    input: {
      conversation_id: conversationId,
      hook_event_name: "stop",
      status: "completed",
      loop_count: 0,
      workspace_roots: ["C:\\Users\\Administrator\\Documents\\workspace\\cursor_girl"],
    },
  });

  assert.equal(res.status, 0, `hook exited non-zero. stderr=${res.stderr}`);

  const sent = getSentMessages(capture);
  assert.ok(sent.some((m) => m.type === "register"), "missing register message");
  assert.ok(sent.some((m) => m.type === "aituber_receive_text"), "missing aituber_receive_text message");
});

