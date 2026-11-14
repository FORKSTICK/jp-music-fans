$ErrorActionPreference = 'Stop'
$vbs = 'D:\DeepSeekHarness\default-workspace\jp-music-fans\tools\watchdog-hidden.vbs'
$act = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('//B //Nologo "' + $vbs + '"')
Set-ScheduledTask -TaskName 'jpm-watchdog' -TaskPath '\' -Action $act | Out-Null
$t = Get-ScheduledTask -TaskName 'jpm-watchdog'
"watchdog action -> " + (($t.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' | ')
try {
  Unregister-ScheduledTask -TaskName 'surfcore-lmem-sync' -TaskPath '\' -Confirm:$false
  "surfcore-lmem-sync removed"
} catch { "surfcore remove failed: " + $_.Exception.Message }
