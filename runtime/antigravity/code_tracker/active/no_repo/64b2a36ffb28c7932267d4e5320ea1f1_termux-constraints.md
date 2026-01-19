�# Termux制約 (Termux Constraints)

> **ステータス**: 条件付き適用 (Termux環境のみ)
> **分類**: G-1 Iron Cage (環境制御)
> **対象**: ARM64/Android環境での実行時

---

## 概要

Termux環境（Android上のLinuxエミュレーション）では、
ネイティブコンパイルが必要なライブラリが動作しない場合がある。

---

## 禁止ライブラリ (ARM64互換性なし)

| ライブラリ | 理由 |
|------------|------|
| `pandas` | C拡張のビルド困難 |
| `numpy` | BLAS/LAPACKの依存 |
| `scipy` | Fortranコンパイラ必要 |
| `lxml` | libxml2のビルド問題 |
| Rust製依存 | rustcのARM64サポート限定 |

---

## PC専用ライブラリ (Termuxでスキップ)

以下はTermux環境では自動でスキップまたはフォールバック:

| ライブラリ | 代替 |
|------------|------|
| `flet` | CLI版にフォールバック |
| `keyboard` | 非対応（グローバルフック不可） |
| `pyperclip` | `termux-clipboard-get/set` |

---

## 設計指針

```yaml
Required:
  - Pure Python優先
  - メモリ・バッテリー効率重視
  - SQLite WALモード使用
  - 軽量HTTPクライアント (httpx > requests)

Forbidden:
  - config.json の直接上書き
  - API Key のログ出力
  - rm -rf without confirmation
  - 大量メモリ消費処理
```

---

## 環境検出

```python
import os
import platform

def is_termux() -> bool:
    """Termux環境かどうかを判定"""
    return (
        os.environ.get("TERMUX_VERSION") is not None
        or "termux" in os.environ.get("PREFIX", "").lower()
        or platform.machine() in ("aarch64", "armv7l")
    )
```

---

## 発動条件

以下の場合にこのルールを参照:

- ユーザーが「Termux」「Android」「モバイル」に言及
- プロジェクトに `termux` 関連ファイルが存在
- 環境変数 `TERMUX_VERSION` が設定されている
�*cascade082Afile:///C:/Users/raikh/.gemini/.agent/rules/termux-constraints.md