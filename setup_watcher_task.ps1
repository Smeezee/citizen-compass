$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This needs Administrator rights to register the scheduled task." -ForegroundColor Yellow
    Write-Host "Reopening as Administrator now - a Windows permission popup will appear, click Yes." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

$taskName    = "Citizen Compass Inbox Watcher"
$projectPath = "C:\Users\david\citizen-compass"
$exePath     = "$projectPath\inbox_watcher.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "Could not find inbox_watcher.exe at $exePath." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Using Go binary at: $exePath"

# No interpreter/argument needed anymore -- the watcher is now a standalone
# .exe (Go rewrite, replacing the old pythonw.exe inbox_watcher.py setup).
$action = New-ScheduledTaskAction -Execute $exePath -WorkingDirectory $projectPath

# REVISED 2026-07-30: the previous version attached a 1-minute repetition
# pattern directly to an "At log on" trigger (an event-based trigger, no
# fixed clock time of its own). Tested live: killed the watcher, waited
# well past 90 seconds -- it did NOT come back. Event-based triggers
# (AtLogOn/AtStartup) are widely reported as unreliable when combined with
# a Repetition pattern, because the engine's repetition polling is anchored
# to a trigger's StartBoundary, and event triggers don't have one until the
# event actually fires once.
#
# Fix: use a genuine calendar-based "Daily" trigger instead, which DOES have
# a real StartBoundary (today, right now) for the engine to poll against.
# NOTE: an earlier version of this fix tried RepetitionDuration = TimeSpan.Zero
# to mean "repeat forever" -- that is WRONG. Task Scheduler's XML schema
# rejects a zero Duration outright ("value incorrectly formatted or out of
# range: Duration:PT0S"). There's no zero-means-indefinite sentinel here;
# "indefinite" just means a duration long enough not to matter -- back to a
# large-but-finite duration (10 years), same value the original script used,
# just now attached to a Daily trigger instead of AtLogOn.
# Kept "At log on" too, purely so it also comes up immediately after a
# reboot rather than waiting up to a minute for the first repeat tick.
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At (Get-Date)
$dailyTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 1) `
    -RepetitionDuration (New-TimeSpan -Days 3650)).Repetition

$logonTrigger = New-ScheduledTaskTrigger -AtLogOn

$trigger = @($dailyTrigger, $logonTrigger)

$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Watches the citizen-compass inbox folder and auto-sorts anything dropped there. (Go binary, no interpreter needed.) Self-heals via a 1-minute repetition (10-year duration) on a Daily trigger + IgnoreNew, not just RestartCount (AtLogOn+repetition was tested and found unreliable)." -ErrorAction Stop | Out-Null
    Write-Host ""
    Write-Host "Task registered successfully." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "FAILED to register the task: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Starting it now to confirm it works..."
try {
    Start-ScheduledTask -TaskName $taskName -ErrorAction Stop
}
catch {
    Write-Host "FAILED to start the task: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

Start-Sleep -Seconds 3
Write-Host ""
Write-Host "Last few lines of the log (should show 'Watcher started (Go)'):"
Get-Content "$projectPath\logs\inbox_watcher.log" -Tail 5
Write-Host ""
Write-Host "All set. It'll now start automatically at login, and Task Scheduler will" -ForegroundColor Green
Write-Host "re-launch it within a minute if it's ever found not running." -ForegroundColor Green
Read-Host "Press Enter to close"
