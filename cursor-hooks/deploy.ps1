<#
Cursor Agent Hooks deployment script (Windows / PowerShell)

Goal:
- Install hooks to a global directory under the user's home
- Generate a Windows-safe hooks.json using absolute paths (no $HOME, no symlinks)

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy.ps1

Optional:
  -Force    overwrite existing install without prompt

Notes:
- This script does NOT start/stop any services.
- Cursor may or may not need a restart to pick up hooks.json; try without restarting first.
#>

[CmdletBinding()]
param(
  [switch]$Force,
  [string]$PythonPath
)

$ErrorActionPreference = "Stop"

function Get-UserHome {
  $home = [Environment]::GetFolderPath("UserProfile")
  if ([string]::IsNullOrWhiteSpace($home)) {
    throw "Unable to resolve user profile directory."
  }
  return $home
}

function Write-Info([string]$msg) { Write-Host $msg }
function Write-Warn([string]$msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Ok([string]$msg)   { Write-Host $msg -ForegroundColor Green }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = Get-UserHome

$TargetDir = Join-Path $HomeDir ".cursor-agent"
$CursorDir = Join-Path $HomeDir ".cursor"
$HooksDir  = Join-Path $TargetDir "hooks"
$LibDir    = Join-Path $TargetDir "lib"
$CursorHooksJson = Join-Path $CursorDir "hooks.json"
$TargetHooksJson = Join-Path $TargetDir "hooks.json"

Write-Info ""
Write-Info "== Cursor Agent Hooks Deploy (Windows) =="
Write-Info ("Source:  {0}" -f $ScriptDir)
Write-Info ("Target:  {0}" -f $TargetDir)
Write-Info ("Cursor:  {0}" -f $CursorDir)
Write-Info ""

if (Test-Path $TargetDir) {
  if (-not $Force) {
    $resp = Read-Host "$TargetDir already exists. Overwrite? (y/N)"
    if ($resp -notmatch "^[Yy]$") {
      Write-Warn "Cancelled."
      exit 0
    }
  }
  Remove-Item -Recurse -Force $TargetDir
}

New-Item -ItemType Directory -Force -Path $HooksDir | Out-Null
New-Item -ItemType Directory -Force -Path $LibDir | Out-Null
New-Item -ItemType Directory -Force -Path $CursorDir | Out-Null

# Copy hooks + libs
Copy-Item -Recurse -Force (Join-Path $ScriptDir "hooks\*") $HooksDir
Copy-Item -Recurse -Force (Join-Path $ScriptDir "lib\*") $LibDir

# Copy runners
Copy-Item -Force (Join-Path $ScriptDir "run_hook.py") (Join-Path $TargetDir "run_hook.py")
if (Test-Path (Join-Path $ScriptDir "run_hook.sh")) {
  Copy-Item -Force (Join-Path $ScriptDir "run_hook.sh") (Join-Path $TargetDir "run_hook.sh")
}

# Determine python command for hooks.json:
# - Prefer explicit -PythonPath if provided
# - Else prefer python on PATH; fallback to py -3 if available
$pythonCmd = $null
if ($PythonPath) {
  if (-not (Test-Path $PythonPath)) {
    throw "PythonPath does not exist: $PythonPath"
  }
  $pythonCmd = "`"$PythonPath`""
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pythonCmd = "py -3"
} else {
  $pythonCmd = "python"
  Write-Warn "python/py not found on PATH. hooks may fail until Python is installed/configured."
}

function New-HookCommand([string]$hookPyPath) {
  # Quote paths for cmd/PowerShell compatibility.
  $runner = (Join-Path $TargetDir "run_hook.py")
  return "$pythonCmd `"$runner`" `"$hookPyPath`""
}

$hooks = @{
  beforeShellExecution = @(@{ command = (New-HookCommand (Join-Path $HooksDir "beforeShellExecution.py")) })
  afterShellExecution  = @(@{ command = (New-HookCommand (Join-Path $HooksDir "afterShellExecution.py")) })
  beforeMCPExecution   = @(@{ command = (New-HookCommand (Join-Path $HooksDir "beforeMCPExecution.py")) })
  afterMCPExecution    = @(@{ command = (New-HookCommand (Join-Path $HooksDir "afterMCPExecution.py")) })
  afterFileEdit        = @(@{ command = (New-HookCommand (Join-Path $HooksDir "afterFileEdit.py")) })
  beforeReadFile       = @(@{ command = (New-HookCommand (Join-Path $HooksDir "beforeReadFile.py")) })
  beforeSubmitPrompt   = @(@{ command = (New-HookCommand (Join-Path $HooksDir "beforeSubmitPrompt.py")) })
  afterAgentResponse   = @(@{ command = (New-HookCommand (Join-Path $HooksDir "afterAgentResponse.py")) })
  stop                 = @(@{ command = (New-HookCommand (Join-Path $HooksDir "stop.py")) })
}

$hooksJsonObj = @{
  version = 1
  hooks   = $hooks
}

$json = $hooksJsonObj | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $TargetHooksJson -Encoding utf8

# Backup existing Cursor hooks.json, then write
if (Test-Path $CursorHooksJson) {
  $backup = "$CursorHooksJson.backup"
  Copy-Item -Force $CursorHooksJson $backup
  Write-Warn ("Backed up existing hooks.json to: {0}" -f $backup)
}
$json | Out-File -FilePath $CursorHooksJson -Encoding utf8

Write-Ok "Deployed successfully."
Write-Info ("- Installed hooks at: {0}" -f $TargetDir)
Write-Info ("- Cursor config at:   {0}" -f $CursorHooksJson)
Write-Info ""
Write-Info "Tip: Log file default is OS temp dir (search for cursor-agent-hooks.log), or set CURSOR_AGENT_HOOKS_LOG."
Write-Info ""

