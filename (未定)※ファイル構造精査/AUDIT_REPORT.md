# 🔴 Forge 敵対監査レポート (Adversarial Audit)

> **監査日**: 2026-01-15
> **対象バージョン**: v2.0
> **監査姿勢**: 攻撃者・批判者の視点から、システムの弱点を徹底的に洗い出す

---

## 📊 総合評価

| カテゴリ | 評価 | 深刻度 |
|---------|------|--------|
| セキュリティ | ⚠️ 要改善 | 中〜高 |
| パフォーマンス | ⚠️ 要改善 | 中 |
| ユーザビリティ | ✅ 良好 | 低 |
| アーキテクチャ | ⚠️ 要改善 | 中 |
| コード品質 | ⚠️ 要改善 | 低〜中 |

---

## 🔓 セキュリティ脆弱性

### 1. Webサーバー: ディレクトリトラバーサル攻撃に脆弱 【高】

**問題箇所**: `start-server.ps1` Line 59

```powershell
$FilePath = Join-Path $Root $UrlPath.Replace('/', '\')
```

**攻撃シナリオ**:
```
GET /../../../Windows/System32/config/SAM HTTP/1.1
```

**現状**: `Join-Path`は`..\`を正規化しますが、エンコードされたパス（`%2e%2e%2f`）や特殊なパターンで回避される可能性があります。

**改善案**:
```powershell
$NormalizedPath = [System.IO.Path]::GetFullPath($FilePath)
if (-not $NormalizedPath.StartsWith($Root)) {
    # 拒否
}
```

---

### 2. CLI: 入力検証が不完全 【中】

**問題箇所**: `forge.ps1` Line 60-66

```powershell
if ($UserInput -match '\\.\\.[\\\\/]') { ... }
if ($UserInput -match '[<>|&;`$]') { ... }
```

**問題点**:
- 正規表現が`..`の一部パターンしか検出しない
- Unicode正規化攻撃（例: `．．／`）に対応していない
- PowerShellの`Invoke-Expression`的な攻撃ベクトルは考慮されていない

**現実的リスク**: 低（ローカルツールであり、信頼されたユーザーが使用）

---

### 3. Web UI: XSS脆弱性 【中】

**問題箇所**: `web/index.html` Line 444-447

```javascript
return `
    <div class="module-card" data-id="${m.id}">
        <h3>${m.name}</h3>
        <p class="description">${m.description || '説明なし'}</p>
    </div>
`;
```

**攻撃シナリオ**:
モジュールのファイル名や説明文に`<script>`タグを含めると、そのまま実行される。

**改善案**:
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

### 4. クリップボード操作が無条件 【低】

**問題箇所**: `forge.ps1` Line 370+

```powershell
Set-Clipboard -Value $sb.ToString()
```

**問題点**: ユーザーの確認なしにクリップボードを上書きする。悪意のあるモジュールコンテンツがコピーされる可能性。

---

## ⚡ パフォーマンス問題

### 1. index.json の毎回全読み込み 【中】

**問題箇所**: `forge.ps1` Line 82

```powershell
$json = Get-Content $Script:IndexFile -Raw -Encoding UTF8 | ConvertFrom-Json
```

**問題点**:
- 100KB+ のJSONを毎回フルパースしている
- モジュール数が増えると線形に遅くなる
- メモリ効率が悪い

**改善案**:
- 軽量なインデックスファイル（名前とパスのみ）を別途作成
- バイナリキャッシュ（CLIXML）の使用
- 遅延読み込み

---

### 2. Web UI: クライアントサイドフィルタリングの限界 【中】

**問題箇所**: `web/index.html` Line 424-433

```javascript
const filtered = indexData.modules.filter(m => { ... });
```

**問題点**:
- 120モジュールは問題ないが、1000+になると遅延が発生
- 毎キー入力でフィルタリング実行（デバウンスなし）

**改善案**:
```javascript
let debounceTimer;
searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(renderModules, 300);
});
```

---

### 3. テストスクリプトの非並列実行 【低】

**問題箇所**: `tests/test-forge.ps1`

**問題点**: 
- 各ファイルを順次処理しており、並列化されていない
- ファイルI/Oがボトルネック

---

## 🎨 ユーザビリティ問題

### 1. エラーメッセージが日本語のみ 【低】

英語ユーザーへの対応なし。国際化 (i18n) の仕組みがない。

### 2. サーバー終了時のクリーンアップなし 【低】

**問題箇所**: `start-server.ps1`

Ctrl+Cで終了した際、`$Listener.Stop()` が呼ばれない可能性がある。

**改善案**:
```powershell
try {
    # メインループ
} finally {
    $Listener.Stop()
    Write-Host "サーバーを停止しました"
}
```

### 3. 検索結果のハイライトなし 【低】

検索した文字列がどこにマッチしたか視覚的にわからない。

---

## 🏗️ アーキテクチャ問題

### 1. DRY原則違反: ディレクトリマッピングの重複定義 【中】

**問題箇所**: 
- `forge.ps1` Line 28-38
- `build-index.ps1` Line 18-73
- `tests/test-forge.ps1` Line 29-37

同じディレクトリ構造が3ファイルに重複定義されている。1箇所を変更すると他も変更が必要。

**改善案**:
```
/config/directories.json または /config/directories.ps1
```
を作成し、全ツールがここを参照する。

---

### 2. 設定ファイルの欠如 【中】

ポート番号、パス、デフォルト動作などがハードコードされている。

**改善案**:
```
/forge.config.json
{
    "server": { "port": 8000 },
    "index": { "path": "index.json" },
    "defaultCategory": "all"
}
```

---

### 3. ロギング機能の欠如 【中】

操作履歴、エラーログがどこにも記録されない。デバッグや監査が困難。

---

### 4. バージョン管理の不整合 【低】

`index.json`に`version: 2.0`があるが、他のファイルとの整合性チェックがない。

---

## 🐛 コード品質問題

### 1. 未使用変数 【低】

**問題箇所**: `forge.ps1` Line 278
```powershell
$presetDir = Join-Path $Script:BaseDir "presets"  # 使用されていない
```

### 2. 非標準動詞の使用 【低】

**問題箇所**: `forge.ps1` Line 307
```powershell
function Build-Custom-Preset  # "Build" は非承認動詞
```

PowerShellの承認動詞は`New-`、`Set-`、`Invoke-`など。

### 3. エラーハンドリングの欠如 【中】

**問題箇所**: `build-index.ps1` Line 165-166

```powershell
$json = $index | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($OutputFile, $json, ...)
```

ファイル書き込み失敗時の処理がない。

---

## 📋 改善優先度マトリクス

| 問題 | 影響度 | 修正難易度 | 優先度 |
|------|--------|-----------|--------|
| ディレクトリトラバーサル | 高 | 低 | 🔴 最優先 |
| XSS脆弱性 | 中 | 低 | 🟠 高 |
| DRY違反（設定重複） | 中 | 中 | 🟡 中 |
| デバウンス未実装 | 低 | 低 | 🟢 低 |
| 設定ファイル導入 | 中 | 中 | 🟡 中 |
| ロギング追加 | 中 | 高 | 🟡 中 |

---

## 🚀 推奨アクション

### 今すぐ（1日以内）
1. `start-server.ps1` にパス正規化チェックを追加
2. Web UIに`escapeHtml`関数を実装

### 短期（1週間以内）
3. 設定ファイル (`forge.config.json`) の導入
4. ディレクトリマッピングの共通化
5. 検索のデバウンス実装

### 中期（1ヶ月以内）
6. ロギングシステムの追加
7. 国際化 (i18n) 対応
8. テストの並列化

---

> **監査者注記**: このシステムはローカル開発ツールであり、インターネット公開を想定していないため、セキュリティリスクの実際の影響は限定的です。しかし、将来的な拡張や公開を見据えて、上記の問題を修正することを推奨します。
