#!/usr/bin/env node
/**
 * afterFileEdit (Node)
 */

const path = require("path");
const { spawnSync } = require("child_process");
const { AuditHook } = require(path.join(__dirname, "..", "agent_hook_handler"));

class AfterFileEditHook extends AuditHook {
  constructor() {
    super("afterFileEdit");
  }

  static FORMATTERS = {
    ".py": ["black", "--quiet"],
    ".js": ["prettier", "--write"],
    ".ts": ["prettier", "--write"],
    ".tsx": ["prettier", "--write"],
    ".jsx": ["prettier", "--write"],
    ".json": ["prettier", "--write"],
    ".css": ["prettier", "--write"],
    ".md": ["prettier", "--write"],
  };

  audit() {
    const filePath = this.inputData.file_path || "";
    if (!filePath) return;

    const fileName = path.basename(filePath);
    const ext = path.extname(filePath);

    this.sendToOrtensia(`Agent 编辑了文件：${fileName}`, "neutral").catch(() => {});

    const formatter = AfterFileEditHook.FORMATTERS[ext];
    if (!formatter) return;

    try {
      const cmd = [...formatter, filePath];
      const res = spawnSync(cmd[0], cmd.slice(1), {
        encoding: "utf8",
        timeout: 10_000,
        windowsHide: true,
      });
      if (res && res.status === 0) {
        this.sendToOrtensia(`文件已自动格式化：${fileName}`, "happy").catch(() => {});
      }
    } catch (e) {
      this.logger.warn(`格式化失败: ${e && e.message ? e.message : String(e)}`);
    }
  }
}

process.exit(new AfterFileEditHook().run());

