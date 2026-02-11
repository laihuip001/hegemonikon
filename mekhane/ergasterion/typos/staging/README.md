# typos Staging Directory

このディレクトリは、AIが動的に生成したプロンプトの**暫定置き場**です。

## ライフサイクル

```
生成 → staging/ → バッチ分析 → library/ または 破棄
```

## 命名規則

| パターン | 例 | 用途 |
|----------|----|----|
| `{timestamp}_{slug}.prompt` | `20260120_2245_code-reviewer.prompt` | 自動生成プロンプト |
| `draft_{slug}.prompt` | `draft_translator.prompt` | 手動作成の下書き |

### ファイル名構成

- **timestamp**: `YYYYMMDD_HHMM` 形式
- **slug**: 小文字英数字とハイフンのみ (`[a-z0-9-]+`)
- **拡張子**: `.prompt` (typos形式)

## 保持期間

- **自動生成**: 7日後に自動レビュー対象
- **draft**: 無期限（手動で整理）

---

*このディレクトリは typos Phase 0.2 で作成されました。*
