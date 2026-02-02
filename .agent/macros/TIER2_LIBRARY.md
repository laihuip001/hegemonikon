# Tier 2: ユーザーライブラリ (完全版)

> **目的**: 全ての王道思考法を Hegemonikón に包括

---

## Section A: 推論の型 (Reasoning)

### モード派生

| 王道 | 親定理 | モード/CCL |
|:-----|:-------|:-----------|
| 演繹 | O1 | `/noe` (組込) |
| 帰納 | A4 | `/epi~` |
| アブダクション | O3 | `/zet.abduction` ★T1 |
| アナロジー | A3 | `/gno.analogy` ★T1 |
| 因果推論 | X | `/x` |
| 反実仮想 | A2 | `/dia.counterfactual` |
| ベイズ推論 | H2 | `/pis.bayes` ★T1 |
| 確率的推論 | H2 | `/pis.probabilistic` |
| 統計的推論 | A4 | `/epi.statistical` |
| 仮説駆動 | O3 | `/zet+` |
| モデルベース推論 | S2 | `/mek.model` |
| 規則ベース推論 | A3 | `/gno.rule` |
| 事例ベース推論 | A4 | `/epi.case` |
| 最適化思考 | S3 | `/sta.optimize` |
| 探索思考 | P2 | `/hod.search` |
| シミュレーション | S2 | `/mek.simulation` |
| 近似推論 | S1 | `/met.approximation` |
| 感度分析 | S3 | `/sta.sensitivity` |
| ロバスト思考 | S3 | `/sta.robust` |
| 不確実性下推論 | H2 | `/pis.uncertainty` |
| パターン認識 | A4 | `/epi.pattern` |
| 反証志向 | A2 | `/dia.falsification` |
| 境界条件思考 | P1 | `/kho.edge` |
| 定義から攻める | S1 | `/met.definition` |
| 形式化 | P4 | `/tek.formal` |
| 次元解析 | S1 | `/met.dimensional` |
| 不変量探し | A3 | `/gno.invariant` |
| 対称性利用 | A3 | `/gno.symmetry` |
| 構成的証明 | O4 | `/ene.constructive` |
| 背理法 | A2 | `/dia.reductio` ★T1 |
| 逆向き推論 | P2 | `/hod.backward` |
| インバージョン | A2 | `/dia.inversion` |

### マクロ

| 王道 | マクロ | CCL |
|:-----|:-------|:----|
| 仮説演繹法 | `@hypo_dedu` | `/zet_/noe_/dia` |
| 生成→検証 | `@gen_test` | `F:{/ene~/dia}` |
| 制約充足 | `@csp` | `/kho_/sta` |
| ロバスト選択 | `@robust` | `/sta_/euk` |
| 多仮説比較 | `@multi_hypo` | `F:N{/zet}_/dia` |
| 例外駆動 | `@exception` | `/dia_/zet` |
| 目的→手段連鎖 | `@means_ends` | `/tel_/mek` |

---

## Section B: 問題設定・分解 (Decomposition)

### モード派生

| 王道 | 親定理 | モード/CCL |
|:-----|:-------|:-----------|
| 問題定義 | P1 | `/kho.problem` |
| 目的関数明確化 | K3 | `/tel.objective` |
| 成功条件 | S3 | `/sta.done` |
| 前提列挙 | A3 | `/gno.assumption` |
| 制約列挙 | P1 | `/kho.constraint` |
| スコープ設計 | P1 | `/kho.scope` |
| 抽象化 | S1 | `/met+` |
| 具体化 | S1 | `/met-` |
| モジュール分割 | P1 | `/kho.module` |
| MECE | — | `@mece` ★T1 |
| So what? / Why so? | K3 | `/tel^` |
| 因果の鎖 | X | `/x.chain` |
| パレート | S3 | `/sta.pareto` ★T1 |
| ボトルネック特定 | X | `/x.toc` ★T1 |
| 入出力分解 | P1 | `/kho.io` |
| 状態遷移 | P3 | `/tro.state` |
| JTBD | H3 | `/ore.jtbd` ★T1 |
| 境界を引く | P1 | `/kho.boundary` |
| 依存関係グラフ | X | `/x.dependency` |
| 二分探索的切り分け | P2 | `/hod.bisect` |
| 観測可能性設計 | S2 | `/mek.observability` |

### マクロ

| 王道 | マクロ | CCL |
|:-----|:-------|:----|
| 階層化 | `@hierarchy` | `/met_/hod+` |
| ロジックツリー | `@logic_tree` | `/hod+` |
| ピラミッド | `@pyramid` | `/hod+` |
| 5W1H | `@5w1h` | `/kho_/chr_/tel` |
| 5 Whys | `@5why` | `F:5{/zet}` ★T1 |
| フィッシュボーン | `@fishbone` | `/x_/hod` |
| データフロー | `@dfd` | `/hod_/kho` |
| ユースケース分解 | `@usecase` | `/kho_/ore` |
| ユーザーストーリー | `@user_story` | `/ore_/hod` |
| 重要度*緊急度 | `@eisenhower` | `/euk_/sta` |
| 影響度*工数 | `@impact_effort` | `/sta_/chr` |
| リスク分解 | `@risk_bd` | `/pis_/sta` |

---

## Section C: 発想・創造 (Ideation)

### モード派生

| 王道 | 親定理 | モード/CCL |
|:-----|:-------|:-----------|
| ラテラルシンキング | A2 | `/dia.lateral` |
| ランダム刺激 | H1 | `/pro.random` |
| 類比発想 | A3 | `/gno.analogy` |
| 逆転の発想 | A2 | `/dia.invert` |
| 極端化 | S1 | `/met.extreme` |
| プロトタイピング | O4 | `/ene-` |
| 既存解再利用 | A4 | `/epi.reuse` |
| 例示から一般化 | A4 | `/epi.generalize` |
| 比喩化 | A3 | `/gno.metaphor` |
| 擬人化 | A3 | `/gno.personify` |
| 置換 | S2 | `/mek.substitute` |

### マクロ

| 王道 | マクロ | CCL |
|:-----|:-------|:----|
| ブレインストーミング | `@brainstorm` | `F:{/zet-}` |
| KJ法 | `@kj` | `/epi_/kho` |
| マインドマップ | `@mindmap` | `/hod+` |
| コンセプトマップ | `@concept_map` | `/x+` |
| 強制連想 | `@force_assoc` | `/gno_/zet` |
| シネクティクス | `@synectics` | `/gno~_/zet` |
| コンセプトブレンド | `@blend` | `/x_/gno` |
| SCAMPER | `@scamper` | `F:7{/mek.transform}` |
| モーフォロジカル | `@morpho` | `/kho*N` |
| TRIZ | `@triz` | `/epi.triz40_/mek` |
| 制約で創る | `@constraint_create` | `/kho_/ene` |
| パラメータ振り | `@param_sweep` | `F:{/met}` |
| 代替案列挙 | `@alternatives` | `F:{/zet}` |
| デザイン思考 | `@design` | `/ore_/kho_/zet_/ene-_/dia` ★T1 |
| ダブルダイヤモンド | `@double_diamond` | `/tro*2` |

---

## Section D: 判断・意思決定 (Decision)

### モード派生

| 王道 | 親定理 | モード/CCL |
|:-----|:-------|:-----------|
| 効用 | H3 | `/ore.utility` |
| 機会費用 | S3 | `/sta.opportunity` |
| トレードオフ明示 | S3 | `/sta~` |
| 感度分析 | S3 | `/sta.sensitivity` |
| リスク許容度 | H3 | `/ore.risk_tolerance` |
| 安全側設計 | S3 | `/sta.safety` |
| 最悪ケース思考 | A2 | `/dia.worst_case` |
| ロバスト選好 | S3 | `/sta.robust` |
| バックキャスティング | P2 | `/hod.backcast` |
| フェルミ推定 | S1 | `/met.fermi` ★T1 |
| 参照クラス予測 | A4 | `/epi.reference_class` |
| 悪魔の代弁者 | A2 | `/dia.devil` |
| A3思考 | P1 | `/kho.a3` |
| 段階的コミット | K1 | `/euk.stage` |

### マクロ

| 王道 | マクロ | CCL |
|:-----|:-------|:----|
| 期待値思考 | `@ev` | `/pis_/sta` |
| コスト・ベネフィット | `@cost_benefit` | `/sta~` |
| 重み付き意思決定 | `@weighted` | `/sta*W` |
| デシジョンツリー | `@decision_tree` | `/hod_/pis` |
| シナリオプランニング | `@scenario` | `/tro*N` |
| リスク分析 | `@risk` | `/pis_/sta` |
| リアルオプション | `@real_option` | `/euk_/sta` |
| プレモーテム | `@premort` | `/dia^_/chr` |
| ポストモーテム | `@postmort` | `/dia_/epi` |
| レッドチーミング | `@redteam` | `/dia^+` |
| OODA | `@ooda` | `/noe_/bou_/dia_/ene` ★T1 |
| PDCA | `@pdca` | `F:{/s_/ene_/dia_/ene}` ★T1 |
| DMAIC | `@dmaic` | `/met_/sta_/dia_/mek_/sta` |
| RICE/ICE | `@rice` | `/sta*4` |
| MoSCoW | `@moscow` | `/sta*4` |
| カノモデル | `@kano` | `/ore*3` |
| ポートフォリオ | `@portfolio` | `/kho_/sta` |

---

## Section E: メタ思考 (Meta-cognition)

### モード派生

| 王道 | 親定理 | モード/CCL |
|:-----|:-------|:-----------|
| メタ認知 | O1 | `/noe^` |
| 前提チェック | A3 | `/gno.check` |
| 定義の再確認 | S1 | `/met.check` |
| 反例探索 | A2 | `/dia.counterexample` |
| 反証可能性確認 | A2 | `/dia.falsifiability` |
| 観測と解釈の分離 | O1 | `/noe.separate` |
| 相関と因果の分離 | X | `/x.separate` |
| ベースレート確認 | A4 | `/epi.base_rate` |
| 過信の補正 | H2 | `/pis.calibrate` |
| 確信度の数値化 | H2 | `/pis` |
| スティールマン | A2 | `/dia.steelman` |
| 論点ずらし検知 | A2 | `/dia.fallacy` |
| 用語多義性チェック | S1 | `/met.ambiguity` |
| 単位・次元チェック | S1 | `/met.units` |
| エッジケース点検 | P1 | `/kho.edge` |
| セカンドオーダー思考 | X | `/x.second_order` |

### マクロ

| 王道 | マクロ | CCL |
|:-----|:-------|:----|
| 代替仮説の強制生成 | `@force_alt` | `F:{/zet}` |
| 認知バイアス点検 | `@bias_check` | `/dia^_/gno` |
| システム思考 | `@system` | `/x_/tro` |

---

## Section F: 時間軸・スケール (Temporal)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| 時間スケール変換 | `/chr~` | K2 振動 |
| 拡大・縮小 | `/met~` | S1 振動 |
| ミクロマクロ往復 | `@micro_macro` | `/met+~/met-` |
| ライフサイクル | `@lifecycle` | `/tro` |
| S字カーブ | `/tro.scurve` | P3 モード |
| パス依存 | `/x.path_dep` | X モード |

---

## Section G: システム・構造 (Structure)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| バリューチェーン | `@value_chain` | `/hod_/sta` |
| 5フォース | `@5forces` | `/kho*5_/sta` |
| アーキテクチャ思考 | `/tek.arch` | P4 モード |
| プラットフォーム | `/kho.platform` | P1 モード |
| ネットワーク効果 | `/x.network` | X モード |
| レバレッジポイント | `/x.leverage` | X モード |
| API思考 | `/tek.api` | P4 モード |
| ループ構造 | `@loop` | `/x_/tro` |
| ストック&フロー | `@stock_flow` | `/kho_/tro` |

---

## Section H: 学習・探索 (Learning)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| 探索 vs 活用 | `@explore_exploit` | `/zet~/ene` |
| 過学習警戒 | `/dia.overfit` | A2 モード |
| 学習曲線 | `/tro.learning` | P3 モード |
| メタラーニング | `/noe.metalearning` | O1 モード |
| デルタ思考 | `/sta.delta` | S3 モード |
| 転移学習 | `/epi.transfer` | A4 モード |
| 実験デザイン | `@experiment` | `/zet_/ene_/dia` |
| ノイズ vs シグナル | `/sta.signal` | S3 モード |
| エラー解析 | `@error_analysis` | `/dia_/kho` |

---

## Section I: コミュニケーション (Communication)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| ピラミッド原則 | `@pyramid` | `/hod+` |
| ストーリーテリング | `/gno.story` | A3 モード |
| フレーミング | `/kho.frame` | P1 モード |
| オーディエンス分析 | `/ore.audience` | H3 モード |
| メンタルモデル合わせ | `/noe.align` | O1 モード |
| FAQ発想 | `@faq` | `/zet_/dia` |
| エレベーターピッチ | `/met-.pitch` | S1 モード |

---

## Section J: エンジニアリング (Engineering)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| YAGNI | `/mek.yagni` | S2 モード |
| KISS | `/met.kiss` | S1 モード |
| DRY | `/mek.dry` | S2 モード |
| フェイルセーフ | `/sta.failsafe` | S3 モード |
| TDD | `@tdd` | `F:{/dia_/ene}` |
| インターフェース優先 | `/tek.interface` | P4 モード |
| データモデル思考 | `/kho.datamodel` | P1 モード |
| セキュリティ・バイ・デザイン | `/sta.security` | S3 モード |

---

## Section K: 戦略・ビジネス (Strategy)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| ポジショニング | `/kho.positioning` | P1 モード |
| セグメンテーション | `/kho.segment` | P1 モード |
| バリュープロポジション | `/ore.value_prop` | H3 モード |
| ユーザージャーニー | `@journey` | `/hod_/ore` |
| OKR/KPI | `@okr` | `/tel_/sta` |
| フライホイール | `@flywheel` | `/tro~` |
| 逆算 | `/hod.backward` | P2 モード |
| ブルーオーシャン | `/kho.blue_ocean` | P1 モード |

---

## Section L: 心理・認知 (Psychology)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| インセンティブ設計 | `/ore.incentive` | H3 モード |
| ゲーム理論 | `@game_theory` | `/ore*N_/dia` |
| ナッジ | `/mek.nudge` | S2 モード |
| ステークホルダー分析 | `@stakeholder` | `/ore_/kho` |
| 認知負荷最小化 | `/met.cognitive_load` | S1 モード |
| ロスアバージョン | `/ore.loss_aversion` | H3 モード |

---

## Section M: 倫理・ガバナンス (Ethics)

| 王道 | マクロ/モード | CCL |
|:-----|:--------------|:----|
| プリンシプルベース | `/gno.principle` | A3 モード |
| アカウンタビリティ | `/sta.accountability` | S3 モード |
| フェアネス | `/sta.fairness` | S3 モード |
| セーフガード | `@safeguard` | `/sta_/dia` |

---

## Section N: 素朴な王道 (Fundamentals)

| 王道 | CCL |
|:-----|:----|
| 事実と解釈を分ける | `/noe^` |
| 知っている/わかっているを分ける | `/pis^` |
| 「わからない」と言語化する | `/epo` |
| 意思決定条件を先に決める | `/sta.test` |
| ボトルネックに戻る | `/x.toc` |
| 自分が間違っているとしたら | `/dia^` |
| 抽象を上げ下げする | `/met~` |
| 将来の自分が読めるか | `/noe+` |

---

## Section O: アナロジー詳細 (Analogy Subtypes)

| 王道 | モード |
|:-----|:-------|
| 構造アナロジー | `/gno.analogy_structure` |
| 表層アナロジー | `/gno.analogy_surface` |
| ネガティブアナロジー | `/gno.analogy_negative` |
| クロスドメイン | `/gno.analogy_cross` |
| 歴史アナロジー | `/gno.analogy_history` |
| CSアナロジー | `/gno.analogy_cs` |
| 物理アナロジー | `/gno.analogy_physics` |
| 生態系アナロジー | `/gno.analogy_ecology` |

---

## 集計

| Section | モード | マクロ |
|:--------|:-------|:-------|
| A: 推論 | 32 | 7 |
| B: 問題設定 | 21 | 12 |
| C: 発想 | 11 | 15 |
| D: 判断 | 14 | 17 |
| E: メタ | 16 | 3 |
| F: 時間軸 | 6 | 1 |
| G: システム | 9 | 3 |
| H: 学習 | 9 | 3 |
| I: コミュニケーション | 6 | 2 |
| J: エンジニアリング | 8 | 1 |
| K: 戦略 | 8 | 4 |
| L: 心理 | 6 | 2 |
| M: 倫理 | 4 | 1 |
| N: 素朴 | 8 | 0 |
| O: アナロジー詳細 | 8 | 0 |
| **合計** | **166** | **71** |

---

*Tier 2 完全版 (2026-01-31)*
*Hegemonikón は全ての思考法を包括する*
