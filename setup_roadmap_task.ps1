[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $TaskName    = "Citizen Compass Roadmap Watcher",
    [string] $ProjectPath = "C:\Users\david\citizen-compass"
)

# setup_roadmap_task.ps1 - the roadmap watcher runs on its own, or it does not run.
#
# Q5b, approved by Sleven 2026-08-30. Hard rule 6 puts Task Scheduler behind an
# explicit ask, every time; that ask was made and answered.
#
# WHY: `last_good_scheduled_run` has been "" since the day the watcher was
# built. Its last run was manual, thirteen days ago. A tripwire nobody trips is
# not a tripwire - and this one had the answer to Q5c sitting in its payload for
# months while nobody double-clicked it.
#
# Modelled on setup_watcher_task.ps1, deliberately, including both of its
# hard-won guards. Where this one differs from that one is noted at each site.

$taskName    = $TaskName
$projectPath = $ProjectPath
$exePath     = "$projectPath\roadmap-watcher\roadmap-watcher.exe"
$workingDir  = "$projectPath\roadmap-watcher"

if (-not (Test-Path $exePath)) {
    Write-Host "Could not find roadmap-watcher.exe at $exePath." -ForegroundColor Red
    Write-Host "Build it first:  cd roadmap-watcher; go build -o roadmap-watcher.exe ." -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------------------------
# DUPLICATE GUARD - matched STRUCTURALLY, on what a task EXECUTES.
#
# Same rule as the inbox watcher's, for the same reason (rule 14): two watchers
# polling one board double the traffic RSI sees from us and interleave writes to
# one state file and one history log. The failure would look like a history that
# skips observations for no apparent reason.
#
# It does NOT match on task names. A name pattern is a naming convention and it
# fails exactly when it matters - the moment somebody passes
# -TaskName "Nightly RSI Poll". Matching the action's command line answers the
# real question, "is something already polling this board", and cannot be evaded
# by choosing a different name.
#
# Runs BEFORE the elevation check on purpose: detecting a duplicate needs no
# privileges, a dry run must be able to report the refusal, and there is no
# reason to raise a UAC prompt for a run that is going to refuse anyway.
# ---------------------------------------------------------------------------
$others = @(
    Get-ScheduledTask -ErrorAction SilentlyContinue | ForEach-Object {
        $t = $_
        $cmd = ($t.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -join ' '
        if ($cmd -match 'roadmap-watcher' -and $t.TaskName -ne $taskName) {
            [pscustomobject]@{ Name = $t.TaskName; Path = $t.TaskPath; Cmd = $cmd.Trim() }
        }
    }
)
if ($others.Count -gt 0) {
    Write-Host "REFUSING TO REGISTER - something else already polls the roadmap:" -ForegroundColor Red
    foreach ($o in $others) {
        Write-Host ("  {0}{1}" -f $o.Path, $o.Name) -ForegroundColor Red
        Write-Host ("      {0}" -f $o.Cmd) -ForegroundColor DarkGray
    }
    Write-Host ""
    Write-Host "Remove or rename that task first. Two pollers on one board double" -ForegroundColor Yellow
    Write-Host "the traffic RSI sees from us and interleave writes to one state file." -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------------------------
# ELEVATION MUST NOT LAUNDER AWAY -WhatIf.
#
# setup_checks_task.ps1 elevated with Start-Process -Verb RunAs and forwarded
# ONLY -File. The elevated copy had never heard of -WhatIf, took the real
# branch, and on 2026-08-01 a -WhatIf run registered a scheduled task for real.
# That is hard rule 12's own example of a safety flag that silently does not
# apply: the flag reported a safety it did not provide.
#
# So -WhatIf REFUSES to elevate rather than elevating without it, and a real
# elevation forwards its arguments.
# ---------------------------------------------------------------------------
$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    if ($WhatIfPreference) {
        Write-Host "-WhatIf requested, and registering a task needs Administrator." -ForegroundColor Yellow
        Write-Host "NOT elevating: an elevated relaunch would drop -WhatIf and register for real." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "WOULD register: $taskName"
        Write-Host "  Runs    : $exePath -check"
        Write-Host "  Working : $workingDir"
        Write-Host "  Triggers: Daily (repeating every 4 hours) + AtLogOn"
        Write-Host "  Window  : hidden - no console on the desktop"
        Write-Host ""
        Write-Host "Nothing was changed."
        exit 0
    }

    Write-Host "This needs Administrator rights to register the scheduled task." -ForegroundColor Yellow
    Write-Host "Reopening as Administrator now - click Yes on the Windows prompt." -ForegroundColor Yellow
    $fwd = @(
        '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"",
        '-TaskName', "`"$taskName`"", '-ProjectPath', "`"$projectPath`""
    )
    Start-Process powershell -ArgumentList $fwd -Verb RunAs
    exit
}

Write-Host "Using roadmap watcher at: $exePath"

# -check RATHER THAN THE RESIDENT LOOP.
#
# The watcher can run forever on its own 4-hour timer, but a resident process
# has to survive a reboot by its own effort and there is nothing to watch
# between polls - it sleeps. Letting the scheduler own the interval means the
# thing that survives reboots is the scheduler, which is what it is for, and a
# crashed poll costs one cycle rather than every cycle until somebody notices.
$action = New-ScheduledTaskAction -Execute $exePath -Argument "-check" -WorkingDirectory $workingDir

# A CALENDAR TRIGGER, NOT AtLogOn+Repetition.
#
# setup_watcher_task.ps1 records this the hard way: a repetition pattern
# attached to an event-based trigger does not fire reliably, because the
# engine's polling is anchored to a StartBoundary that an event trigger does
# not have until the event fires once. Tested there, found dead. A Daily
# trigger has a real StartBoundary. Four hours matches interval_hours in
# roadmap-watcher-settings.json; the watcher's own timer is then a no-op.
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At (Get-Date)
$dailyTrigger.Repetition = (New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 4) `
    -RepetitionDuration (New-TimeSpan -Days 3650)).Repetition

# AtLogOn as well, so a reboot gets a poll immediately rather than waiting up
# to four hours for the next repeat tick.
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn

$trigger = @($dailyTrigger, $logonTrigger)

# MultipleInstances IgnoreNew: a poll that overruns must not stack a second one
# on top of it against RSI's servers.
# ExecutionTimeLimit 1 hour, NOT zero: -check is a bounded job, and a hung HTTP
# read should be killed rather than held forever. The inbox watcher is resident
# and correctly uses zero; this one is not, and copying that value would have
# been the wrong kind of consistency.
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
        -Settings $settings `
        -Description ("Polls RSI's roadmap board every 4 hours and reports the gap " +
                      "between the live patch version and the site's own " +
                      "last_verified_patch. Runs -check, so the scheduler owns the " +
                      "interval and a reboot is survived by the scheduler rather " +
                      "than by the process. Registered 2026-08-30, Q5b, on Sleven's " +
                      "explicit approval per hard rule 6.") `
        -ErrorAction Stop | Out-Null
    Write-Host ""
    Write-Host "Task registered successfully." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "FAILED to register the task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Starting it now to confirm it actually runs..."
try {
    Start-ScheduledTask -TaskName $taskName -ErrorAction Stop
    Start-Sleep -Seconds 20
    $info = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host ("  last run   : {0}" -f $info.LastRunTime)
    Write-Host ("  last result: {0}" -f $info.LastTaskResult)
    if ($info.LastTaskResult -eq 0) {
        Write-Host "The task ran and exited 0." -ForegroundColor Green
    } else {
        Write-Host "The task ran and did NOT exit 0 - check roadmap-watcher's log." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Could not start it: $($_.Exception.Message)" -ForegroundColor Yellow
}
