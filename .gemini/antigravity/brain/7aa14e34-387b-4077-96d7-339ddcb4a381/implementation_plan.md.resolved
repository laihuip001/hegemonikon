# エピソード記憶機構 再設計計画

## 調査結果

| データソース | 読み取り | 内容 |
|:-------------|:--------:|:-----|
| `.gemini/antigravity/conversations/*.pb` | ❌ | 暗号化済み、パース不可 |
| `.gemini/antigravity/annotations/*.pbtxt` | ⚠️ | メタデータのみ (last_view_time) |
| `.gemini/antigravity/brain/{id}/` | ✅ | task.md, walkthrough.md, implementation_plan.md |
| `.gemini/antigravity/knowledge/` | ✅ | KI (知識アイテム) |
| `mneme/.hegemonikon/sessions/handoff_*.md` | ✅ | Handoff (セッション要約) |

---

## 代替アーキテクチャ: 3層エピソード記憶

```
┌─────────────────────────────────────────────────────────┐
│ L1: Episodic Session Layer (エピソード)                  │
│     ├── Handoff (Creator/AI 視点の要約)                   │
│     └── Walkthrough (実行履歴)                           │
├─────────────────────────────────────────────────────────┤
│ L2: Semantic Knowledge Layer (意味記憶)                  │
│     ├── KI (Knowledge Items)                             │
│     └── Doxa (信念永続化)                                │
├─────────────────────────────────────────────────────────┤
│ L3: Working Memory Layer (作業記憶)                      │
│     └── task.md, implementation_plan.md                  │
└─────────────────────────────────────────────────────────┘
```

---

## 実装計画

### Phase 1: データ収集強化 (/bye 拡張)

1. **Walkthrough 自動エクスポート**: /bye 時に walkthrough.md を mneme にコピー
2. **Handoff 構造化**: YAML メタデータ + Markdown 本文
3. **変更差分記録**: 各セッションの Git diff を保存

### Phase 2: 自動化 (cron/systemd)

```bash
# 1時間ごとに brain/ と knowledge/ をバックアップ
0 * * * * rsync -a ~/.gemini/antigravity/brain/ ~/oikos/mneme/.antigravity/brain/
0 * * * * rsync -a ~/.gemini/antigravity/knowledge/ ~/oikos/mneme/.antigravity/knowledge/
```

### Phase 3: 検索インデックス

- Handoff + Walkthrough を Kairos にインデックス
- /boot 時に関連エピソードを自動検索

---

## 今すぐ実行: バックアップスクリプト

```bash
#!/bin/bash
# episodic_backup.sh

BRAIN_SRC="$HOME/oikos/.gemini/antigravity/brain"
BRAIN_DST="$HOME/oikos/mneme/.antigravity/brain"
KNOWLEDGE_SRC="$HOME/oikos/.gemini/antigravity/knowledge"
KNOWLEDGE_DST="$HOME/oikos/mneme/.antigravity/knowledge"

mkdir -p "$BRAIN_DST" "$KNOWLEDGE_DST"
rsync -a "$BRAIN_SRC/" "$BRAIN_DST/"
rsync -a "$KNOWLEDGE_SRC/" "$KNOWLEDGE_DST/"
echo "[$(date)] Episodic backup complete"
```
