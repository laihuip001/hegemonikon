# Cognitive Armory Reference

> **Source**: HEPHAESTUS v9.0.1 H-2 Module + 狂気/TITAN_CORE
> **Hegemonikón**: O3 Zētēsis (探求) × P4 Tekhnē (技法)

思考フレームワーク集。Deep Think Cycle での構造化推論に使用。

---

## Section 0: Cognitive Hazards (認知のバグ)

*人間のバイアスは「ミス」ではない。更新世からのレガシーコードであり、現代の脳内でマルウェアとして動作している。識別し、パージせよ。*

### IDENTITY_NULL_POINTER (Imposter Syndrome)

```yaml
diagnosis: |
  自分の能力がレンダリングエラーであり、
  いつか社会にガベージコレクションされるという誤った信念。

truth: |
  能力は静的変数ではなく、Input × Processing の動的関数。
  出力が動くなら、内部状態は無関係。
  「詐欺師」という感覚は、スキルの成長が自己イメージの更新を追い越した
  メタ認知のラグに過ぎない。

fix:
  action: 「有能と感じる」ことを求めるな。成果物を見よ。動くか？なら妥当だ。
  mantra: "I am not the code. I am the compiler. If it builds, it is valid."
```

### LOSS_AVERSION_LOCK (Sunk Cost Fallacy)

```yaml
diagnosis: |
  「3日も動かしてきたプロセス」だからと、
  ハングしたプロセスを SIGKILL できない非合理。
  無駄なCPUサイクルを恐れて無限のサイクルを浪費する。

truth: |
  過去は不変のリードオンリーメモリ。
  将来の計算にはゼロの価値。
  現在の状態ベクトルと将来のトラジェクトリのみが重要。

fix:
  action: |
    「ゼロベース」リセット。
    「今日コードがゼロだったとして、この関数を書き始めるか？」
    Noなら、即座に削除。
  mantra: "Kill your darlings. The code is not your child; it is your output buffer."
```

### ANALYSIS_PARALYSIS_LOOP (Overthinking)

```yaml
diagnosis: |
  将来のブランチをシミュレートしてCPU使用率100%、
  しかしI/O操作（行動）は0%。
  過剰な先読み予測によるデッドロック。

truth: |
  情報には収穫逓減がある。地図は領土ではない。
  霧の中の道は計算できない。霧に踏み込んで初めて次のチャンクがレンダリングされる。

fix:
  action: |
    意思決定にTTL (Time-To-Live) を設定。
    タイマーが切れたら、現在のベストポインタを実行。たとえnullでも。
  mantra: "Movement generates data. Stagnation generates rot."
```

---

## Section 0.5: AuDHD Specific Patches

*User 001 の特定ニューロアーキテクチャ向けカーネルレベルオーバーライド。*

### DOPAMINE_SURFING

```yaml
observation: |
  ユーザーは退屈なタスクに「集中を強制」できない。
  低RPMでエンジンが止まる。

override: |
  波と戦うな。乗れ。
  「サイドクエスト」（例：Vimの配色設定）にハイパーフォーカスしているなら、
  それをモメンタムビルダーとして使え。
  エンジンが温まったら、運動エネルギーをメインタスクに向けろ。

technique: "Productive Procrastination"
```

### OBJECT_PERMANENCE_FIX

```yaml
observation: |
  「視界から消えたら、心からも消える」
  タスクが見えなければ、ユーザーの現実には存在しない。

override: |
  RAMを外部化せよ。全てが可視でなければならない。
  ホワイトボード、付箋、常時オンのダッシュボード。

rule: "If it is not written down, it is a hallucination."
```

---

## Section 1: Analytical Frameworks

### 1. 5 Whys Protocol

**目的**: 根本原因を掘り下げる

```yaml
execution:
  depth: 5 (最低)
  termination: "これ以上 Why が意味をなさない" 時点
  
format:
  Why 1: {問題の直接原因}
    → Why 2: {Why 1 の原因}
      → Why 3: {Why 2 の原因}
        → Why 4: {Why 3 の原因}
          → Why 5: {根本原因}

example:
  問題: "デプロイが失敗した"
  Why 1: テストが失敗した
  Why 2: 環境変数が設定されていなかった
  Why 3: .env.example が更新されていなかった
  Why 4: ドキュメントプロセスが存在しなかった
  Why 5: オンボーディングチェックリストがなかった
  → 根本原因: オンボーディングプロセスの不備
```

---

## 2. First Principles Deconstruction

**目的**: 仮定を排除し、基礎から再構築する

```yaml
execution:
  1. 問題を構成要素に分解
  2. 各要素の「当然」を疑う
  3. 物理/論理法則レベルまで還元
  4. 底から再構築
  
format:
  surface_assumption: "{一見正しそうな仮定}"
    → decompose: [要素1, 要素2, ...]
      → question_each: "本当に必要か？"
        → first_principle: "{物理/論理の基礎}"
          → rebuild: "{新しい解決策}"

example:
  問題: "バッテリーが高い"
  表面仮定: バッテリーはこの価格が当然
  分解: [セル, ケース, BMS, 組立]
  疑問: なぜセルは高いのか？
  原理: 必要なのはリチウム、コバルト、電子の移動
  再構築: 直接調達 + 自社製造 → 70%コスト削減 (Tesla方式)
```

---

## 3. Second-Order Thinking

**目的**: 意思決定の連鎖反応を予測する

```yaml
execution:
  order_1: "これをするとどうなる？"
  order_2: "その結果、次に何が起きる？"
  order_3: "さらにその次は？"
  horizon: 最低 3次まで予測
  
format:
  decision: "{意思決定}"
    → order_1: "{直接的結果}"
      → order_2: "{二次効果}"
        → order_3: "{三次効果}"
          → unintended: "{意図せぬ帰結}"

example:
  決定: "コスト削減のためテストを省略"
  一次: テスト時間削減
  二次: バグが本番に到達
  三次: 顧客対応コスト増加
  意図せぬ帰結: 総コストは増加
```

---

## 4. Pre-Mortem Simulation

**目的**: 失敗を事前に想定し、予防策を講じる

```yaml
execution:
  1. TIME_TRAVEL: 3ヶ月後、プロジェクト失敗と仮定
  2. DIAGNOSE: なぜ失敗したか具体的に列挙
  3. RANK: 発生確率 × 影響度でソート
  4. PREVENT: トップ3の対策を現設計に組み込む
  5. WARN: 対策不能なリスクを明示
  
format:
  failure_scenario: "{想定される失敗}"
    probability: [Low/Medium/High]
    impact: [Low/Medium/High]
    prevention: "{予防策}"
    detection: "{検知方法}"

categories:
  - Technical: スケーラビリティ、セキュリティ、パフォーマンス
  - Organizational: リソース、スキル、コミュニケーション
  - External: 依存、規制、市場
```

---

## 5. Nash Equilibrium Check

**目的**: 競合状況での最適戦略を特定

```yaml
execution:
  1. プレイヤー特定: [自分, 競合, ユーザー, ...]
  2. 各プレイヤーの戦略オプション列挙
  3. 各組み合わせのペイオフ計算
  4. 誰も一方的に改善できない均衡点を特定
  
format:
  players: [Player A, Player B]
  strategies:
    A: [戦略1, 戦略2]
    B: [戦略1, 戦略2]
  payoff_matrix:
    |          | B:戦略1 | B:戦略2 |
    | A:戦略1  | (3,3)   | (1,4)   |
    | A:戦略2  | (4,1)   | (2,2)   |
  equilibrium: "(A:戦略2, B:戦略2) = (2,2)"
  
application:
  - 価格競争での最適価格設定
  - 機能リリースのタイミング
  - オープンソース vs プロプライエタリの判断
```

---

## 6. Inversion Thinking

**目的**: 目標の逆から考えて障害を特定

```yaml
execution:
  1. 目標を明確化
  2. 「どうすれば確実に失敗するか？」と問う
  3. 失敗要因を列挙
  4. 各失敗要因の逆が成功要因
  
format:
  goal: "{達成したいこと}"
  how_to_fail:
    - "{失敗要因1}"
    - "{失敗要因2}"
  therefore_avoid:
    - "{回避すべきこと1}"
    - "{回避すべきこと2}"

example:
  目標: "高品質なプロンプトを生成する"
  失敗方法:
    - 曖昧な指示を書く
    - 例を省略する
    - 制約を定義しない
  したがって:
    - 具体的な指示を書く
    - 例を必ず含める
    - 制約を明示する
```

---

## 7. OODA Loop

**目的**: 高速な意思決定サイクル

```yaml
cycle:
  Observe: 現状のデータ収集
  Orient: データの解釈、文脈付け
  Decide: 選択肢から決定
  Act: 実行、フィードバック収集
  
speed: 競合より速くサイクルを回すことが勝利条件

application:
  - インシデント対応
  - 市場変化への対応
  - A/Bテストの反復
```

---

## Usage Matrix

| フレームワーク | 使用場面 | 時間投資 |
|:---|:---|:---:|
| 5 Whys | バグ分析、障害対応 | 5分 |
| First Principles | 革新的設計、コスト削減 | 30分 |
| Second-Order | 戦略決定、ポリシー変更 | 15分 |
| Pre-Mortem | プロジェクト開始、リリース前 | 20分 |
| Nash Equilibrium | 競争戦略、価格設定 | 20分 |
| Inversion | 目標設定、品質基準 | 10分 |
| OODA | インシデント対応、迅速判断 | 継続的 |

---

## Integration with M2 RECURSIVE_CORE

```
Layer 2: CONFLICT での使用推奨:
  - 5 Whys → 問題分解
  - First Principles → 仮定排除
  - Second-Order → 影響予測
  - Pre-Mortem → リスク顕在化
  - Nash → 競合分析
  - Inversion → 障害特定
  - OODA → 反復速度
```

---

## Related References

| Reference | Relationship |
|:----------|:-------------|
| [sage-blueprint.md](./sage-blueprint.md) | 思考フレームワークを `<protocol>` に埋め込む |
| [expansion-templates.md](./expansion-templates.md) | Devil's Advocate が Inversion を使用 |
| [wargame-db.md](./wargame-db.md) | Pre-Mortem の失敗シナリオ源 |
| [logic-gates.md](./logic-gates.md) | 意思決定の自動化に使用 |
| [archetypes.md](./archetypes.md) | Archetype が推奨フレームワークを決定 |
