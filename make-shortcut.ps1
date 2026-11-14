$lnk = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\jpm-music-fans.lnk'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = 'powershell.exe'
$s.Arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\DeepSeekHarness\default-workspace\jp-music-fans\start-local.ps1"'
$s.WorkingDirectory = 'D:\DeepSeekHarness\default-workspace\jp-music-fans'
$s.Save()
Write-Host ("SHORTCUT_OK " + $lnk)
