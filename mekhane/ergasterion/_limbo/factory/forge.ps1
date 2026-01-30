<# 
.SYNOPSIS
    Forge CLI - 認知ハイパーバイザー・プロンプトシステム

.DESCRIPTION
    Forgeモジュールを検索・表示するためのCLIツール

.EXAMPLE
    .\forge.ps1 list
    .\forge.ps1 load "決断"
    .\forge.ps1 search "TDD"
    .\forge.ps1 tree
    .\forge.ps1 start
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",
    
    [Parameter(Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$Script:BaseDir = $PSScriptRoot
$Script:IndexFile = Join-Path $BaseDir "index.json"

# ディレクトリマッピング
$Script:Directories = @{
    "find"      = Join-Path $BaseDir "modules\find"
    "expand"    = Join-Path $BaseDir "modules\think\expand"
    "focus"     = Join-Path $BaseDir "modules\think\focus"
    "prepare"   = Join-Path $BaseDir "modules\act\prepare"
    "create"    = Join-Path $BaseDir "modules\act\create"
    "reflect"   = Join-Path $BaseDir "modules\reflect"
    "protocols" = Join-Path $BaseDir "protocols"
    "knowledge" = Join-Path $BaseDir "knowledge"
    "helpers"   = Join-Path $BaseDir "helpers"
}

# カテゴリ表示名
$Script:CategoryNames = @{
    "find"      = "🔎 見つける (Find)"
    "expand"    = "🧠📊 考える/広げる (Think/Expand)"
    "focus"     = "🧠🎯 考える/絞る (Think/Focus)"
    "prepare"   = "⚡🔧 働きかける/固める (Act/Prepare)"
    "create"    = "⚡✨ 働きかける/生み出す (Act/Create)"
    "reflect"   = "🔄 振り返る (Reflect)"
    "protocols" = "🛡️ プロトコル (Protocols)"
    "knowledge" = "📚 知識ベース (Knowledge)"
    "helpers"   = "🔧 ヘルパー (Helpers)"
}

# ========================================
# セキュリティ: 入力検証
# ========================================
function Test-SafeInput {
    param([string]$UserInput)
    
    # パストラバーサル攻撃を防止
    if ($UserInput -match '\\.\\.[\\\\/]') {
        Write-Host "⚠️ セキュリティ警告: 無効な入力です" -ForegroundColor Red
        return $false
    }
    
    # 危険な文字を検出
    if ($UserInput -match '[<>|&;`$]') {
        Write-Host "⚠️ セキュリティ警告: 無効な文字が含まれています" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# ========================================
# パフォーマンス: インデックスキャッシュ (index.json利用)
# ========================================
function Get-AllModules {
    param([switch]$ForceRefresh)
    
    if (-not $ForceRefresh -and (Test-Path $Script:IndexFile)) {
        try {
            $json = Get-Content $Script:IndexFile -Raw -Encoding UTF8 | ConvertFrom-Json
            # index.jsonの構造 (modules配列) をハッシュテーブル形式に変換
            $modules = @{}
            foreach ($m in $json.modules) {
                if (-not $modules[$m.category]) { $modules[$m.category] = @() }
                $modules[$m.category] += $m.path
            }
            return $modules
        }
        catch {}
    }
    
    # フォールバック: ディレクトリから生成
    Write-Host "⚠️ index.jsonが見つかりません。再生成します..." -ForegroundColor Yellow
    & "$Script:BaseDir\build-index.ps1" | Out-Null
    return Get-AllModules
}

function Get-ModulesInDirectory {
    param([string]$Path)
    if (Test-Path $Path) {
        return Get-ChildItem -Path $Path -Filter "*.md" | Select-Object -ExpandProperty FullName
    }
    return @()
}

function Update-Index {
    Write-Host "🔄 インデックスを更新中..." -ForegroundColor Cyan
    & "$Script:BaseDir\build-index.ps1"
}

# ========================================
# 基本機能
# ========================================
function Show-List {
    param([string]$Category)
    
    $modules = Get-AllModules
    
    Write-Host "`n🔥 Forge - モジュール一覧`n" -ForegroundColor Cyan
    
    foreach ($cat in $modules.Keys) {
        if ($Category -and $cat -ne $Category) { continue }
        if ($modules[$cat].Count -eq 0) { continue }
        
        Write-Host "$($Script:CategoryNames[$cat]) ($($modules[$cat].Count))" -ForegroundColor Yellow
        
        foreach ($mod in $modules[$cat]) {
            $name = [System.IO.Path]::GetFileNameWithoutExtension($mod)
            Write-Host "  - $name" -ForegroundColor White
        }
        Write-Host ""
    }
}

function Show-Module {
    param([string]$ModuleName)
    
    if (-not (Test-SafeInput $ModuleName)) { return }
    
    $modules = Get-AllModules
    $target = $null
    
    foreach ($cat in $modules.Keys) {
        $found = $modules[$cat] | Where-Object { 
            ([System.IO.Path]::GetFileNameWithoutExtension($_)) -eq $ModuleName 
        } | Select-Object -First 1
        
        if ($found) {
            $target = $found
            break
        }
    }
    
    if ($target) {
        # 完全パスを復元（index.json由来の場合は相対パスの可能性あり）
        $fullPath = $target
        if (-not [System.IO.Path]::IsPathRooted($target)) {
            $fullPath = Join-Path $Script:BaseDir $target
        }
        
        Write-Host "`n📁 モジュール: $ModuleName" -ForegroundColor Cyan
        Write-Host "📍 パス: $fullPath`n" -ForegroundColor DarkGray
        
        $content = Get-Content -Path $fullPath -Raw -Encoding UTF8
        Write-Host $content -ForegroundColor White
    }
    else {
        Write-Host "エラー: モジュール '$ModuleName' が見つかりません" -ForegroundColor Red
        Write-Host "ヒント: 'forge list' で一覧を確認するか、'forge search' で検索してください" -ForegroundColor Gray
    }
}

function Search-Modules {
    param([string]$Keyword)
    
    if (-not (Test-SafeInput $Keyword)) { return }
    
    $modules = Get-AllModules
    $hits = 0
    
    Write-Host "`n🔍 検索結果: '$Keyword'`n" -ForegroundColor Cyan
    
    foreach ($cat in $modules.Keys) {
        foreach ($mod in $modules[$cat]) {
            $name = [System.IO.Path]::GetFileNameWithoutExtension($mod)
            $fullPath = if ([System.IO.Path]::IsPathRooted($mod)) { $mod } else { Join-Path $Script:BaseDir $mod }
            
            # ファイル名検索
            if ($name -match "(?i)$Keyword") {
                Write-Host "  [$($Script:CategoryNames[$cat])] $name" -ForegroundColor Yellow
                $hits++
                continue
            }
            
            # コンテンツ検索 (簡易)
            $content = Get-Content -Path $fullPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
            if ($content -match "(?i)$Keyword") {
                Write-Host "  [$($Script:CategoryNames[$cat])] $name (内容にヒット)" -ForegroundColor Gray
                $hits++
            }
        }
    }
    
    if ($hits -eq 0) {
        Write-Host "  見つかりませんでした。" -ForegroundColor DarkGray
    }
    else {
        Write-Host "`n  計 $hits 件が見つかりました" -ForegroundColor Green
    }
}

function Show-Tree {
    Write-Host "`n🌳 ディレクトリ構造`n" -ForegroundColor Cyan
    tree $BaseDir /F | Select-Object -last 100
}

# ========================================
# ユーザビリティ: インタラクティブモード
# ========================================
function Start-Interactive {
    Clear-Host
    $msg = @"
========================================
🔥 Forge - 認知ハイパーバイザー
========================================

ようこそ、設計者(Architect)。
これはあなたの思考を拡張・整理・出力するための
「プロンプトエンジニアリング支援システム」です。

[できること]
  1. 🔎 見つける  (Find)    - 脳内整理、情報収集
  2. 🧠 考える    (Think)   - 問題分析、意思決定、アイデア出し
  3. ⚡ 働きかける (Act)     - スライド作成、文章執筆、設計
  4. 🔄 振り返る  (Reflect) - 品質チェック、KPT
  5. 🛡️ プロトコル (Rules)   - 開発ルール、DMZ、TDD

[使い方]
  list <category>     モジュール一覧を表示
                      例: .\forge.ps1 list think
  
  load <module>       モジュールを読み込み表示
                      例: .\forge.ps1 load "決断を下す"
  
  search <keyword>    キーワードでモジュールを検索
                      例: .\forge.ps1 search "TDD"
  
  preset [name]       プリセット一覧/コピー (Google AI Studio用)
                      例: .\forge.ps1 preset architect
                      例: .\forge.ps1 preset custom -Modules "DMZ,TDD,Logging"
  
  tree                ディレクトリ構造を表示
  
  index               インデックスを再構築
  
  server              ローカルサーバーを起動
  
  help                このヘルプを表示

例:
  .\forge.ps1 start              # 初心者はこちらから
  .\forge.ps1 list
  .\forge.ps1 list protocols
  .\forge.ps1 load "Module 04"
  .\forge.ps1 search "推論"
  .\forge.ps1 preset architect   # プリセットをクリップボードにコピー

"@
    Write-Host $msg -ForegroundColor White
}

# ========================================
# プリセット機能
# ========================================
function Show-Presets {
    $presetDir = Join-Path $Script:BaseDir "presets"
    
    Write-Host "`n🎯 Forge - プリセット機能`n" -ForegroundColor Cyan
    Write-Host "Google AI Studio用のシステムプロンプトを生成します。`n" -ForegroundColor DarkGray
    
    Write-Host "静的プリセット (推奨):" -ForegroundColor Yellow
    $presets = @{
        "architect"  = "設計・アーキテクチャ向け (Hypervisor + TDD + DMZ)"
        "coder"      = "コーディング支援向け (TDD + Logging + Security)"
        "analyst"    = "分析・調査向け (問題特定 + 状況把握 + 比較)"
        "writer"     = "文章作成向け (ライティング原則 + 品質チェック)"
        "decision"   = "意思決定支援向け (決断 + リスク + 優先順位)"
        "brainstorm" = "アイデア出し向け (ブレスト + 逆転思考 + SCAMPER)"
    }
    
    foreach ($key in $presets.Keys) {
        Write-Host "  $key" -ForegroundColor White -NoNewline
        Write-Host " - $($presets[$key])" -ForegroundColor Gray
    }
    
    Write-Host "`n動的生成:" -ForegroundColor Yellow
    Write-Host "  custom" -ForegroundColor White -NoNewline
    Write-Host " - 任意のモジュールを組み合わせて生成" -ForegroundColor Gray
    
    Write-Host "`n使い方:" -ForegroundColor DarkGray
    Write-Host "  .\forge.ps1 preset architect"
    Write-Host "  .\forge.ps1 preset custom -Modules `"DMZ,TDD,Logging`""
}

function Build-Custom-Preset {
    param([string]$ModuleParams)
    
    $keywords = $ModuleParams -split ","
    $foundModules = @()
    $modules = Get-AllModules
    
    Write-Host "`nカスタムプリセットを構築中..." -ForegroundColor Cyan
    
    foreach ($k in $keywords) {
        $k = $k.Trim()
        if ([string]::IsNullOrWhiteSpace($k)) { continue }
        
        # モジュール検索
        $matchPath = $null
        foreach ($cat in $modules.Keys) {
            $targetPath = $modules[$cat] | Where-Object { 
                $path = $_
                $name = [System.IO.Path]::GetFileNameWithoutExtension($path)
                # エスケープして正規表現マッチ、またはLike演算子
                $name -like "*$k*"
            } | Select-Object -First 1
            if ($targetPath) { $matchPath = $targetPath; break }
        }
        
        if ($matchPath) {
            $fullPath = if ([System.IO.Path]::IsPathRooted($matchPath)) { $matchPath } else { Join-Path $Script:BaseDir $matchPath }
            $foundModules += $fullPath
            Write-Host "  [+] 追加: $([System.IO.Path]::GetFileNameWithoutExtension($fullPath))" -ForegroundColor Green
        }
        else {
            Write-Host "  [!] 未発見: $k" -ForegroundColor Red
        }
    }
    
    if ($foundModules.Count -eq 0) {
        Write-Host "モジュールが見つかりませんでした。" -ForegroundColor Red
        return
    }

    # プリセット構築
    $sb = [System.Text.StringBuilder]::new()
    $sb.AppendLine("# Forge Custom Preset")
    $sb.AppendLine("# Generated at $(Get-Date)")
    $sb.AppendLine("")
    $sb.AppendLine("<system_constitution version=`"custom`">")
    $sb.AppendLine("    <module_registry>")
    
    foreach ($path in $foundModules) {
        $content = Get-Content $path -Raw -Encoding UTF8
        # XMLエスケープなどは簡易的
        $name = [System.IO.Path]::GetFileNameWithoutExtension($path)
        $sb.AppendLine("        <!-- Module: $name -->")
        $sb.AppendLine("        <module name=`"$name`">")
        $sb.AppendLine($content)
        $sb.AppendLine("        </module>")
    }
    
    $sb.AppendLine("    </module_registry>")
    $sb.AppendLine("</system_constitution>")
    
    Set-Clipboard -Value $sb.ToString()
    Write-Host "`n✅ カスタムプリセットをクリップボードにコピーしました！" -ForegroundColor Cyan
}

function Copy-Preset {
    param(
        [string]$PresetName,
        [string]$Modules = ""
    )
    
    if ($PresetName.ToLower() -eq "custom") {
        if (-not $Modules) {
            Write-Host "エラー: -Modules パラメータが必要です (例: custom -Modules `"TDD,DMZ`")" -ForegroundColor Red
            return
        }
        Build-Custom-Preset -ModuleParams $Modules
        return
    }
    
    $presetDir = Join-Path $Script:BaseDir "presets"
    $presetFile = Join-Path $presetDir "$PresetName.txt"
    
    if (-not (Test-Path $presetFile)) {
        Write-Host "エラー: プリセット '$PresetName' が見つかりません" -ForegroundColor Red
        Show-Presets
        return
    }
    
    $content = Get-Content -Path $presetFile -Raw -Encoding UTF8
    Set-Clipboard -Value $content
    Write-Host "`n✅ プリセット '$PresetName' をクリップボードにコピーしました！" -ForegroundColor Green
    Write-Host "`n次のステップ:" -ForegroundColor Yellow
    Write-Host "  1. Google AI Studio を開く" -ForegroundColor Gray
    Write-Host "  2. System Instructions に貼り付け (Ctrl+V)" -ForegroundColor Gray
    Write-Host "  3. チャットを開始" -ForegroundColor Gray
    Write-Host ""
}

# ========================================
# メイン処理
# ========================================
switch ($Command.ToLower()) {
    "start" { Start-Interactive }
    "list" { Show-List -Category ($Arguments -join " ") }
    "load" {
        if (-not $Arguments) {
            Write-Host "エラー: モジュール名を指定してください" -ForegroundColor Red
            return
        }
        Show-Module -ModuleName ($Arguments -join " ")
    }
    "search" {
        if (-not $Arguments) {
            Write-Host "エラー: 検索キーワードを指定してください" -ForegroundColor Red
            return
        }
        Search-Modules -Keyword ($Arguments -join " ")
    }
    "preset" {
        # 引数解析
        $pName = $null
        $modules = $null
        
        for ($i = 0; $i -lt $Arguments.Count; $i++) {
            if ($Arguments[$i] -eq "-Modules") {
                $modules = $Arguments[$i + 1]
                $i++
            }
            elseif (-not $pName) {
                $pName = $Arguments[$i]
            }
        }
        
        if (-not $pName) {
            Show-Presets
        }
        else {
            Copy-Preset -PresetName $pName -Modules $modules
        }
    }
    "tree" { Show-Tree }
    "index" { 
        Update-Index
    }
    "server" {
        & "$Script:BaseDir\start-server.ps1"
    }
    default { Show-Help }
}
