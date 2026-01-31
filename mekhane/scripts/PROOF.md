# mekhane/scripts/ PROOF

> **存在証明**: 運用・保守スクリプトを格納

## 必然性の導出

```
システムは運用・保守される
→ 自動化スクリプトが必要
→ scripts/ ディレクトリが担う
```

## 粒度

**L3/ユーティリティ**: 補助的な運用ツール

## 主要ファイル

| File | 役割 |
|------|------|
| `check_proof.py` | PROOF 検証 (CI) |
| `swarm_scheduler.py` | Synedrion スケジューラ |
| `collect_results.py` | 結果収集 |
| `cleanup_sessions.py` | セッション整理 |
