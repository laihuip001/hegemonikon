# Workflow Artifact Standard Implementation

## 目標

全ワークフローの実行結果をチャットではなくファイルに自動保存する

## 決定事項

- [x] 保存先: mneme ディレクトリ (`/home/laihuip001/oikos/mneme/.hegemonikon/workflows/`)
- [x] 対象: 全30+ ワークフロー
- [x] トリガー: 自動保存
- [x] チャット出力: 最小限（ファイルパスと要約のみ）

## タスク

### Phase 1: 標準ドキュメント

- [x] 統一標準ドキュメント作成 (`workflow_artifact_standard.md`)
- [x] 出力ディレクトリ作成

### Phase 2: ワークフロー更新 (O-series)

- [x] `/noe` — 既存規則をmneme向けに更新
- [x] `/bou` — 既存規則をmneme向けに更新
- [x] `/zet` — Artifact規則セクション追加
- [x] `/ene` — 既存規則をmneme向けに更新

### Phase 3: ワークフロー更新 (S-series)

- [x] `/s` — (Hub, 除外)
- [x] `/met` — Artifact規則セクション追加
- [x] `/mek` — 既存規則をmneme向けに更新
- [x] `/sta` — Artifact規則セクション追加
- [x] `/pra` — Artifact規則セクション追加

### Phase 4: ワークフロー更新 (H-series)

- [x] `/pro` — Artifact規則セクション追加
- [x] `/pis` — Artifact規則セクション追加
- [x] `/ore` — Artifact規則セクション追加
- [x] `/dox` — Artifact規則セクション追加

### Phase 5: ワークフロー更新 (P-series)

- [x] `/kho` — Artifact規則セクション追加
- [x] `/hod` — Artifact規則セクション追加
- [x] `/tro` — Artifact規則セクション追加
- [x] `/tek` — Artifact規則セクション追加

### Phase 6: ワークフロー更新 (K/A-series)

- [x] `/k` — (Hub, 除外)
- [x] `/euk` — Artifact規則セクション追加
- [x] `/chr` — Artifact規則セクション追加
- [x] `/tel` — Artifact規則セクション追加
- [x] `/sop` — 既存規則をmneme向けに更新
- [x] `/a` — (Hub, 除外)
- [x] `/dia` — Artifact規則セクション追加
- [x] `/pat` — Artifact規則セクション追加
- [x] `/gno` — Artifact規則セクション追加
- [x] `/epi` — Artifact規則セクション追加

### Phase 7: ワークフロー更新 (X/その他)

- [x] `/x` — (Hub, 除外)
- [x] `/ax` — Artifact規則セクション追加
- [x] `/eat` — 既存規則をmneme向けに更新

### Phase 8: 検証・コミット

- [x] ワークフロー更新確認
- [ ] コミット
