# Start the Japanese-music fan site locally (server + ngrok fixed tunnel).
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File start-local.ps1
#        -Port 8789 -Data D:\jp-other\data.json -Domain other.ngrok-free.dev -NoTunnel
param(
  [int]$Port = 8788,
  [string]$Data = '',
  [string]$Domain = 'fructose-hardiness-botanist.ngrok-free.dev',
  [switch]$NoTunnel
)
$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyCandidates = @(
  (Join-Path $env:USERPROFILE '.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'),
  'C:\Users\Pkochan\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
)
$py = $pyCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $py) {
  $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
  if ($cmd) { $py = $cmd.Source }
}
if (-not $py) { Write-Host 'NO_PYTHON_FOUND'; exit 1 }
$ngrok = Join-Path $root 'tools\ngrok.exe'
$cfg = Join-Path $root 'tools\ngrok.yml'
$env:JPM_PORT = "$Port"
if ($Data -ne '') { $env:JPM_DATA = $Data }

# stop previous tunnel / server
if (-not $NoTunnel) {
  Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force
}
Get-Process -Name cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
$conn = Get-NetTCPConnection -LocalPort $Port -State Listen
if ($conn) {
  Stop-Process -Id $conn.OwningProcess -Force
  Start-Sleep -Seconds 1
}

Start-Process -FilePath $py -ArgumentList 'server.py' -WorkingDirectory $root -WindowStyle Hidden `
  -RedirectStandardOutput (Join-Path $root "server-$Port.out.log") -RedirectStandardError (Join-Path $root "server-$Port.err.log")
Start-Sleep -Seconds 2

if (-not $NoTunnel) {
  $log = Join-Path $root 'ngrok.log'
  if (Test-Path $log) { Remove-Item $log -Force }
  Start-Process -FilePath $ngrok -WorkingDirectory $root -WindowStyle Hidden `
    -ArgumentList 'http',"$Port",'--domain',$Domain,'--config',$cfg,'--log=stdout','--log-format=logfmt' `
    -RedirectStandardOutput $log -RedirectStandardError (Join-Path $root 'ngrok.err.log')
  Start-Sleep -Seconds 4
}

$local = $null
for ($i = 0; $i -lt 15; $i++) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/health" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $local = 'ok'; break }
  } catch { }
  Start-Sleep -Seconds 1
}

if (-not $NoTunnel) { Write-Host "PUBLIC_URL=https://$Domain" }
Write-Host "LOCAL=http://127.0.0.1:$Port ($local)"
Write-Host "DATA=$env:JPM_DATA"
