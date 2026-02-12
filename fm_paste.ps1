<#
.SYNOPSIS
    FileMaker スクリプトエディタへの XML ペーストツール

.DESCRIPTION
    Forge が生成した fmxmlsnippet XML ファイルを読み込み、
    Windows クリップボードに FM カスタム形式 (Mac-XMSS) として設定する。
    その後 FM スクリプトエディタで Ctrl+V すれば、スクリプトステップが貼り付けられる。

.PARAMETER XmlFile
    FM XML ファイルのパス

.EXAMPLE
    .\fm_paste.ps1 -XmlFile "腎生検_block4.xml"
    # → クリップボードに設定完了。FM で Ctrl+V。

.NOTES
    - Windows 11 / FileMaker Pro 2024 で動作確認
    - PowerShell 5.1+ (Windows 標準) で動作
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$XmlFile
)

# Validate file exists
if (-not (Test-Path $XmlFile)) {
    Write-Error "❌ ファイルが見つかりません: $XmlFile"
    exit 1
}

# Read XML content
$xmlContent = Get-Content -Path $XmlFile -Raw -Encoding UTF8
Write-Host "📄 読込: $XmlFile"
Write-Host "   サイズ: $($xmlContent.Length) 文字"

# Convert to UTF-8 bytes
$utf8 = [System.Text.Encoding]::UTF8
$xmlBytes = $utf8.GetBytes($xmlContent)

# --- Windows API definitions ---
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class ClipboardHelper {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool OpenClipboard(IntPtr hWndNewOwner);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool EmptyClipboard();

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool CloseClipboard();

    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr SetClipboardData(uint uFormat, IntPtr hMem);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern uint RegisterClipboardFormat(string lpszFormat);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GlobalAlloc(uint uFlags, UIntPtr dwBytes);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr GlobalLock(IntPtr hMem);

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool GlobalUnlock(IntPtr hMem);

    // GMEM_MOVEABLE = 0x0002
    public const uint GMEM_MOVEABLE = 0x0002;
}
"@

# Register FM clipboard format
$fmFormat = [ClipboardHelper]::RegisterClipboardFormat("Mac-XMSS")
if ($fmFormat -eq 0) {
    Write-Error "❌ クリップボード形式の登録に失敗しました"
    exit 1
}
Write-Host "🔧 FM 形式登録: Mac-XMSS (ID: $fmFormat)"

# Allocate global memory for the XML data
# XMLPaste format: 4-byte header (data length as uint32 LE) + XML bytes
$dataLength = $xmlBytes.Length
$totalSize = 4 + $dataLength

$hMem = [ClipboardHelper]::GlobalAlloc(
    [ClipboardHelper]::GMEM_MOVEABLE,
    [UIntPtr]::new($totalSize)
)
if ($hMem -eq [IntPtr]::Zero) {
    Write-Error "❌ メモリ確保に失敗しました"
    exit 1
}

# Lock and write data
$ptr = [ClipboardHelper]::GlobalLock($hMem)
if ($ptr -eq [IntPtr]::Zero) {
    Write-Error "❌ メモリロックに失敗しました"
    exit 1
}

try {
    # Write 4-byte header (data length as little-endian uint32)
    $lengthBytes = [BitConverter]::GetBytes([uint32]$dataLength)
    [Runtime.InteropServices.Marshal]::Copy($lengthBytes, 0, $ptr, 4)

    # Write XML bytes after header
    $dataPtr = [IntPtr]::Add($ptr, 4)
    [Runtime.InteropServices.Marshal]::Copy($xmlBytes, 0, $dataPtr, $dataLength)
} finally {
    [ClipboardHelper]::GlobalUnlock($hMem) | Out-Null
}

# Set clipboard
$opened = [ClipboardHelper]::OpenClipboard([IntPtr]::Zero)
if (-not $opened) {
    Write-Error "❌ クリップボードを開けませんでした"
    exit 1
}

try {
    [ClipboardHelper]::EmptyClipboard() | Out-Null
    $result = [ClipboardHelper]::SetClipboardData($fmFormat, $hMem)

    if ($result -eq [IntPtr]::Zero) {
        Write-Error "❌ クリップボードへの設定に失敗しました"
        exit 1
    }

    Write-Host "✅ クリップボードに設定完了!"
    Write-Host "   形式: Mac-XMSS (FM Script Steps)"
    Write-Host "   データ: $dataLength bytes"
    Write-Host ""
    Write-Host "→ FileMaker のスクリプトエディタで Ctrl+V を押してください"
} finally {
    [ClipboardHelper]::CloseClipboard() | Out-Null
}
