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
  [string]$PythonPath,
  [ValidateSet("auto", "python", "node")]
  [string]$Runtime = "auto"
)

$ErrorActionPreference = "Stop"

function Get-UserHome {
  $userHome = [Environment]::GetFolderPath("UserProfile")
  if ([string]::IsNullOrWhiteSpace($userHome)) {
    throw "Unable to resolve user profile directory."
  }
  return $userHome
}

function Write-Info([string]$msg) { Write-Host $msg }
function Write-Warn([string]$msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-Ok([string]$msg)   { Write-Host $msg -ForegroundColor Green }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = Get-UserHome

$TargetDir = Join-Path $HomeDir ".cursor-agent"
$CursorDir = Join-Path $HomeDir ".cursor"
$HooksDir  = Join-Path $TargetDir "hooks"
$HooksNodeDir  = Join-Path $TargetDir "hooks-node"
$LibDir    = Join-Path $TargetDir "lib"
$LibNodeDir    = Join-Path $TargetDir "lib-node"
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
New-Item -ItemType Directory -Force -Path $HooksNodeDir | Out-Null
New-Item -ItemType Directory -Force -Path $LibNodeDir | Out-Null
New-Item -ItemType Directory -Force -Path $CursorDir | Out-Null

# Copy hooks + libs
Copy-Item -Recurse -Force (Join-Path $ScriptDir "hooks\*") $HooksDir
Copy-Item -Recurse -Force (Join-Path $ScriptDir "lib\*") $LibDir
if (Test-Path (Join-Path $ScriptDir "hooks-node")) {
  Copy-Item -Recurse -Force (Join-Path $ScriptDir "hooks-node\*") $HooksNodeDir
}
if (Test-Path (Join-Path $ScriptDir "lib-node")) {
  Copy-Item -Recurse -Force (Join-Path $ScriptDir "lib-node\*") $LibNodeDir
}

# Copy runners
Copy-Item -Force (Join-Path $ScriptDir "run_hook.py") (Join-Path $TargetDir "run_hook.py")
if (Test-Path (Join-Path $ScriptDir "run_hook_node.js")) {
  Copy-Item -Force (Join-Path $ScriptDir "run_hook_node.js") (Join-Path $TargetDir "run_hook_node.js")
}
if (Test-Path (Join-Path $ScriptDir "run_hook.sh")) {
  Copy-Item -Force (Join-Path $ScriptDir "run_hook.sh") (Join-Path $TargetDir "run_hook.sh")
}

# Determine runtime for hooks.json:
# - auto: prefer python if available else node
# - python: requires python
# - node: requires node

$hasPython = $false
$hasPyLauncher = $false
$hasNode = $false

if (Get-Command python -ErrorAction SilentlyContinue) { $hasPython = $true }
if (Get-Command py -ErrorAction SilentlyContinue) { $hasPyLauncher = $true }
if (Get-Command node -ErrorAction SilentlyContinue) { $hasNode = $true }

if ($Runtime -eq "auto") {
  if ($PythonPath -or $hasPython -or $hasPyLauncher) {
    $Runtime = "python"
  } elseif ($hasNode) {
    $Runtime = "node"
  } else {
    throw "No runtime found. Install Python or Node.js."
  }
}

$pythonCmd = $null
if ($Runtime -eq "python" -and $PythonPath) {
  if (-not (Test-Path $PythonPath)) {
    throw "PythonPath does not exist: $PythonPath"
  }
  $pythonCmd = "`"$PythonPath`""
} elseif ($Runtime -eq "python" -and (Get-Command python -ErrorAction SilentlyContinue)) {
  $pythonCmd = "python"
} elseif ($Runtime -eq "python" -and (Get-Command py -ErrorAction SilentlyContinue)) {
  $pythonCmd = "py -3"
} elseif ($Runtime -eq "python") {
  throw "python/py not found on PATH. Install Python, or re-run with -Runtime node."
}

function New-PythonHookCommand([string]$hookPyPath) {
  $runner = (Join-Path $TargetDir "run_hook.py")
  return "$pythonCmd `"$runner`" `"$hookPyPath`""
}

function New-NodeHookCommand([string]$hookJsPath) {
  $runner = (Join-Path $TargetDir "run_hook_node.js")
  if (-not (Test-Path $runner)) {
    throw "run_hook_node.js not found at $runner"
  }
  if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "node not found on PATH. Install Node.js or use -Runtime python."
  }
  return "node `"$runner`" `"$hookJsPath`""
}

if ($Runtime -eq "python") {
  $hooks = @{
    beforeShellExecution = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "beforeShellExecution.py")) })
    afterShellExecution  = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "afterShellExecution.py")) })
    beforeMCPExecution   = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "beforeMCPExecution.py")) })
    afterMCPExecution    = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "afterMCPExecution.py")) })
    afterFileEdit        = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "afterFileEdit.py")) })
    beforeReadFile       = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "beforeReadFile.py")) })
    beforeSubmitPrompt   = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "beforeSubmitPrompt.py")) })
    afterAgentResponse   = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "afterAgentResponse.py")) })
    stop                 = @(@{ command = (New-PythonHookCommand (Join-Path $HooksDir "stop.py")) })
  }
} elseif ($Runtime -eq "node") {
  $hooks = @{
    beforeShellExecution = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "beforeShellExecution.js")) })
    afterShellExecution  = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "afterShellExecution.js")) })
    beforeMCPExecution   = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "beforeMCPExecution.js")) })
    afterMCPExecution    = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "afterMCPExecution.js")) })
    afterFileEdit        = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "afterFileEdit.js")) })
    beforeReadFile       = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "beforeReadFile.js")) })
    beforeSubmitPrompt   = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "beforeSubmitPrompt.js")) })
    afterAgentResponse   = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "afterAgentResponse.js")) })
    stop                 = @(@{ command = (New-NodeHookCommand (Join-Path $HooksNodeDir "stop.js")) })
  }
} else {
  throw "Invalid Runtime: $Runtime"
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
Write-Info ("- Runtime:           {0}" -f $Runtime)
Write-Info ""
Write-Info "Tip: Log file default is OS temp dir (search for cursor-agent-hooks.log), or set CURSOR_AGENT_HOOKS_LOG."
Write-Info ""

