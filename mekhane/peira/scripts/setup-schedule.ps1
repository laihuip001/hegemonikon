$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RunScript = Join-Path $ScriptDir "run-sync.ps1"
$TaskName = "Antigravity Chat History Sync"

Write-Host "Registering Scheduled Task: $TaskName" -ForegroundColor Cyan

# Check if task exists
try {
    Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop | Out-Null
    Write-Warning "Task already exists. Unregistering..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
} catch {
    # Task doesn't exist, proceed
}

# Trigger: Every 10 minutes, indefinitely
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10)

# Action: Run run-sync.ps1 with Bypass policy
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$RunScript`""

# Settings: Run only when user is logged on, strictly
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Syncs Antigravity Brain chat history to LanceDB."
    Write-Host "✅ Task Registered Successfully!" -ForegroundColor Green
    Write-Host "Logs will be written to: $(Join-Path $ScriptDir 'logs\sync.log')"
} catch {
    Write-Error "Failed to register task. Ensure you are running as Administrator if needed (usually not for user-level tasks)."
    Write-Error $_
}
