# PROOF: [L2/インフラ] <- mekhane/pks/

PURPOSE: 能動的知識プッシュ (PKS) エンジンにより、コンテキストに応じた知識を先回りで提示する
REASON: 受動的な検索ではなく、AI 側から能動的に関連知識を提供する仕組みが必要だった

## 存在証明

A0 (FEP) → 予測誤差最小化には能動的情報取得が必要
→ P3 (情報永続化) → 永続化された情報の能動的表面化が必要
→ **mekhane/pks/** が存在しなければならない

## 責務

Proactive Knowledge Surface (PKS): Pull 型検索 (Gnōsis) を Push 型に逆転し、
知識が自らコンテキストに語りかける機構を提供する。

## 依存

- mekhane/anamnesis (GnosisIndex, LanceDB)
- mekhane/fep (リスクタグ)