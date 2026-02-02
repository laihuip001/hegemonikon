# Task: M-Series FEP Octave 実装

## 目的
FEP 2×2×2マトリクスに基づく新M-series (8モジュール) を実装

---

## Phase 5: M-Series 再設計 (Octave)

### 5.1 既存モジュール解体
- [/] 既存M-series削除 (m1-input-gate, m6-context-nexus, m7-adversarial-council, m9-protocol-loader)

### 5.2 新モジュール作成

| Code | ID | Name | 状態 |
|------|-----|------|------|
| I-E-F | M1 | Aisthēsis (知覚) | [x] |
| I-P-F | M2 | Krisis (判断) | [x] |
| I-E-S | M3 | Theōria (理論) | [x] |
| I-P-S | M4 | Phronēsis (実践知) | [x] |
| A-E-F | M5 | Peira (探求) | [x] |
| A-P-F | M6 | Praxis (行為) | [x] |
| A-E-S | M7 | Dokimē (検証) | [x] |
| A-P-S | M8 | Anamnēsis (想起) | [x] |

---

## 設計原則

- **FEP準拠**: 3軸 (Flow/Value/Tempo) × 2値 = 8セル
- **命名**: 古典ギリシャ語 (Hegemonikón整合)
- **1モジュール1責任**: 各セルに1機能のみ

## 作成されたファイル

### Skills (19ファイル, 127KB)

| Skill | SKILL.md | References |
|-------|----------|------------|
| m1-input-gate | ✅ | `intent_patterns.md`, `logic_gates.md` |
| m6-context-nexus | ✅ | `context_patterns.md` |
| m7-adversarial-council | ✅ | `wargame_scenarios.md`, `cognitive_armory.md`, `quality_assurance.md` |
| m9-protocol-loader | ✅ | `the_codex.md`, `the_codex_infra.md`, `skill_templates.md` |
| meta-prompt-generator | ✅ | `archetypes.md`, `templates.md`, `transformations.md`, `quality-checklist.md` |
| japanese-to-prompt-converter | ✅ | — |

### Rules (7ファイル)

| ファイル | 目的 |
|----------|------|
| `test-rule.md` | 自動読み込み検証用 |
| `protocol-g.md` | Git操作禁止 |
| `protocol-d.md` | 外部サービス検証 |
| `protocol-d-extended.md` | 存在系断言禁止 |
| `protocol-v.md` | バージョン検証 |
| `error-prevention-protocols.md` | P1-P9 エラー防止体系 |
| `safety-invariants.md` | 安全不変条件 |

### Workflows (6ファイル)

| ファイル | コマンド |
|----------|----------|
| `do.md` | /do |
| `forge-plan.md` | /forge-plan |
| `forge-code.md` | /forge-code |
| `flow-dev-ecosystem.md` | /flow-dev-ecosystem |
| `global-rules.md` | /global-rules |
| `update-manual.md` | /update-manual |

---

## Phase 6: モジュール精査・改良

| ID | Name | v1 | 精査 | 改良 | 最終評価 |
|----|------|-----|------|------|----------|
| M1 | Aisthēsis | ✅ | ✅ | v3.0 | A |
| M2 | Krisis | ✅ | ✅ | v3.0 | A- |
| M3 | Theōria | ✅ | ✅ | v2.0 | A- |
| M4 | Phronēsis | ✅ | ✅ | v2.0 | A |
| M5 | Peira | ✅ | ✅ | v2.0 | A |
| M6 | Praxis | ✅ | ✅ | v2.0 | A- |
| M7 | Dokimē | ✅ | ✅ | v2.0 (Synedrion追加) | A |
| M8 | Anamnēsis | ✅ | ✅ | v2.0 (Vault統合) | A |

---

## 後続タスク

- [x] **M3-M8連携検証**: M8完成後、M3のVault保存連携が正しく動作するか検証
- [x] **Vault構造初期化**: `.hegemonikon/` ディレクトリと初期ファイル作成
- [x] **/boot ワークフロー更新**: M8 Load Phaseを呼び出すよう修正

---

## ✅ 完了

Phase 5 (8モジュール作成) 完了。Phase 6 (精査・改良) 完了。Vault構造初期化完了。M3-M8連携検証完了。
