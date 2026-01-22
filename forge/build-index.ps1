<#
.SYNOPSIS
    Forge インデックス生成スクリプト

.DESCRIPTION
    全モジュールをスキャンし、index.jsonを生成します。
    このファイルは全ツール（CLI, Web UI, プリセット生成）の
    単一データソース（Single Source of Truth）として機能します。

.EXAMPLE
    .\build-index.ps1
#>

$Script:BaseDir = $PSScriptRoot
$Script:OutputFile = Join-Path $BaseDir "index.json"

# ディレクトリマッピング
$Script:Directories = @{
    "find"      = @{
        path  = "modules\find"
        label = "見つける (Find)"
        emoji = "🔎"
        phase = "find"
    }
    "expand"    = @{
        path  = "modules\think\expand"
        label = "考える/広げる (Think/Expand)"
        emoji = "📊"
        phase = "think"
    }
    "focus"     = @{
        path  = "modules\think\focus"
        label = "考える/絞る (Think/Focus)"
        emoji = "🎯"
        phase = "think"
    }
    "prepare"   = @{
        path  = "modules\act\prepare"
        label = "働きかける/固める (Act/Prepare)"
        emoji = "🔧"
        phase = "act"
    }
    "create"    = @{
        path  = "modules\act\create"
        label = "働きかける/生み出す (Act/Create)"
        emoji = "✨"
        phase = "act"
    }
    "reflect"   = @{
        path  = "modules\reflect"
        label = "振り返る (Reflect)"
        emoji = "🔄"
        phase = "reflect"
    }
    "protocols" = @{
        path  = "protocols"
        label = "プロトコル (Protocols)"
        emoji = "🛡️"
        phase = "system"
    }
    "knowledge" = @{
        path  = "knowledge"
        label = "知識ベース (Knowledge)"
        emoji = "📚"
        phase = "reference"
    }
    "helpers"   = @{
        path  = "helpers"
        label = "ヘルパー (Helpers)"
        emoji = "🔧"
        phase = "reference"
    }
}

function Get-ModuleDescription {
    param([string]$Content)
    
    # 最初の説明文を抽出（見出し以降の最初の段落）
    if ($Content -match '(?m)^#[^#].*\r?\n\r?\n(.+?)(?:\r?\n\r?\n|$)') {
        $desc = $Matches[1] -replace '\r?\n', ' '
        if ($desc.Length -gt 100) {
            return $desc.Substring(0, 100) + "..."
        }
        return $desc
    }
    return ""
}

function Get-ModuleMetadata {
    param([string]$Content)
    
    $meta = @{
        hasInstruction  = $Content -match '<instruction>'
        hasOutputFormat = $Content -match '<output' -or $Content -match '##.*出力|##.*Output'
        hasExample      = $Content -match '##.*例|##.*Example|```'
        wordCount       = ($Content -split '\s+').Count
    }
    
    return $meta
}

Write-Host "`n🔧 Forge インデックス生成`n" -ForegroundColor Cyan

$index = @{
    version    = "2.0"
    generated  = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    stats      = @{
        totalModules = 0
        categories   = 0
        phases       = @{}
    }
    categories = @{}
    modules    = @()
}

foreach ($catKey in $Script:Directories.Keys) {
    $catInfo = $Script:Directories[$catKey]
    $dirPath = Join-Path $BaseDir $catInfo.path
    
    if (-not (Test-Path $dirPath)) { continue }
    
    Write-Host "[$catKey] " -ForegroundColor Yellow -NoNewline
    
    $categoryModules = @()
    
    Get-ChildItem -Path $dirPath -Filter "*.md" | ForEach-Object {
        $file = $_
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        
        $module = @{
            id          = [System.IO.Path]::GetFileNameWithoutExtension($file.Name) -replace '[^\w\-]', '_'
            name        = $file.BaseName
            category    = $catKey
            phase       = $catInfo.phase
            path        = $catInfo.path + "/" + $file.Name
            description = Get-ModuleDescription $content
            metadata    = Get-ModuleMetadata $content
            size        = $file.Length
        }
        
        $categoryModules += $module
        $index.modules += $module
        $index.stats.totalModules++
    }
    
    $index.categories[$catKey] = @{
        label = $catInfo.label
        emoji = $catInfo.emoji
        phase = $catInfo.phase
        count = $categoryModules.Count
    }
    
    # Phase統計
    if (-not $index.stats.phases[$catInfo.phase]) {
        $index.stats.phases[$catInfo.phase] = 0
    }
    $index.stats.phases[$catInfo.phase] += $categoryModules.Count
    
    Write-Host "$($categoryModules.Count) modules" -ForegroundColor Gray
}

$index.stats.categories = $index.categories.Count

# JSON出力
$json = $index | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($OutputFile, $json, [System.Text.Encoding]::UTF8)

Write-Host "`n✅ index.json を生成しました" -ForegroundColor Green
Write-Host "   総モジュール: $($index.stats.totalModules)" -ForegroundColor Gray
Write-Host "   カテゴリ: $($index.stats.categories)" -ForegroundColor Gray
Write-Host "   出力: $OutputFile" -ForegroundColor Gray
Write-Host ""
