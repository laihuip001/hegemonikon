# 比喩一貫性の詩人 レビュー

## 対象ファイル
`mekhane/symploke/boot_integration.py`

## 判定
発言（要改善）

## 発見事項
- **機能的語彙の過剰使用**: ファイル名 `boot_integration.py` における `integration` は実装の詳細（統合）を述べているだけで、ドメイン内の役割（「起動」や「始原」）を表現できていない。`Symploke` が「絡み合い（Interweaving）」を意味するため、`integration` はトートロジーに近い。
- **官僚的比喩の混入**: `IntentWALManager` における `Manager` は、認知プロセス（Intent）やデータベース用語（WAL）に対して企業的な「管理者」のメタファーを持ち込んでおり、哲学的・認知科学的な文脈と不協和を起こしている。`IntentWALSteward`（執事）や単に `IntentWAL` の方が適切。
- **物流・物理比喩の衝突**: `AttractorDispatcher` において、FEP由来の物理・力学用語 `Attractor`（引き寄せるもの）と、物流・輸送用語 `Dispatcher`（発送者）が衝突している。アトラクタは「引き寄せる」ものであり、「発送する」ものではない。`AttractorGuide` や `AttractorOracle` が望ましい。
- **航空メタファーの唐突な出現**: `gpu_preflight` は航空用語（飛行前点検）であり、`Boot`（起動）のメタファーとは親和性があるものの、システム全体を「乗り物（Vehicle）」とするか「計算機」とするかの揺らぎを生んでいる。

## 重大度
Low
