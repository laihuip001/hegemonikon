# Workflow Catalog — 全ワークフロー一覧

## Ω層 (Series 統合)

| WF | 名称 | 説明 |
|:---|:-----|:-----|
| /o | O-series Peras | 純粋認知の統合判断 |
| /s | S-series Peras | 戦略設計の統合判断 |
| /h | H-series Peras | 動機の統合判断 |
| /p | P-series Peras | 環境配置の統合判断 |
| /k | K-series Peras | 文脈判断の統合 |
| /a | A-series Peras | 精度保証の統合判断 |
| /x | X-series | 定理間の従属関係を可視化 |
| /ax | 全体分析 | 6 Series 極限を多層収束 |

## Δ層 (定理レベル)

| WF | 定理 | 説明 | よく使う場面 |
|:---|:-----|:-----|:-----------|
| /noe | O1 Noēsis | 最深層思考・直観 | 本質を問う |
| /bou | O2 Boulēsis | 意志・目的の明確化 | 何を望むか |
| /zet | O3 Zētēsis | 探求・問いの発見 | 何を問うべきか |
| /ene | O4 Energeia | 行為・実装 | 意志を現実に |
| /dia | A2 Krisis | 判定・敵対レビュー | 品質判定 |
| /mek | S2 Mekhanē | 方法配置・Skill生成 | WF/Skill を作る |
| /pra | S4 Praxis | 実践・価値実現 | 方法を選ぶ |
| /pro | H1 Propatheia | 前感情・直感 | 初期傾向を評価 |
| /pis | H2 Pistis | 確信・信頼性 | 確信度を評価 |
| /ore | H3 Orexis | 欲求・価値傾向 | 欲求を評価 |
| /dox | H4 Doxa | 信念の記録 | 法則を永続化 |
| /sop | K4 Sophia | 調査依頼書生成 | 外部調査を依頼 |
| /epi | A4 Epistēmē | 知識確立 | 信念→知識に昇格 |

## τ層 (タスク実行)

| WF | 説明 | よく使う場面 |
|:---|:-----|:-----------|
| /boot | セッション開始 | 毎回最初に実行 |
| /bye | セッション終了・Handoff 生成 | 毎回最後に実行 |
| /dev | 開発プロトコル参照 | コーディング時 |
| /now | 現在地確認 | 迷った時 |
| /why | Five Whys — 根本原因 | なぜ？を繰り返す |
| /u | 主観を引き出す | AIの意見を聞く |
| /m | 本気モード | Creator が真剣な時 |
| /eat | 外部コンテンツ消化 | 論文・記事を HGK に取り込む |

## CCL マクロ (τ相当)

| マクロ | 日本語名 | CCL 展開 |
|:-------|:---------|:---------|
| @wake | 起きる | /boot+_@dig_@plan |
| @go | 即実行 | /s+_/ene+ |
| @dig | 掘る | /s+~(/p*/a)_/dia*/o+ |
| @plan | 段取る | /bou+_/s+~(/p*/k)_V:{/dia} |
| @build | 組む | /bou-_/s+_/ene+_V:{/dia-} |
| @fix | 直す | C:{/dia+_/ene+}_I:[✓]{/dox-} |
| @vet | 確かめる | /kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pis_/dox |
| @learn | 刻む | /dox+_*^/u+_/bye+ |
| @read | 読む | /s-_/pro_F:[×3]{/m.read~(/noe*/dia)}_/ore_~(/h*/k)_/pis_/dox- |
| @chew | 噛む | /s-_/pro_F:[×3]{/eat+~(/noe*/dia)}_~(/h*/k)_@proof_/pis_/dox- |
