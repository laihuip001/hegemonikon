# migrate_antigravity_to_m.ps1
# Antigravity データ移行スクリプト (C: -> M:)
# 実行条件: Antigravity (VS Code/Cursor) を完全に終了していること

$Source = "$env:USERPROFILE\.gemini\antigravity"
$Dest = "M:\Brain\.gemini_data\antigravity"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Antigravity Data Migration (C: -> M:)   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Antigravity 終了確認
Write-Host "`n[Step 1] Antigravity (Editor) が終了しているか確認してください。" -ForegroundColor Yellow
Pause

# 2. 移動先ディレクトリ作成
if (-not (Test-Path $Dest)) {
    Write-Host "`n[Step 2] Creating Destination: $Dest"
    New-Item -ItemType Directory -Force -Path $Dest | Out-Null
}

# 3. データ移動 (Robocopy)
Write-Host "`n[Step 3] Moving Data..."
if (Test-Path $Source) {
    # Robocopy は堅牢なコピーが可能 (Moveだとロックで失敗しやすい)
    robocopy $Source $Dest /E /MOVE /NFL /NDL /R:3 /W:5
    
    # Robocopyの終了コード判定 (1は成功、それ以上は警告/エラー)
    if ($LASTEXITCODE -ge 8) {
        Write-Host "Error: Copy failed. Please close all editors and try again." -ForegroundColor Red
        exit
    }
} else {
    Write-Host "Source directory not found (Already moved?). Skipping." -ForegroundColor Gray
}

# 4. 残骸削除 (Robocopy /MOVE で消えなかった場合)
if (Test-Path $Source) {
    Write-Host "`n[Step 4] Cleaning up source..."
    Remove-Item -Path $Source -Recurse -Force -ErrorAction SilentlyContinue
}

# 5. ジャンクション作成
Write-Host "`n[Step 5] Creating Junction Link..."
if (-not (Test-Path $Source)) {
    cmd /c mklink /J "$Source" "$Dest"
    
    if (Test-Path $Source) {
        Write-Host "`nSUCCESS! Junction created." -ForegroundColor Green
        Write-Host "C: (Link) -> $Source"
        Write-Host "M: (Real) -> $Dest"
    } else {
        Write-Host "`nFAILED to create junction." -ForegroundColor Red
    }
} else {
    Write-Host "`nError: Source directory still exists. Cannot create link." -ForegroundColor Red
}

Write-Host "`nDone. You can restart Antigravity now." -ForegroundColor Cyan
Pause
