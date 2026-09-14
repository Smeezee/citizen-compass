# Ops mail wake — optional Scheduled Task (Owner-only register)
# Hard rule 6: Owner runs the real Register. Ops may -WhatIf only.

param(
  [switch]$WhatIf
)

$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $PSScriptRoot 'ops-mail-wake.exe'))) {
  Write-Error "Build first: go build -o ops-mail-wake.exe ."
  exit 1
}
$Exe = Join-Path $PSScriptRoot 'ops-mail-wake.exe'
$Settings = Join-Path $PSScriptRoot 'ops-mail-wake-settings.json'
$Action = New-ScheduledTaskAction -Execute $Exe -Argument "-settings `"$Settings`"" -WorkingDirectory $PSScriptRoot
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$SettingsT = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$Name = 'CitizenCompass-OpsMailWake'

if ($WhatIf) {
  Write-Host "WhatIf: would register task $Name"
  Write-Host "  Execute: $Exe"
  Write-Host "  Settings: $Settings"
  Write-Host "  Trigger: AtLogOn"
  exit 0
}

Register-ScheduledTask -TaskName $Name -Action $Action -Trigger $Trigger -Principal $Principal -Settings $SettingsT -Force
Write-Host "Registered $Name"
