# AI のバージョン管理をどうするか

> **ID**: E8
> **想定媒体**: Zenn（技術記事）
> **想定読者**: Agent 開発者
> **フック**: AI システムの「聖域」と「実験場」を分ける

---

## 本文構成（案）

### 1. Immutable vs Mutable

| 層 | 変更可否 | 例 |
|:---|:---------|:---|
| SACRED_TRUTH.md | **不変** | 体系の不変真理 |
| kernel/ | 承認必須 | 公理・定理 |
| CCL_FREEZE.md | 凍結版 | CCL 仕様のスナップショット |
| mekhane/ | 自由に変更 | 実装コード |
| experiments/ | 自由 | 実験 |

### 2. SACRED_TRUTH — 不変の核

- 変更には Creator の明示的承認が必要
- AI が勝手に変更してはならない
- EAFP/LBYL の使い分け

### 3. CCL_FREEZE

- CCL 仕様の特定バージョンを凍結
- 破壊的変更を防ぐ
- セマンティックバージョニング

### 4. EAFP vs LBYL の場所別使い分け

| 場所 | 方針 | 理由 |
|:-----|:-----|:-----|
| kernel/ | LBYL (確認してから) | 聖域 |
| experiments/ | EAFP (やってから考える) | 遊び場 |
| 外部API | LBYL | 不可逆 |

---

*関連: C8 (Dendron), E7 (Via Negativa)*
