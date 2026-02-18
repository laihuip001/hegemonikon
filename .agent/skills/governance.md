---
name: Skill Governance
description: 外部 Skill の信頼性ゲート — 4 tier 権限モデル
summary: |
  外部 Skill の信頼性評価。T0(未信頼)→T3(Core) の4段階昇降格制度。
  チェックリスト付き監査プロセスで脆弱性 (26.1%) に対応。
triggers:
  - "外部Skill"
  - "Skill インストール"
  - "trust"
  - "governance"
risk_tier: "L2"
risks:
  - "外部 Skill の未検証実行によるセキュリティリスク"
reversible: true
requires_approval: true
fallbacks: ["手動で SKILL.md を review"]
---

# Skill Governance — Trust Gate

> **Origin**: arXiv 2602.12430 (Agent Skills Survey, 2026-02) — community skill の 26.1% に脆弱性
> **分類**: G-2 Logic Gate (品質管理)
> **発動**: 外部 Skill のインストール・評価・実行時

---

## 4-Tier Trust Model

| Tier | 名称 | 条件 | 許可される操作 |
|:-----|:-----|:-----|:-------------|
| **T0** | Untrusted | 初見、未検証 | `view_file` のみ (閲覧) |
| **T1** | Reviewed | Creator がコード監査済み | 実行可、ファイル書込み不可 |
| **T2** | Trusted | テスト通過 + 1週間運用 | 実行可、制限付きファイル書込み |
| **T3** | Core | HGK 自作、完全管理 | 全操作許可 |

## 昇格条件

| 遷移 | 必須条件 |
|:-----|:---------|
| T0 → T1 | Creator が SKILL.md を `view_file` で全読し、`[承認]` を発話 |
| T1 → T2 | `/vet` による検証 Pass + 7日間のインシデントゼロ |
| T2 → T3 | HGK リポジトリにマージ + `register_project.py` 登録 |

## 降格条件

| トリガー | アクション |
|:---------|:----------|
| セキュリティインシデント | 即座に T0 に降格 + WBC アラート |
| 未承認のファイル変更 | T1 に降格 |
| テスト失敗 (3回連続) | T1 に降格 |

## チェックリスト (T0 → T1 監査時)

- [ ] `SKILL.md` の frontmatter に `risk_tier`, `risks`, `reversible` が記載されているか
- [ ] 外部 API 呼出しがある場合、Protocol D で検証済みか
- [ ] ファイル書込み操作がある場合、対象パスが明示されているか
- [ ] `SafeToAutoRun: true` を使うコマンドがあるか → 全て読取専用か確認
- [ ] 暗黙の依存ライブラリがインストール済みか

## 現行 Skill の Tier 分類

| Skill | Tier | 理由 |
|:------|:-----|:-----|
| 全 15 `.agent/skills/` | **T3 (Core)** | HGK 自作、リポジトリ管理下 |
| tekhne-maker | **T3 (Core)** | HGK 自作 |

---

*v1.0 — 消化レポート 2026-02-18。arXiv 2602.12430 に基づく*
