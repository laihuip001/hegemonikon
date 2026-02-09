# mekhane/pks/ PROOF

PURPOSE: 外部知識・世界モデルを提供する
REASON: エージェントは内部状態だけでなく外部情報を参照する必要がある

> **存在証明**: 外部知識・世界モデルを提供

## 必然性の導出

```
エージェントは世界を知る必要がある
→ 知識ソースへのアクセスが必要
→ pks/ (Parakletos Knowledge System) が担う
```

## 粒度

**L2/PKS**: 知識・推論エンジン

## Registry
- `push_dialog.py`: [L2/PKS] 能動的情報提示
- `external_search.py`: [L2/PKS] 外部情報検索
- `llm_client.py`: [L2/PKS] 言語モデル通信クライアント
