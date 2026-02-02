# B4 KI 依存関係 (Dependencies) 実装計画

> **CCL**: `/s_/mek-`
> **Date**: 2026-02-01

---

## 目的

KI の metadata.json に `dependencies` フィールドを追加し、KI 間の依存グラフを明示化。

## 設計

```json
{
  "title": "...",
  "summary": "...",
  "dependencies": ["hegemonikon_system"],  // ← 追加
  "references": [...]
}
```

---

## Proposed Changes

| KI | dependencies |
|:---|:-------------|
| `cognitive_algebra_system` | `["hegemonikon_system"]` |
| `active_inference_implementation` | `["hegemonikon_system"]` |
| `project_hermeneus` | `["cognitive_algebra_system"]` |
| `project_pythosis` | `["cognitive_algebra_system"]` |
| `synergeia_distributed_execution` | `["hegemonikon_system"]` |
| `hegemonikon_system` | `[]` (root) |

---

## スコープ

- 6 KI のみ対象（主要なコア KI）
- 残りは必要に応じて段階的に追加

---

*B4 Implementation Plan | Pythōsis*
