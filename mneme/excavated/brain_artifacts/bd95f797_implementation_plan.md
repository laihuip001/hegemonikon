# .gemini → Hegemonikon 統合計画

## 目的

`.gemini/` の内容を `C:\Users\raikh\Hegemonikon` に統合し、Git一元管理を実現する。

---

## 現状比較

| パス | .gemini | Hegemonikon | 方針 |
|------|---------|-------------|------|
| `GEMINI.md` | ✅ 最新 | ❌ なし | **コピー** → `kernel/` |
| `.agent/workflows/` | ✅ 最新 | ✅ 空 | **コピー** |
| `.agent/rules/` | ✅ あり | ✅ あり | **マージ確認** |
| `.agent/skills/m*` | ✅ 最新 | ✅ 既存 | **上書き** (どちらが最新か確認) |
| `.agent/scripts/` | ✅ あり | ❌ なし | **コピー** |
| `README.md` | ✅ あり | ❌ なし | **コピー** |
| `.env.local` | ✅ あり (API Key) | ❌ なし | **コピー** (.gitignore必須) |

---

## 統合方針

### 案A: シンボリックリンク (推奨)

```
C:\Users\raikh\.gemini → C:\Users\raikh\Hegemonikon\runtime
```

- Antigravityは `.gemini` を参照し続ける
- 実体は Hegemonikon リポジトリ内
- Gitで一元管理

### 案B: 直接コピー

1. `.gemini/*` を `Hegemonikon/` にコピー
2. `.gemini` は削除または別名保存
3. シンボリックリンク作成

---

## 提案ディレクトリ構造

```
Hegemonikon/
├── kernel/
│   ├── doctrine.md (既存)
│   └── GEMINI.md (← .gemini から移動)
├── skills/
│   ├── m1-aisthesis/
│   │   └── SKILL.md (← 最新版で上書き)
│   └── ... (M2-M8)
├── .agent/
│   ├── workflows/ (← .gemini から移動)
│   ├── rules/ (マージ)
│   └── scripts/ (← .gemini から移動)
├── runtime/ (新規: Antigravity用シンボリックリンク先)
│   └── .env.local (← API Key)
└── .gitignore (runtime/.env.local 追加)
```

---

## 実行手順

1. Hegemonikon の skills/ と .gemini の skills/ を比較
2. 最新版で上書き
3. Workflows, Scripts をコピー
4. GEMINI.md を kernel/ に配置
5. シンボリックリンク作成
6. Git コミット

---

## リスク

| リスク | 対策 |
|--------|------|
| Antigravity が .gemini を見つけられない | シンボリックリンクで解決 |
| API Key が Git に入る | .gitignore 必須 |
| 既存ファイルの上書き | 事前にバックアップ |
