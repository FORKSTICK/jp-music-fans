$ErrorActionPreference = 'SilentlyContinue'
$root = 'D:\DeepSeekHarness\default-workspace\jp-music-fans'
$py = 'C:\Users\Pkochan\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe'
$pids = Get-NetTCPConnection -LocalPort 8788 -State Listen | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) { Stop-Process -Id $p -Force }
Start-Sleep -Seconds 2
Start-Process -FilePath $py -ArgumentList 'server.py' -WorkingDirectory $root -WindowStyle Hidden
Start-Sleep -Seconds 3
"restarted"
