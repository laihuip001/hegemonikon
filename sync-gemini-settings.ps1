# sync-gemini-settings.ps1
# C:\.gemini <-> M:\.gemini 双方向同期スクリプト
# 用途: 設定変更後に実行し、両ドライブを同期する

param(
    [ValidateSet("CtoM", "MtoC", "Both")]
    [string]$Direction = "Both"
)

$CPath = "$env:USERPROFILE\.gemini"
$MPath = "M:\.gemini"

Write-Host "=== Gemini Settings Sync ===" -ForegroundColor Cyan

switch ($Direction) {
    "CtoM" {
        Write-Host "Syncing C: -> M: ..."
        robocopy $CPath $MPath /E /XO /NFL /NDL /R:3 /W:5
    }
    "MtoC" {
        Write-Host "Syncing M: -> C: ..."
        robocopy $MPath $CPath /E /XO /NFL /NDL /R:3 /W:5
    }
    "Both" {
        Write-Host "Syncing C: -> M: ..."
        robocopy $CPath $MPath /E /XO /NFL /NDL /R:3 /W:5
        Write-Host "Syncing M: -> C: ..."
        robocopy $MPath $CPath /E /XO /NFL /NDL /R:3 /W:5
    }
}

Write-Host "`nSync Complete!" -ForegroundColor Green
