$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$LogsDir = Join-Path $ScriptDir "logs"
$LogFile = Join-Path $LogsDir "sync.log"
$LockFile = Join-Path $LogsDir "sync.lock"

# Ensure Logs Directory Exists
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

function Log-Message {
    param([string]$Msg)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp $Msg" | Out-File -FilePath $LogFile -Append -Encoding utf8
}

# Start fresh log
"" | Out-File -FilePath $LogFile -Encoding utf8 -Force

# Lock Check
if (Test-Path $LockFile) {
    $LockDate = Get-Item $LockFile | Select-Object -ExpandProperty LastWriteTime
    if ((Get-Date) - $LockDate -lt (New-TimeSpan -Minutes 30)) {
        Log-Message "SKIP: Lock file exists (since $LockDate)."
        exit
    }
    else {
        Remove-Item $LockFile -Force
        Log-Message "WARN: Removed stale lock file."
    }
}

New-Item -ItemType File -Path $LockFile -Force | Out-Null

try {
    Log-Message "START: Sync Process"

    # Resolve Paths
    $RootForVenv = (Resolve-Path (Join-Path $ScriptDir "..")).Path
    $VenvPathKB = Join-Path $RootForVenv ".venv-kb"
    $VenvPathDef = Join-Path $RootForVenv ".venv"
    
    $PythonCandidates = @()
    if (Test-Path $VenvPathKB) { $PythonCandidates += Join-Path $VenvPathKB "Scripts\python.exe" }
    if (Test-Path $VenvPathDef) { $PythonCandidates += Join-Path $VenvPathDef "Scripts\python.exe" }
    $PythonCandidates += "python" # Fallback to PATH

    $SelectedPython = $null

    foreach ($Py in $PythonCandidates) {
        try {
            # Verification Check
            $CheckCmd = if ($Py -eq "python") { "python" } else { "& '$Py'" }
            $Res = Invoke-Expression "$CheckCmd --version 2>&1"
            if ($LASTEXITCODE -eq 0) {
                # Ensure it's not the Windows Store shim that fails silently or interactively
                # Store shim often returns 0 but prints nothing or opens dialog if not installed?
                # Python 3.x prints "Python 3.x.x".
                if ($Res -match "Python") {
                    $SelectedPython = $Py
                    Log-Message "INFO: Verified interpreter: $Py ($Res)"
                    break
                }
            }
        }
        catch {
            Log-Message "DEBUG: Candidate $Py failed check."
        }
    }

    if (-not $SelectedPython) {
        Throw "No valid Python interpreter found. Checked: $($PythonCandidates -join ', ')"
    }

    $ScriptPath = Join-Path $ScriptDir "chat-history-kb.py"
    $ArgumentList = "`"$ScriptPath`" sync --report"
    
    # Run Command
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    if ($SelectedPython -eq "python") {
        # Need to capture path for python in PATH
        $ProcessInfo.FileName = "python" 
    }
    else {
        $ProcessInfo.FileName = $SelectedPython
    }
    
    $ProcessInfo.Arguments = $ArgumentList
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    $ProcessInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $ProcessInfo
    $Process.Start() | Out-Null
    
    $StdOut = $Process.StandardOutput.ReadToEnd()
    $StdErr = $Process.StandardError.ReadToEnd()
    
    $Process.WaitForExit()

    # Log Results
    if ($StdOut) {
        $StdOut | Out-File -FilePath $LogFile -Append -Encoding utf8
    }
    if ($StdErr) {
        Log-Message "STDERR:"
        $StdErr | Out-File -FilePath $LogFile -Append -Encoding utf8
    }

    Log-Message "END: Exit Code $($Process.ExitCode)"

}
catch {
    Log-Message "ERROR: $_"
    Log-Message "Stack Trace: $($_.ScriptStackTrace)"
}
finally {
    if (Test-Path $LockFile) {
        Remove-Item $LockFile -Force
    }
}
