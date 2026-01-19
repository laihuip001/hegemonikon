<#
.SYNOPSIS
    Forge Web UI Server
.DESCRIPTION
    Webインターフェース用の簡易HTTPサーバーを起動します。
    Node.jsやPythonに依存せず、.NETのHttpListenerを使用します。
    すべてのファイルへのアクセスを提供し、Web UIからのモジュール閲覧を可能にします。
#>

param(
    [int]$Port = 8000
)

$Root = $PSScriptRoot
$Prefix = "http://localhost:$Port/"
$Listener = New-Object Net.HttpListener
$Listener.Prefixes.Add($Prefix)

try {
    $Listener.Start()
}
catch {
    Write-Host "エラー: ポート $Port をバインドできません。管理者権限が必要か、ポートが使用中です。" -ForegroundColor Red
    exit
}

Write-Host "`n🚀 Forge Web Server Started" -ForegroundColor Green
Write-Host "   URL: $Prefix`web/index.html" -ForegroundColor Cyan
Write-Host "   Root: $Root" -ForegroundColor Gray
Write-Host "   (Ctrl+C で停止)`n" -ForegroundColor Yellow

# MIMEタイプ
$MimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".css"  = "text/css"
    ".js"   = "application/javascript"
    ".json" = "application/json; charset=utf-8"
    ".md"   = "text/markdown; charset=utf-8"
    ".txt"  = "text/plain; charset=utf-8"
    ".png"  = "image/png"
}

# インデックスファイルのコピー（Web UI用）
if (Test-Path "index.json") {
    Copy-Item "index.json" "web\index.json" -Force
}

while ($Listener.IsListening) {
    $Context = $Listener.GetContext()
    $Request = $Context.Request
    $Response = $Context.Response

    $UrlPath = $Request.Url.LocalPath.TrimStart('/')
    if ([string]::IsNullOrEmpty($UrlPath)) { $UrlPath = "web/index.html" }
    
    # パスが web/ で始まらない場合、web/ を補完してリダイレクト（利便性のため）
    # ただし、modules/ や index.json などのリソースへのアクセスは許可
    
    $FilePath = Join-Path $Root $UrlPath.Replace('/', '\')
    $StatusCode = 200
    $ContentType = "text/plain"
    
    Write-Host "[Request] $UrlPath" -ForegroundColor DarkGray

    # パストラバーサル対策: パスを正規化してルートディレクトリ内にあるか確認
    $NormalizedPath = [System.IO.Path]::GetFullPath($FilePath)
    if (-not $NormalizedPath.StartsWith($Root)) {
        $StatusCode = 403
        $ErrorMsg = [System.Text.Encoding]::UTF8.GetBytes("403 Forbidden: Invalid Path")
        $Response.OutputStream.Write($ErrorMsg, 0, $ErrorMsg.Length)
        $Response.StatusCode = $StatusCode
        $Response.Close()
        continue
    }

    if (Test-Path $NormalizedPath -PathType Leaf) {
        $Extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
        if ($MimeTypes.ContainsKey($Extension)) {
            $ContentType = $MimeTypes[$Extension]
        }
        
        try {
            $Bytes = [System.IO.File]::ReadAllBytes($FilePath)
            $Response.ContentType = $ContentType
            $Response.ContentLength64 = $Bytes.Length
            $Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
        }
        catch {
            $StatusCode = 500
        }
    }
    else {
        $StatusCode = 404
        $ErrorMsg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
        $Response.OutputStream.Write($ErrorMsg, 0, $ErrorMsg.Length)
    }

    $Response.StatusCode = $StatusCode
    $Response.Close()
}
