/**
 * Fake WebSocket implementation for hook unit tests.
 *
 * Inject with:
 *   NODE_OPTIONS=--require <path/to/fake_ws.js>
 *
 * Captures outbound `send()` payloads and writes them to disk on process exit.
 * This lets us assert that the hook waited long enough for the async WebSocket
 * "open -> send -> close" cycle to complete before exiting.
 */
const fs = require("fs");

function safeWriteJson(filePath, data) {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf8");
  } catch {
    // ignore
  }
}

class FakeWebSocket {
  static OPEN = 1;
  static CLOSED = 3;

  constructor(url) {
    this.url = url;
    this.readyState = 0;
    this._listeners = new Map();

    FakeWebSocket.__events.push({ type: "construct", url, at: Date.now() });

    // Simulate async connect (important: if hook doesn't await, process can exit
    // before this fires).
    setTimeout(() => {
      this.readyState = FakeWebSocket.OPEN;
      FakeWebSocket.__events.push({ type: "open", url: this.url, at: Date.now() });
      this._emit("open", {});
    }, 15);
  }

  addEventListener(type, handler) {
    if (!this._listeners.has(type)) this._listeners.set(type, new Set());
    this._listeners.get(type).add(handler);
  }

  removeEventListener(type, handler) {
    const set = this._listeners.get(type);
    if (set) set.delete(handler);
  }

  send(data) {
    FakeWebSocket.__events.push({ type: "send", url: this.url, at: Date.now(), data });
    // Simulate server register_ack so hook code can close on ack quickly.
    // (Keeps tests fast and mirrors central server behavior.)
    try {
      const obj = JSON.parse(typeof data === "string" ? data : String(data));
      if (obj && obj.type === "register") {
        setTimeout(() => {
          const ack = {
            type: "register_ack",
            from: "server",
            to: obj.from || "",
            timestamp: Date.now(),
            payload: { success: true, assigned_id: obj.from || "" },
          };
          FakeWebSocket.__events.push({ type: "message", url: this.url, at: Date.now(), data: JSON.stringify(ack) });
          this._emit("message", { data: JSON.stringify(ack) });
        }, 5);
      }
    } catch {
      // ignore
    }
  }

  close() {
    if (this.readyState === FakeWebSocket.CLOSED) return;
    this.readyState = FakeWebSocket.CLOSED;
    setTimeout(() => {
      FakeWebSocket.__events.push({ type: "close", url: this.url, at: Date.now() });
      this._emit("close", {});
    }, 5);
  }

  _emit(type, event) {
    const set = this._listeners.get(type);
    if (!set) return;
    for (const fn of Array.from(set)) {
      try {
        fn(event);
      } catch {
        // ignore
      }
    }
  }
}

// Shared capture store across the process
FakeWebSocket.__events = [];

// Install globally for the hook code to pick up
globalThis.WebSocket = FakeWebSocket;

// Persist capture on exit for the test runner to inspect
process.on("exit", () => {
  const out = process.env.FAKE_WS_CAPTURE_PATH;
  if (!out) return;
  safeWriteJson(out, {
    pid: process.pid,
    at: Date.now(),
    events: FakeWebSocket.__events,
  });
});

