# Hegemonikón Config Sync Script
# Syncs M:\.gemini (source of truth) -> C:\Users\$env:USERNAME\.gemini
# Run on every /boot

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$Source = "M:\.gemini"
$Dest = "C:\Users\$env:USERNAME\.gemini"

# Files and directories to sync
$SyncTargets = @(
    "GEMINI.md",
    ".agent"
)

# Additional targets for Antigravity compatibility
# Antigravity reads ~/.gemini/workflows/ directly, not .agent/workflows/
$LegacySyncTargets = @(
    @{
        Source = "M:\Hegemonikon\.agent\workflows"
        Dest   = "C:\Users\$env:USERNAME\.gemini\workflows"
    }
)

Write-Host "[Hegemonikon] Config Sync: M: -> C:" -ForegroundColor Cyan

foreach ($target in $SyncTargets) {
    $srcPath = Join-Path $Source $target
    $dstPath = Join-Path $Dest $target
    
    if (-not (Test-Path $srcPath)) {
        Write-Host "  SKIP: $target (not found in source)" -ForegroundColor Yellow
        continue
    }
    
    if ($DryRun) {
        Write-Host "  DRY-RUN: Would sync $target" -ForegroundColor Gray
        continue
    }
    
    # Use robocopy for directories, Copy-Item for files
    if (Test-Path $srcPath -PathType Container) {
        $null = robocopy $srcPath $dstPath /MIR /NFL /NDL /NJH /NJS /NC /NS 2>&1
        Write-Host "  SYNCED: $target/ (directory)" -ForegroundColor Green
    }
    else {
        Copy-Item $srcPath $dstPath -Force
        Write-Host "  SYNCED: $target" -ForegroundColor Green
    }
}

# Sync legacy targets (Antigravity compatibility)
foreach ($legacy in $LegacySyncTargets) {
    $srcPath = $legacy.Source
    $dstPath = $legacy.Dest
    
    if (-not (Test-Path $srcPath)) {
        Write-Host "  SKIP: $srcPath (not found)" -ForegroundColor Yellow
        continue
    }
    
    if ($DryRun) {
        Write-Host "  DRY-RUN: Would sync $srcPath -> $dstPath" -ForegroundColor Gray
        continue
    }
    
    # Always use robocopy for directories
    $null = robocopy $srcPath $dstPath /MIR /NFL /NDL /NJH /NJS /NC /NS 2>&1
    Write-Host "  SYNCED: workflows/ (Antigravity compat)" -ForegroundColor Green
}

Write-Host "[Hegemonikon] Config Sync: Complete" -ForegroundColor Cyan
