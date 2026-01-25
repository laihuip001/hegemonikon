param([switch]$Unregister)
$TaskName = "Hegemonikon-Gnosis-DailyCollect"
$ScriptPath = "M:\Hegemonikon\.agent\scripts\gnosis-auto-collect.ps1"
if ($Unregister) { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false; exit 0 }
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File $ScriptPath"
$Trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings
Write-Host "Task registered: $TaskName"
