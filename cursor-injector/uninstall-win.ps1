<#
Ortensia Cursor Injector - Windows uninstall (PowerShell wrapper)

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File .\uninstall-win.ps1

Optional:
  -CursorExe "C:\Path\To\Cursor.exe"   override Cursor location

Notes:
- Close Cursor before running, then restart Cursor after uninstall.
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

node .\uninstall-win.js

