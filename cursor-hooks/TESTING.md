# Hook Tests (Node.js)

This folder contains a small unit test suite that verifies **Node.js hooks do not exit before their async WebSocket send completes**.

## Requirements

- Node.js **18+** (for `node:test`)

## Run

From repo root:

```bash
node --test cursor-hooks/test/node_hooks.test.js
```

## How it works

- The test runner spawns a hook in a child Node process (same way Cursor runs hooks).
- We inject a **fake `globalThis.WebSocket`** using:
  - `NODE_OPTIONS=--require cursor-hooks/test/fake_ws.js`
- The fake WebSocket delays its `open` event, so if the hook doesn't `await sendToOrtensia()`, the process exits too early and the test fails.

