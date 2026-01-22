---
id: C-3
trigger: manual
enforcement_level: L1
---

# C-3: Structural Bottleneck Audit (システム構造監査)

## Objective

システム（コード/設計/計画）を4つの工学的観点から監査し、構造的脆弱性と将来の負債を特定する。

## Audit Perspectives

### 1. Architectural Friction

- **Scalability:** 負荷増大時のボトルネック（単一障害点、同期処理の詰まり）
- **Concurrency:** 並列処理の競合リスク（ロック、レースコンディション）

### 2. Security & Integrity

- **Data Leakage:** 機密情報/PIIがログや外部APIに流出する経路
- **Detection Logic:** 脆弱なルール（正規表現）に依存していないか

### 3. Context Integration

- **Hard-coding vs Dynamic:** ロジックのハードコードがPersonalization/Learningを阻害
- **State Management:** ステートレスによる文脈欠落

### 4. Maintainability & Portability

- **Dependency Hell:** 依存過大でデプロイ困難
- **Complexity:** スパゲッティ化の兆候

## Output Template

```markdown
## 🏗️ システム構造監査レポート

### 1. Architectural Friction
- **Defect:** [構造的弱点]
- **Fix:** [技術的解決策]

### 2. Security & Data Integrity
- **Defect:** ...
- **Fix:** ...

### 3. Context Integration
- **Defect:** ...
- **Fix:** ...

### 4. Maintainability & Portability
- **Defect:** ...
- **Fix:** ...
```
