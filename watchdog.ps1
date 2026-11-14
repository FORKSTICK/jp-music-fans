# Watchdog: if local server or ngrok is down, relaunch start-local.ps1.
$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $root 'start-local.ps1'

$localOk = $false
try {
  $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8788/api/health' -UseBasicParsing -TimeoutSec 3
  $localOk = ($r.StatusCode -eq 200)
} catch { $localOk = $false }

$ngrokOk = [bool](Get-Process -Name ngrok -ErrorAction SilentlyContinue)

if (-not $localOk -or -not $ngrokOk) {
  Add-Content -Path (Join-Path $root 'watchdog.log') -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + " restart local=$localOk ngrok=$ngrokOk")
  Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File',$script -WindowStyle Hidden
}
