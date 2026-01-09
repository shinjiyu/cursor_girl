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
  // Hook scripts are expected to call process.exit(...) themselves.
  require(abs);
  return 0;
}

process.exit(main(process.argv));

