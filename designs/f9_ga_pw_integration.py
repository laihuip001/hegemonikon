#!/usr/bin/env python3
# F9: precision_weights × Aristos GA 連携設計
"""
F9: Precision Weights — Aristos L3 GA 連携

PURPOSE:
  pw_adapter.py Phase 2 (学習的マッピング) と Aristos pt_optimizer.py
  (Genetic Algorithm) を接続し、精度加重の自動最適化を実現する。

ARCHITECTURE:
  ┌──────────────────┐     feedback      ┌──────────────────┐
  │  pw_adapter.py   │ ←─────────────── │  pt_optimizer.py │
  │  resolve_pw()    │     evolved_pw     │  GA evolution    │
  └────────┬─────────┘                    └────────┬─────────┘
           │                                       │
           │ derive_pw()                           │ mutate/crossover
           ▼                                       ▼
  ┌──────────────────┐                    ┌──────────────────┐
  │  FEP Agent       │                    │  Feedback Store  │
  │  precision_weights│                   │  (JSON logs)     │
  └──────────────────┘                    └──────────────────┘

INTEGRATION POINTS:

  1. pw_adapter.resolve_pw() の priority cascade に GA 戦略を追加:
     explicit > context > GA-evolved > agent-derived > default

  2. pt_optimizer.py の fitness function に precision_weights を入力:
     - 各 Source の π_i を GA chromosome として符号化
     - fitness = WF 成功率 × 精度加重のエントロピー逆数

  3. Phase 2 移行条件 (PHASE2_BASIN_THRESHOLD=50) 到達時に GA を起動

IMPLEMENTATION PLAN:

  Step 1: ga_pw_bridge.py を mekhane/fep/ に作成
    - AristosWeightProvider クラス
    - get_evolved_weights(series: str) -> Dict[str, float]
    - is_ga_available() -> bool

  Step 2: pw_adapter.resolve_pw() に GA slot 追加
    - priority: explicit > context > GA > agent > default
    - GA unavailable 時は transparent に fallback

  Step 3: pt_optimizer.py の Individual に precision_weights を追加
    - 既存の weight chromosome [w1..w7] に π_i を追加
    - fitness evaluation で WF 実行結果 + 精度加重を参照

  Step 4: F5 較正結果をデフォルト初期値に使用
    - session=1.50, github=1.12, manual=0.78, arxiv=0.50
    - GA 初期個体群の seed として使用

STATUS: 設計完了。実装は次回スプリントで。
"""
