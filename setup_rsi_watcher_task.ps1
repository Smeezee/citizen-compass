[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $TaskName    = "Citizen Compass RSI Watcher",
    [string] $ProjectPath = "C:\Users\david\citizen-compass"
)

# setup_rsi_watcher_task.ps1 - the local RSI firehose watcher runs hourly on its own.
#
# Architecture's order with the Owner's word, 2026-09-14
# (`..._go-rsi-firehose-watcher-sc-brain.md`). SHIPPED BY BUILD, RUN BY THE OWNER:
# hard rule 6 puts Task Scheduler behind his hand, and Build does not register it.
#
# Modelled on setup_roadmap_task.ps1, including both of its hard-won guards, with
# one difference that matters: -WhatIf EXITS BEFORE ANY CHANGE WHETHER OR NOT THE
# SESSION IS ELEVATED. The roadmap script only guards the non-admin path; an
# already-elevated -WhatIf would fall through to Unregister/Register. Here the
# no-op is unconditional, so it can be proven by running it (rule 12).

$taskName    = $TaskName
$projectPath = $ProjectPath
$exePath     = "$projectPath\rsi-watcher\rsi-watcher.exe"
$workingDir  = "$projectPath\rsi-watcher"

if (-not (Test-Path $exePath)) {
    Write-Host "Could not find rsi-watcher.exe at $exePath." -ForegroundColor Red
    Write-Host "Build it first:  cd rsi-watcher; `$env:GOWORK='off'; go build -o rsi-watcher.exe ." -ForegroundColor Yellow
    exit 1
}

# DUPLICATE GUARD - matched on what a task EXECUTES, not on its name (rule 14):
# two watchers would double the traffic RSI sees from us and interleave writes to
# one state file. Runs before elevation so a dry run can report a refusal too.
$others = @(
    Get-ScheduledTask -ErrorAction SilentlyContinue | ForEach-Object {
        $t = $_
        $cmd = ($t.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' '
        if ($cmd -match 'rsi-watcher' -and $t.TaskName -ne $taskName) {
            [pscustomobject]@{ Name = $t.TaskName; Path = $t.TaskPath; Cmd = $cmd.Trim() }
        }
    }
)
if ($others.Count -gt 0) {
    Write-Host "REFUSING TO REGISTER - something else already runs the RSI watcher:" -ForegroundColor Red
    foreach ($o in $others) {
        Write-Host ("  {0}{1}" -f $o.Path, $o.Name) -ForegroundColor Red
        Write-Host ("      {0}" -f $o.Cmd) -ForegroundColor DarkGray
    }
    exit 1
}

# -WhatIf: SAY WHAT WOULD HAPPEN, CHANGE NOTHING, EXIT - before elevation and
# before any Unregister/Register, so the flag cannot be laundered away (rule 12,
# the setup_checks_task.ps1 incident of 2026-08-01).
if ($WhatIfPreference) {
    Write-Host "WHATIF - nothing will be changed."
    Write-Host "WOULD register: $taskName"
    Write-Host "  Runs    : $exePath -check -from-task"
    Write-Host "  Working : $workingDir"
    Write-Host "  Triggers: Daily (repeating every 1 hour) + AtLogOn"
    Write-Host "  Limits  : one instance at a time, 20-minute execution limit"
    Write-Host "Nothing was changed."
    exit 0
}

$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This needs Administrator rights to register the scheduled task." -ForegroundColor Yellow
    Write-Host "Reopening as Administrator now - click Yes on the Windows prompt." -ForegroundColor Yellow
    $fwd = @('-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"",
             '-TaskName', "`"$taskName`"", '-ProjectPath', "`"$projectPath`"")
    Start-Process powershell -ArgumentList $fwd -Verb RunAs
    exit
}

# -check, so the scheduler owns the interval and a reboot is survived by the
# scheduler rather than by a resident process.
$action = New-ScheduledTaskAction -Execute $exePath -Argument "-check -from-task" -WorkingDirectory $workingDir

# A calendar trigger with repetition (an event trigger's repetition does not fire
# reliably - recorded in setup_watcher_task.ps1), plus AtLogOn for a prompt first
# pass after a reboot.
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At (Get-Date)
$dailyTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 3650)).Repetition
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn

# IgnoreNew: an overrunning pass must not stack another against RSI's servers.
# 20 minutes: -check is a bounded job; a hung read is killed, not held.
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($dailyTrigger, $logonTrigger) `
        -Settings $settings `
        -Description ("Hourly local RSI firehose diff (no AI): new CIG post ids and LIVE/PTU build " +
                      "changes become cards under sc-brain/cig-firehose. Runs -check; the " +
                      "scheduler owns the interval. Registered on the Owner's hand per hard rule 6.") `
        -ErrorAction Stop | Out-Null
    Write-Host "Task registered." -ForegroundColor Green
} catch {
    Write-Host "FAILED to register the task: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

# VERIFY FROM OUTSIDE, the way the duplicate guard looks - a Register that did not
# throw is not proof a task exists (setup_roadmap_task.ps1, 2026-08-30).
$now = @(Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
    ($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match 'rsi-watcher' })
if ($now.Count -eq 0) {
    Write-Host "VERIFICATION FAILED: no scheduled task runs the RSI watcher." -ForegroundColor Red
} else {
    Write-Host "VERIFIED against the scheduler:" -ForegroundColor Green
    foreach ($n in $now) { Write-Host ("  {0}{1}  [{2}]" -f $n.TaskPath, $n.TaskName, $n.State) }
}
Read-Host "Press Enter to close"
