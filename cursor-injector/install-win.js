/**
 * Ortensia Cursor Injector - Windows installer
 *
 * Strategy:
 * - Locate Cursor resources directory
 * - If resources/app/out/main.js exists: patch it directly
 * - Else if resources/app.asar exists: extract -> patch -> repack (backup original asar)
 *
 * Patch method (same idea as macOS script):
 * - Create a backup of the target main entry file (".ortensia.backup")
 * - Restore from backup (idempotent)
 * - Create a new main entry file: [INJECTED_CODE] + [ORIGINAL_MAIN]
 */

const fs = require("fs");
const os = require("os");
const path = require("path");

const INJECT_MARKER = "ORTENSIA_INJECT_START";

function buildInjectedMain(originalMain) {
  const injectorSrc = path.join(__dirname, "ortensia-injector.js");
  const injected = readText(injectorSrc);
  return (
    `// === ${INJECT_MARKER} ===\n` +
    injected +
    `\n// === ${INJECT_MARKER}_ORIGINAL_MAIN ===\n` +
    originalMain
  );
}

function fileExists(p) {
  try {
    return fs.existsSync(p);
  } catch {
    return false;
  }
}

function readText(p) {
  return fs.readFileSync(p, "utf8");
}

function writeText(p, text) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, text, { encoding: "utf8" });
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

  // Allow override
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
    const pkg = JSON.parse(readText(pkgPath));
    if (pkg && typeof pkg.main === "string" && pkg.main.trim()) return pkg.main.trim();
  } catch {
    return null;
  }
  return null;
}

function patchLooseApp(appRootDir) {
  // Find main entry
  const mainRel = parseMainFromPackageJson(appRootDir) || "out/main.js";
  const mainPath = path.join(appRootDir, mainRel);
  if (!fileExists(mainPath)) {
    throw new Error(`Could not find main entry at: ${mainPath}`);
  }

  const backupPath = `${mainPath}.ortensia.backup`;
  if (!fileExists(backupPath)) {
    copyFile(mainPath, backupPath);
  }

  // Always restore from backup first (idempotent), then re-inject
  const original = readText(backupPath);

  // If current main already contains marker, we still rebuild from backup to avoid drift.
  writeText(mainPath, buildInjectedMain(original));

  console.log(`✅ Patched main entry (inline inject): ${mainPath}`);
  console.log(`✅ Backup preserved:                  ${backupPath}`);
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

function patchAsar(resourcesDir) {
  const asarPath = path.join(resourcesDir, "app.asar");
  if (!fileExists(asarPath)) throw new Error(`app.asar not found at ${asarPath}`);

  let asar;
  try {
    // Prefer local node_modules resolution from repo root
    asar = require("asar");
  } catch (e) {
    throw new Error(`Missing 'asar' dependency. Run 'npm install' at repo root. Original error: ${e.message}`);
  }

  const backupAsar = `${asarPath}.ortensia.backup`;
  if (!fileExists(backupAsar)) copyFile(asarPath, backupAsar);

  withTempDir("ortensia-asar-", (tmp) => {
    const extracted = path.join(tmp, "app");
    asar.extractAll(asarPath, extracted);

    patchLooseApp(extracted);

    const newAsar = path.join(tmp, "app.asar");
    asar.createPackage(extracted, newAsar);
    copyFile(newAsar, asarPath);
  });

  console.log(`✅ Patched asar: ${asarPath}`);
  console.log(`✅ Asar backup:  ${backupAsar}`);
}

function main() {
  const resources = locateResourcesDir();
  const looseAppDir = path.join(resources, "app");

  console.log(`Resources dir: ${resources}`);

  if (fileExists(path.join(looseAppDir, "out", "main.js")) || fileExists(path.join(looseAppDir, "package.json"))) {
    patchLooseApp(looseAppDir);
    return;
  }

  if (fileExists(path.join(resources, "app.asar"))) {
    patchAsar(resources);
    return;
  }

  throw new Error(`Unsupported Cursor installation layout under: ${resources}`);
}

if (require.main === module) {
  try {
    main();
  } catch (e) {
    console.error(`❌ Install failed: ${e.message}`);
    process.exit(1);
  }
}

