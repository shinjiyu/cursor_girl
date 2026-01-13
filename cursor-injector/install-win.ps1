<#
Ortensia Cursor Injector - Windows install (PowerShell wrapper)

This patches Cursor's main process entry (loose app/out/main.js or app.asar) to load Ortensia.

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\install-win.ps1

Optional:
  -CursorExe "C:\Path\To\Cursor.exe"   override Cursor location

Notes:
- Close Cursor before running, then restart Cursor after install.
#>

[CmdletBinding()]
param(
  [string]$CursorExe
)

$ErrorActionPreference = "Stop"

if ($CursorExe) {
  $env:CURSOR_EXE = $CursorExe
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

node .\install-win.js

