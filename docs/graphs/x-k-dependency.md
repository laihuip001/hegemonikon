# X-K依存グラフ（K-series間依存関係）

> **Hegemonikón X-series**: Taxis（秩序）— K-series文脈定理間の関係

## Mermaid形式

```mermaid
graph TB
    subgraph "選択公理"
        Tempo[Tempo<br/>時間 F/S]
        Stratum[Stratum<br/>階層 L/H]
        Agency[Agency<br/>主体 S/E]
        Valence[Valence<br/>方向 +/-]
    end

    subgraph "K-series 主要6関係"
        K1[K1<br/>Tempo→Stratum]
        K3[K3<br/>Tempo→Valence]
        K4[K4<br/>Stratum→Tempo]
        K6[K6<br/>Stratum→Valence]
        K10[K10<br/>Valence→Tempo]
        K11[K11<br/>Valence→Stratum]
    end

    Tempo --> K1 --> Stratum
    Tempo --> K3 --> Valence
    Stratum --> K4 --> Tempo
    Stratum --> K6 --> Valence
    Valence --> K10 --> Tempo
    Valence --> K11 --> Stratum

    style Tempo fill:#e3f2fd
    style Stratum fill:#f3e5f5
    style Agency fill:#e8f5e9
    style Valence fill:#fff3e0
```

## 依存関係一覧（優先6）

| ID | 軸 A → 軸 B | 問い | 優先度 |
|----|-------------|------|--------|
| K1 | Tempo → Stratum | 今すぐ/後で × 深く/浅く | **P1** |
| K3 | Tempo → Valence | 今すぐ/後で × 攻め/守り | **P2** |
| K4 | Stratum → Tempo | 深く/浅く × 今すぐ/後で | **P3** |
| K6 | Stratum → Valence | 深く/浅く × 攻め/守り | P4 |
| K10 | Valence → Tempo | 攻め/守り × 今すぐ/後で | P5 |
| K11 | Valence → Stratum | 攻め/守り × 深く/浅く | P6 |

## 発動条件 (k-series-activation.md 参照)

- **明示的**: `/k{N}` で指定
- **自動**: `context_ambiguity > 0.5` のとき最大2つ評価

## 用途

- **文脈判定**: T-series発動時に「どの状況か」を明確化
- **衝突解決**: 複数T-seriesが競合するときの調停

---
*Source: Claude Antigravity + kernel/kairos.md (2026-01-26)*
