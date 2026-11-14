$ErrorActionPreference = 'SilentlyContinue'
$rows = @()
foreach ($t in (Get-ScheduledTask | Where-Object { $_.State -ne 'Disabled' })) {
  $reps = @()
  foreach ($tr in $t.Triggers) {
    if ($tr.Repetition -and $tr.Repetition.Interval) { $reps += $tr.Repetition.Interval }
  }
  if ($reps.Count -gt 0) {
    $acts = @()
    foreach ($a in $t.Actions) { $acts += (($a.Execute) + ' ' + ($a.Arguments)) }
    $rows += [pscustomobject]@{
      Name = ($t.TaskPath + $t.TaskName)
      Every = ($reps -join ',')
      Action = ($acts -join ' ; ')
      Hidden = $t.Settings.Hidden
      Logon = $t.Principal.LogonType
    }
  }
}
$rows | Format-List
