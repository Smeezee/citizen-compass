<#
==============================================================================
 setup_checks_task.ps1
==============================================================================
 Registers ONE scheduled task that runs the auditor layer (Path C, Part D).

 Follows the pattern proven by setup_watcher_task.ps1, including the lesson
 that script paid for: an event-based trigger (AtLogOn) combined with a
 Repetition pattern is unreliable, because the engine anchors repetition to a
 trigger's StartBoundary and event triggers have none until they first fire.
 A calendar Daily trigger has a real StartBoundary, so that is what is used.

 ONE TASK. NOT FOUR.
 -------------------
 The order asks for file daily, db daily, sources and network weekly. That is
 four schedules, and registering four tasks would be the wrong way to get
 them: this project has twice lost work to two writers on one target. So a
 single task runs run_checks_scheduled.ps1, and THAT script decides which
 groups run today. One process, one schedule, and `duplicate_process` and
 `checker_health` both watch for it having been violated.

 -MultipleInstances IgnoreNew means a long weekly run can never overlap the
 next day's daily run.

 WHAT THIS DOES NOT DO
 ---------------------
 It does not touch the inbox watcher's task, and it does not run the checks
 itself beyond one confirming start.

 USAGE
   powershell -ExecutionPolicy Bypass -File .\setup_checks_task.ps1
   powershell -ExecutionPolicy Bypass -File .\setup_checks_task.ps1 -WhatIf
==============================================================================
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $ProjectPath = 'C:\Users\david\citizen-compass',
    [string] $TaskName    = 'Citizen Compass Auditor Checks',
    # Daily run time. Kept away from midnight so a machine that sleeps
    # overnight still catches it, and after the watcher's own activity.
    [string] $At          = '09:15'
)

$wrapper = Join-Path $ProjectPath 'run_checks_scheduled.ps1'
if (-not (Test-Path $wrapper)) {
    Write-Host "Could not find $wrapper - nothing registered." -ForegroundColor Red
    exit 1
}

$isAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent() `
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# ---------------------------------------------------------------------------
# ELEVATION MUST NOT LAUNDER AWAY -WhatIf.
#
# This bit is here because it already went wrong. The original version copied
# setup_watcher_task.ps1's elevation block, which relaunches with only
# "-ExecutionPolicy Bypass -File <path>" and forwards NO parameters. Running
# this script with -WhatIf therefore elevated into a copy that had never heard
# of -WhatIf, took the real branch, and registered the task for real.
#
# A dry run that cannot stay dry is the same class of defect as a gate that
# cannot fail: it reports safety it does not provide. So -WhatIf now refuses to
# elevate at all, and the elevation path forwards every argument it was given.
# ---------------------------------------------------------------------------
if (-not $isAdmin) {
    if ($WhatIfPreference) {
        Write-Host "-WhatIf requested, and registering a task needs Administrator." -ForegroundColor Yellow
        Write-Host "NOT elevating: an elevated relaunch would drop -WhatIf and register for real." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Would register:" -ForegroundColor Cyan
        Write-Host "  Task    : $TaskName"
        Write-Host "  Runs    : powershell.exe -File `"$wrapper`""
        Write-Host "  Trigger : Daily at $At"
        Write-Host "Nothing was changed. Re-run from an elevated prompt without -WhatIf to apply."
        exit 0
    }

    Write-Host "This needs Administrator rights to register the scheduled task." -ForegroundColor Yellow
    Write-Host "Reopening as Administrator - a Windows permission popup will appear, click Yes." -ForegroundColor Yellow
    $fwd = @(
        '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"",
        '-ProjectPath', "`"$ProjectPath`"", '-TaskName', "`"$TaskName`"", '-At', "`"$At`""
    )
    Start-Process powershell -ArgumentList $fwd -Verb RunAs
    exit
}

# Guard against the exact failure this project keeps having: a second task
# writing the same thing. Report it rather than silently adding another.
$existing = Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -like '*Auditor*' -or $_.TaskName -like '*Citizen Compass Checks*' } |
    Where-Object { $_.TaskName -ne $TaskName }
if ($existing) {
    Write-Host "REFUSING TO REGISTER - other auditor-looking tasks already exist:" -ForegroundColor Red
    $existing | ForEach-Object { Write-Host "   $($_.TaskName) [$($_.State)]" -ForegroundColor Red }
    Write-Host "Two schedules writing one findings table is the failure this design avoids." -ForegroundColor Red
    Write-Host "Remove or rename them first, then re-run." -ForegroundColor Red
    exit 1
}

$action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument "-NonInteractive -NoProfile -ExecutionPolicy Bypass -File `"$wrapper`"" `
    -WorkingDirectory $ProjectPath

# Calendar-based Daily trigger - a real StartBoundary, unlike AtLogOn.
$trigger = New-ScheduledTaskTrigger -Daily -At $At

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

$desc = "Runs the Citizen Compass auditor layer. One task, one schedule: " +
        "run_checks_scheduled.ps1 runs the file and db groups daily and the " +
        "sources and network groups on Sundays. Findings go to " +
        "pipeline_check_results and pipeline_findings; every run writes a row " +
        "to pipeline_check_runs even when it finds nothing, so a stopped " +
        "scheduler cannot look like a clean bill of health. StartWhenAvailable " +
        "so a missed run catches up rather than being skipped silently."

if ($PSCmdlet.ShouldProcess($TaskName, "Register scheduled task")) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    try {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
            -Settings $settings -Description $desc -ErrorAction Stop | Out-Null
        Write-Host "Task '$TaskName' registered for $At daily." -ForegroundColor Green
    }
    catch {
        Write-Host "FAILED to register: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }

    Write-Host "Starting it once to confirm it actually runs..."
    Start-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 20
    Write-Host ""
    Write-Host "Tail of logs\checks_scheduled.log:"
    Get-Content (Join-Path $ProjectPath 'logs\checks_scheduled.log') -Tail 12
}
