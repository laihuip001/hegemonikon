# X-T依存グラフ（T-series間依存関係）

> **Hegemonikón X-series**: Taxis（秩序）— 定理間の従属関係

## Mermaid形式

```mermaid
graph LR
    subgraph "認知サイクル"
        T1[T1 Aisthēsis<br/>知覚] --> T2[T2 Krisis<br/>判断]
        T2 --> T4[T4 Phronēsis<br/>戦略]
        T4 --> T6[T6 Praxis<br/>実行]
        T6 --> T7[T7 Dokimē<br/>検証]
        T7 --> T8[T8 Anamnēsis<br/>記憶]
        T8 -.->|循環| T1
    end

    subgraph "内省ループ"
        T5[T5 Peira<br/>探索] --> T3[T3 Theōria<br/>内省]
        T3 --> T4
    end

    style T1 fill:#e1f5fe
    style T2 fill:#fff3e0
    style T3 fill:#f3e5f5
    style T4 fill:#e8f5e9
    style T5 fill:#e1f5fe
    style T6 fill:#fff3e0
    style T7 fill:#fce4ec
    style T8 fill:#f3e5f5
```

## 依存関係一覧

| ID | From → To | 関係性 | Workflow |
|----|-----------|--------|----------|
| X-T1 | T1→T2 | 因果 | `/boot` |
| X-T2 | T2→T4 | 因果 | `/plan` |
| X-T3 | T3→T4 | 促進 | `/think` |
| X-T4 | T4→T6 | 因果 | `/do` |
| X-T5 | T5→T3 | 促進 | `/src` |
| X-T6 | T6→T7 | 因果 | `/chk` |
| X-T7 | T7→T8 | 因果 | `/rev` |
| X-T8 | T8→T1 | 循環 | `/rec` |

## 用途

- **デバッグ**: 定理発動チェーンのトレース
- **監査**: 「なぜこの定理が発動したか」の説明
- **設計**: 新ワークフロー作成時の依存確認

---
*Source: Claude.ai (2026-01-26)*
