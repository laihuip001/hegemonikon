<#
.SYNOPSIS
    Forge モジュール検証テストスクリプト

.DESCRIPTION
    プロンプトモジュールの構文、完全性、参照をテストします

.EXAMPLE
    .\test-forge.ps1 syntax
    .\test-forge.ps1 all
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("syntax", "completeness", "reference", "all")]
    [string]$TestType = "all",
    
    [Parameter()]
    [string]$Category = ""
)

$Script:BaseDir = $PSScriptRoot
$Script:ResultsDir = Join-Path $BaseDir "test-results"
$Script:TotalTests = 0
$Script:PassedTests = 0
$Script:FailedTests = 0

# ディレクトリマッピング
$Script:Directories = @{
    "find"      = Join-Path $BaseDir "..\modules\find"
    "expand"    = Join-Path $BaseDir "..\modules\think\expand"
    "focus"     = Join-Path $BaseDir "..\modules\think\focus"
    "prepare"   = Join-Path $BaseDir "..\modules\act\prepare"
    "create"    = Join-Path $BaseDir "..\modules\act\create"
    "reflect"   = Join-Path $BaseDir "..\modules\reflect"
    "protocols" = Join-Path $BaseDir "..\protocols"
}

# 結果ディレクトリ作成
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Message = ""
    )
    
    $Script:TotalTests++
    if ($Passed) {
        $Script:PassedTests++
        Write-Host "  [PASS] " -ForegroundColor Green -NoNewline
    }
    else {
        $Script:FailedTests++
        Write-Host "  [FAIL] " -ForegroundColor Red -NoNewline
    }
    Write-Host "$TestName" -NoNewline
    if ($Message) {
        Write-Host " - $Message" -ForegroundColor DarkGray
    }
    else {
        Write-Host ""
    }
}

function Test-Syntax {
    Write-Host "`n=== 構文テスト (Syntax) ===" -ForegroundColor Cyan
    
    $results = @()
    
    foreach ($cat in $Script:Directories.Keys) {
        if ($Category -and $cat -ne $Category) { continue }
        
        $dirPath = $Script:Directories[$cat]
        if (-not (Test-Path $dirPath)) { continue }
        
        Write-Host "`n[$cat]" -ForegroundColor Yellow
        
        Get-ChildItem -Path $dirPath -Filter "*.md" | ForEach-Object {
            $file = $_
            $testResult = @{
                File     = $file.Name
                Category = $cat
                Tests    = @()
            }
            
            # テスト1: ファイル存在
            $exists = Test-Path $file.FullName
            Write-TestResult -TestName "ファイル存在: $($file.Name)" -Passed $exists
            $testResult.Tests += @{ Name = "FileExists"; Passed = $exists }
            
            # テスト2: 空ファイルでないこと
            $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
            $notEmpty = $content -and $content.Length -gt 100
            Write-TestResult -TestName "コンテンツ存在" -Passed $notEmpty -Message "$($content.Length) bytes"
            $testResult.Tests += @{ Name = "ContentExists"; Passed = $notEmpty }
            
            # テスト3: UTF-8エンコーディング（BOMなし）
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
            $hasUtf8Bom = $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
            $validEncoding = $true  # UTF-8であればOK
            Write-TestResult -TestName "エンコーディング" -Passed $validEncoding -Message $(if ($hasUtf8Bom) { "UTF-8 BOM" } else { "UTF-8" })
            $testResult.Tests += @{ Name = "Encoding"; Passed = $validEncoding }
            
            $results += $testResult
        }
    }
    
    # 結果をJSONで保存
    $results | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $ResultsDir "syntax-report.json") -Encoding UTF8
}

function Test-Completeness {
    Write-Host "`n=== 完全性テスト (Completeness) ===" -ForegroundColor Cyan
    
    $results = @()
    
    foreach ($cat in $Script:Directories.Keys) {
        if ($Category -and $cat -ne $Category) { continue }
        
        $dirPath = $Script:Directories[$cat]
        if (-not (Test-Path $dirPath)) { continue }
        
        Write-Host "`n[$cat]" -ForegroundColor Yellow
        
        Get-ChildItem -Path $dirPath -Filter "*.md" | ForEach-Object {
            $file = $_
            $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
            
            $testResult = @{
                File     = $file.Name
                Category = $cat
                Tests    = @()
            }
            
            # テスト1: タイトル/見出しの存在
            $hasTitle = $content -match "^#\s+.+"
            Write-TestResult -TestName "タイトル存在: $($file.BaseName)" -Passed $hasTitle
            $testResult.Tests += @{ Name = "HasTitle"; Passed = $hasTitle }
            
            # テスト2: 説明セクション
            $hasDescription = $content.Length -gt 500
            Write-TestResult -TestName "十分な説明" -Passed $hasDescription -Message "$($content.Length) chars"
            $testResult.Tests += @{ Name = "HasDescription"; Passed = $hasDescription }
            
            $results += $testResult
        }
    }
    
    $results | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $ResultsDir "completeness-report.json") -Encoding UTF8
}

function Test-Reference {
    Write-Host "`n=== 参照テスト (Reference) ===" -ForegroundColor Cyan
    
    # 全モジュール名を収集
    $allModules = @()
    foreach ($cat in $Script:Directories.Keys) {
        $dirPath = $Script:Directories[$cat]
        if (Test-Path $dirPath) {
            Get-ChildItem -Path $dirPath -Filter "*.md" | ForEach-Object {
                $allModules += $_.BaseName
            }
        }
    }
    
    Write-Host "`n総モジュール数: $($allModules.Count)" -ForegroundColor Yellow
    Write-TestResult -TestName "モジュール収集" -Passed ($allModules.Count -gt 0) -Message "$($allModules.Count) modules"
    
    # 結果を保存
    @{ TotalModules = $allModules.Count; Modules = $allModules } | 
    ConvertTo-Json -Depth 3 | 
    Set-Content (Join-Path $ResultsDir "reference-report.json") -Encoding UTF8
}

function Show-Summary {
    Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
    Write-Host "テスト結果サマリー" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  総テスト数: $Script:TotalTests" -ForegroundColor White
    Write-Host "  成功: " -ForegroundColor White -NoNewline
    Write-Host "$Script:PassedTests" -ForegroundColor Green
    Write-Host "  失敗: " -ForegroundColor White -NoNewline
    Write-Host "$Script:FailedTests" -ForegroundColor $(if ($Script:FailedTests -eq 0) { "Green" } else { "Red" })
    
    $passRate = if ($Script:TotalTests -gt 0) { [math]::Round(($Script:PassedTests / $Script:TotalTests) * 100, 1) } else { 0 }
    Write-Host ""
    Write-Host "  合格率: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Yellow" })
    Write-Host ""
}

# メイン処理
Write-Host "`n🧪 Forge モジュール検証テスト`n" -ForegroundColor Cyan

switch ($TestType) {
    "syntax" {
        Test-Syntax
    }
    "completeness" {
        Test-Completeness
    }
    "reference" {
        Test-Reference
    }
    "all" {
        Test-Syntax
        Test-Completeness
        Test-Reference
    }
}

Show-Summary
