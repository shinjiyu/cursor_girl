/**
 * Ortensia Cursor Injector - Windows uninstaller
 *
 * Restores backed up main entry file and removes sidecar injector.
 * Supports both loose resources/app and resources/app.asar layouts.
 */

const fs = require("fs");
const os = require("os");
const path = require("path");

function fileExists(p) {
  try {
    return fs.existsSync(p);
  } catch {
    return false;
  }
}

function copyFile(src, dst) {
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
}

function resolveCursorExeCandidates() {
  const candidates = [];
  const localAppData = process.env.LOCALAPPDATA || "";
  const programFiles = process.env.ProgramFiles || "";
  const programFilesX86 = process.env["ProgramFiles(x86)"] || "";

  if (localAppData) candidates.push(path.join(localAppData, "Programs", "Cursor", "Cursor.exe"));
  if (programFiles) candidates.push(path.join(programFiles, "Cursor", "Cursor.exe"));
  if (programFilesX86) candidates.push(path.join(programFilesX86, "Cursor", "Cursor.exe"));

  if (process.env.CURSOR_EXE && String(process.env.CURSOR_EXE).trim()) {
    candidates.unshift(String(process.env.CURSOR_EXE).trim());
  }

  return candidates;
}

function locateResourcesDir() {
  const candidates = resolveCursorExeCandidates();
  for (const exe of candidates) {
    if (!exe) continue;
    if (!fileExists(exe)) continue;
    const resources = path.join(path.dirname(exe), "resources");
    if (fileExists(resources)) return resources;
  }
  throw new Error(
    `Unable to locate Cursor installation. Tried:\n- ${candidates.join("\n- ")}\nSet CURSOR_EXE to override.`
  );
}

function parseMainFromPackageJson(appRootDir) {
  const pkgPath = path.join(appRootDir, "package.json");
  if (!fileExists(pkgPath)) return null;
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"));
    if (pkg && typeof pkg.main === "string" && pkg.main.trim()) return pkg.main.trim();
  } catch {
    return null;
  }
  return null;
}

function uninstallLooseApp(appRootDir) {
  const mainRel = parseMainFromPackageJson(appRootDir) || "out/main.js";
  const mainPath = path.join(appRootDir, mainRel);
  const backupPath = `${mainPath}.ortensia.backup`;

  if (!fileExists(mainPath)) throw new Error(`Main entry not found: ${mainPath}`);
  if (!fileExists(backupPath)) {
    console.log("No backup found; nothing to restore.");
    return;
  }

  copyFile(backupPath, mainPath);
  try {
    fs.rmSync(backupPath, { force: true });
  } catch {
    // ignore
  }

  const injectorPath = path.join(path.dirname(mainPath), "ortensia-injector.js");
  if (fileExists(injectorPath)) {
    try {
      fs.rmSync(injectorPath, { force: true });
    } catch {
      // ignore
    }
  }

  console.log(`✅ Restored main entry: ${mainPath}`);
}

function withTempDir(prefix, fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  try {
    return fn(dir);
  } finally {
    try {
      fs.rmSync(dir, { recursive: true, force: true });
    } catch {
      // ignore
    }
  }
}

function uninstallAsar(resourcesDir) {
  const asarPath = path.join(resourcesDir, "app.asar");
  const backupAsar = `${asarPath}.ortensia.backup`;
  if (!fileExists(asarPath)) throw new Error(`app.asar not found: ${asarPath}`);
  if (!fileExists(backupAsar)) {
    console.log("No asar backup found; nothing to restore.");
    return;
  }

  // Restore asar wholesale (simplest and safest)
  copyFile(backupAsar, asarPath);
  console.log(`✅ Restored asar: ${asarPath}`);
  return;
}

function main() {
  const resources = locateResourcesDir();
  const looseAppDir = path.join(resources, "app");

  console.log(`Resources dir: ${resources}`);

  if (fileExists(path.join(looseAppDir, "out", "main.js")) || fileExists(path.join(looseAppDir, "package.json"))) {
    uninstallLooseApp(looseAppDir);
    return;
  }

  if (fileExists(path.join(resources, "app.asar"))) {
    uninstallAsar(resources);
    return;
  }

  throw new Error(`Unsupported Cursor installation layout under: ${resources}`);
}

if (require.main === module) {
  try {
    main();
  } catch (e) {
    console.error(`❌ Uninstall failed: ${e.message}`);
    process.exit(1);
  }
}

