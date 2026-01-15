#!/usr/bin/env node
/**
 * Cross-platform Node hook runner.
 *
 * Usage:
 *   node run_hook_node.js <hook_script.js>
 *
 * We simply require() the hook script so it can execute and exit.
 */

const path = require("path");

function main(argv) {
  const hookPath = argv[2];
  if (!hookPath) {
    process.stderr.write("Usage: run_hook_node.js <hook_script.js>\n");
    return 2;
  }

  const abs = path.isAbsolute(hookPath) ? hookPath : path.resolve(process.cwd(), hookPath);
  // #region agent log (debug)
  fetch('http://127.0.0.1:7242/ingest/bdd4517c-4845-494b-847d-45eb44c85416',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'cursor-hooks/run_hook_node.js:23',message:'runner start',data:{pid:process.pid,abs},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H1'})}).catch(()=>{});
  // #endregion
  // Hook scripts are expected to call process.exit(...) themselves.
  const ret = require(abs);
  // #region agent log (debug)
  fetch('http://127.0.0.1:7242/ingest/bdd4517c-4845-494b-847d-45eb44c85416',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'cursor-hooks/run_hook_node.js:29',message:'runner required module',data:{pid:process.pid,hasThenable:!!(ret&&typeof ret.then==="function"),exportType:typeof ret},timestamp:Date.now(),sessionId:'debug-session',runId:'pre-fix',hypothesisId:'H1'})}).catch(()=>{});
  // #endregion
  if (ret && typeof ret.then === "function") {
    return ret.then((code) => (typeof code === "number" ? code : 0));
  }
  return 0;
}

Promise.resolve()
  .then(() => main(process.argv))
  .then((code) => process.exit(typeof code === "number" ? code : 0))
  .catch((err) => {
    try {
      process.stderr.write(String(err && err.stack ? err.stack : err) + "\n");
    } catch {}
    process.exit(1);
  });

