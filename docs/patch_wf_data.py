#!/usr/bin/env python3
"""Patch wf-data.js with enriched phases and usecases extracted from source reading."""
import json, re

# Rich data extracted from reading all 24 WF source files
PATCHES = {
    "noe": {
        "phases": [
            "STEP 0: SKILL.md読込 — 必須・省略不可。環境強制で本体を開く",
            "STEP 0.5: Gnōsis検索 — 内部知識ベースからの先行知識取得",
            "Ph0 Prolegomena: 図式の定義域J選択 — 分析対象の圏を特定する",
            "Ph1 Excavation: 前提を炙り出す — 暗黙の仮定を表面化。「当然」を疑う",
            "Ph2 Genesis: 仮説=Coneの射を生成 — 複数の視点から仮説を構成する",
            "Ph3 Kalon: 普遍性検証 (L3のみ) — 仮説が普遍的構造を持つか検証",
            "Ph4 Synthesis: 射の合成 (L3のみ) — 複数の洞察を統合する",
            "Ph5 Dokimasia: 忠実性テスト — 結論が元の問題に忠実かを検証",
            "Ph6 Theoria: Yoneda完全性 (L3のみ) — 全ての射が考慮されたか最終確認"
        ],
        "usecases": [
            "体系の根本設計を見直す時 — 「この構造は本当に正しいか？」",
            "パラダイム転換が必要な時 — 既存の前提を全て疑い再構築",
            "「本質は何か」を問う時 — 表層ではなく構造的本質を追求",
            "外部レビュー結果の構造的欠陥を根本から再分析する時",
            "nous: 抽象原理の抽出 — 具体例から普遍的パターンを見出す",
            "phro: 実践判断 — 「どうすべきか」の即座の洞察",
            "meta: 認識の認識 — 「なぜそう考えたか」のメタ分析",
            "separate: 複合問題を独立した部分に分離して個別解決",
            "align: 異なる視点の整合性調整 — 矛盾の解消"
        ]
    },
    "bou": {
        "phases": [
            "Ph0 私の望み提示: Creator に3-5個の「こうしたい」をたたき台として提示",
            "Ph1 対話: 5 Whysで「なぜそれを望むか」を掘り下げる",
            "Ph2 深掘り: 多面的な問いで望みの本質を明確化する",
            "Ph3 衝動vs熟慮: 望みが衝動的(0-30)か熟慮的(70-100)かをスコア判定",
            "Ph4 実現可能性: 2×2マトリクス(緊急度×重要度)で望みを配置",
            "Ph4.5 6W3H具体化: Who/What/When/Where/Why/Which + How/How much/How long",
            "Ph5 優先順位+行動: 最終的な優先順を決定し、/ene への橋渡し"
        ],
        "usecases": [
            "セッション開始時に「今日は何をやるか」を明確化",
            "複数のやりたいことが競合 → voli派生で葛藤解決(Frankfurt階層的意志理論)",
            "やるべきだとわかっているのにできない → akra派生で意志-行為乖離を克服",
            "desir: 純粋欲動の探索 — 葛藤なしに「本当に欲しいもの」を発見",
            "長期プロジェクトの方向性を再確認 — 「まだこれを望んでいるか？」",
            "voli: 複数の望みが矛盾する時 — 高次意志と低次意志の対話で解決",
            "「なぜ」を5回繰り返して表層的な望みから根源的な望みへ到達"
        ]
    },
    "zet": {
        "phases": [
            "Ph1(η) 問い生成: 摩擦点/成功の裏/前提の棚卸しから問いの種を発見",
            "Ph2(μ) 平坦化: メタ問い（問いの問い）を具体的で扱える問いに変換",
            "Ph3 問い候補の提示: 発見した問いをランク付けしてCreatorに提示",
            "Ph4 Kleisli Bind: Creator選択 → /noe で深掘り、または次のT適用"
        ],
        "usecases": [
            "「何か引っかかる」という違和感を具体的な問いに言語化 → anom派生",
            "設計前に「本当に必要か」を問い直す — 前提の棚卸し",
            "anom: 異常検出 — データやシステムの「おかしい」を発見",
            "hypo: 仮説生成 — 「もし〜なら」のシナリオを複数生成",
            "eval: 仮説評価 — 生成した仮説の妥当性を検証",
            "abduction: 最良説明の推論 — 観測結果から最も蓋然性の高い原因を推定",
            "/poc 統合: poc(概念実証)を --mode=poc として吸収",
            "/why 統合: why(5 Whys分析)を --mode=five-whys として吸収",
            "新しいアイデアが浮かんだ時 — 問いの形にすることで検証可能にする"
        ]
    },
    "ene": {
        "phases": [
            "Ph0.1 Risk Tag: 操作の破壊度を🟢低/🟡中/🔴高で判定",
            "Ph0.2 Graduated Supervision: Self/Premortem/External を選択",
            "Ph0.3 Graduated Enforcement: Anti-Skip/Schema/Guardrails を選択",
            "Ph1 実行: 計画に基づく変更+Self-Audit。各ファイルを読込→変更→検証",
            "Ph1.5 Quality Gate: Metrika/Chreos/Palimpsest で変更ファイルを自動検証",
            "Ph2 検証: Build→Lint→Unit→Integration の4段階Early Catch検証",
            "Ph3 偏差検知: 計画と成果物の差分を確認(スコープ/完全性/トレーサビリティ)",
            "Ph3.5 動的リプランニング: 偏差検出時に修正/迂回/縮小/中断を判断",
            "Ph4 完了確認: 変更サマリー+全ゲート結果+コミット提案(Conventional Commits)",
            "Ph5 安全弁: 復元ポイント+変更一覧+影響範囲のロールバック準備"
        ],
        "usecases": [
            "計画承認後の実装作業全般 — /bou で望みを決め /ene で実行",
            "「y」で暗黙発動 — 計画を承認すると自動的に /ene フローが始まる",
            "外部フィードバック反映 → constructive派生: 批判を成長に変換",
            "flow: 没入実行 — 中断なしで集中して作業を完了",
            "prax: 過程重視 — 成果物より実行プロセスの質を重視",
            "pois: 成果重視 — 具体的な成果物の完成を最優先",
            "リスク🔴のタスク — 必ず状態スナップショットを取得してから実行",
            "テスト3回連続失敗 — Creator に報告し判断を委任"
        ]
    },
    "met": {
        "phases": [
            "STEP 0: SKILL.md読込 — S1 Metron 正本参照",
            "Ph1 スケール評価: Micro(局所)/Meso(中間)/Macro(全体)の3層で問題を配置",
            "Ph2 粒度決定: 分析に適切な解像度を選択",
            "Ph3 トレードオフ評価: 粒度を変えたときのコスト/ベネフィットを比較"
        ],
        "usecases": [
            "問題の粒度で迷った時 — Micro/Meso/Macroのどれで考えるべきか",
            "fermi: フェルミ推定 — 桁数レベルで素早く見積もる",
            "kiss: 簡素化 — 複雑なものを最小限に削ぎ落とす",
            "extreme: 極端化 — 限界ケースで思考実験する",
            "cognitive_load: 認知負荷の評価 — ユーザーの処理能力に合わせる",
            "definition: 定義精度の決定 — どこまで厳密に定義すべきか",
            "approximation: 近似レベルの判断 — 正確さと速度のトレードオフ"
        ]
    },
    "mek": {
        "phases": [
            "STEP 0: SKILL.md読込 — S2 Mekhanē 正本参照",
            "STEP 1 調査: 必要な方法の要件を特定+既存リソースの調査",
            "STEP 2 設計: WF/Skill の構造設計(YAML frontmatter + markdown body)",
            "STEP 3 生成: ファイル生成+依存関係の解決",
            "STEP 4 テスト: 生成物のドライラン+エラー検出",
            "STEP 5 統合: registry.yaml への登録+既存システムとの接続",
            "STEP 6 検証: エンドツーエンドテスト+回帰テスト",
            "STEP 7 完了: ドキュメント更新+コミット提案"
        ],
        "usecases": [
            "新しいWFやSkillを作りたい時 — ゼロから構造設計+生成",
            "既存WFの診断・改善 — comp(合成)で複数WFを統合",
            "comp: 複数の小さな方法を合成して大きな方法を作る",
            "inve: 逆問題 — 「結果から原因を逆算」する方法設計",
            "adap: 既存方法を新しい文脈に適応させる",
            "model: 問題をモデル化して抽象的に解く",
            "yagni: 不要な機能を削減 — You Ain't Gonna Need It",
            "nudge: 行動変容を促す小さな仕組みの設計",
            "visual: 概念を可視化するための方法設計"
        ]
    },
    "sta": {
        "phases": [
            "STEP 0: SKILL.md読込 — S3 Stathmos 正本参照",
            "Ph1 基準候補列挙: Must(必須)/Should(推奨)/Could(理想)で分類",
            "Ph2 基準定義: 各基準の測定方法と閾値を明確化",
            "Ph3 検証方法決定: テスト手法とPass/Fail条件を設定"
        ],
        "usecases": [
            "テストケース設計 — test派生で具体的なテスト戦略を策定",
            "完了条件の明確化 — done派生で「いつ終わりか」を定義",
            "pareto: 80/20分析 — 最も効果の高い20%に集中",
            "delta: 差分基準 — 「どれだけ変わったか」の測定基準",
            "security: セキュリティ基準の策定",
            "signal: ノイズからシグナルを選別する基準",
            "品質基準の策定 — 「良い」の定義を数値化する"
        ]
    },
    "pra": {
        "phases": [
            "STEP 0: SKILL.md読込 — S4 Praxis 正本参照",
            "Ph1 方法空間評価: Explore(新しい方法/高リスク高リターン) vs Exploit(確実/低リスク安定)",
            "Ph2 価値マッチング: 価値の緊急度/失敗コスト/学習価値を評価",
            "Ph3 方法選択: 選択された実践方法+根拠を出力"
        ],
        "usecases": [
            "実装方法の選択 — 複数のアプローチをExplore/Exploitで比較",
            "prax: 過程重視の実践 — コードを書くこと自体に内在的価値がある場合",
            "pois: 成果重視の実践 — Must/Should/Could基準で成果物を評価",
            "temp: 時間配置の実践 — 作業の順序/タイミング/リズムを最適化",
            "失敗コストが高い場合 → Exploit(確実な方法)を選択",
            "学習価値が高い場合 → Explore(新しい方法)を選択",
            "時間制約が厳しい場合 → Exploit を強制選択"
        ]
    },
    "pro": {
        "phases": [
            "STEP 0: SKILL.md読込 — H1 Propatheia 正本参照",
            "Ph1 初期反応キャッチ: 新しい情報/提案に対する最初の感覚を捕捉",
            "Ph2 方向判定: 接近(惹かれる)/回避(避けたい)の二値判定",
            "Ph3 強度評価: 直感の強さを0-100スコアで数値化"
        ],
        "usecases": [
            "判断の前に直感をキャッチ — 分析の前に「感じ」を記録",
            "新しい提案や技術に対する最初の反応を記録して後で振り返る",
            "sens: 感覚的直感 — 身体的な感覚レベルの反応(例:「胃がキリキリする」)",
            "cogn: 認知的直感 — 思考レベルの反応(例:「何か矛盾がある気がする」)",
            "soci: 社会的直感 — 対人関係レベルの反応(例:「この人は信頼できる」)",
            "複数の選択肢がある時 — 各選択肢への直感スコアを比較",
            "リスク評価の前段階 — 「なんとなく危なそう」を言語化"
        ]
    },
    "pis": {
        "phases": [
            "STEP 0: SKILL.md読込 — H2 Pistis 正本参照",
            "Ph1 確信度算出: 0-100%のスコアで確信の度合いを数値化",
            "Ph2 根拠リスト: 確信を支えるエビデンスを列挙+SOURCE/TAINT分類",
            "Ph3 反証可能性チェック: 「これが間違っている場合、何で検証するか」"
        ],
        "usecases": [
            "重要判断の確信度を明示 — BC-6準拠の[確信]/[推定]/[仮説]ラベリング",
            "エビデンスの質を評価 — SOURCE(直接確認)かTAINT(間接情報)かを分類",
            "empir: 経験的確信 — 実験/観測データに基づく確信度評価",
            "ratio: 理性的確信 — 論理/推論に基づく確信度評価",
            "test: テスト的確信 — テスト結果に基づく確信度評価",
            "inter: 対人的確信 — 他者の証言/推薦に基づく確信度",
            "反証可能性がない主張を検出 — 擬似科学的な断言を防ぐ"
        ]
    },
    "ore": {
        "phases": [
            "STEP 0: SKILL.md読込 — H3 Orexis 正本参照",
            "Ph1 価値評価: 対象の価値をPositive(+)/Negative(-)で判定",
            "Ph2 欲求方向の特定: 何に惹かれ、何を避けたいかを明確化",
            "Ph3 トレードオフ分析: 欲求間の葛藤を分析"
        ],
        "usecases": [
            "技術選定で「何が魅力的か」を分析 — 合理的理由の裏にある感情的魅力",
            "価値判断の根拠を明示 — 「なぜそれを選んだか」の感情的側面",
            "intri: 内在的欲求 — 「それ自体が楽しい」",
            "instr: 道具的欲求 — 「それを使って何かを達成したい」",
            "avoid: 回避欲求 — 「それだけは嫌だ」の特定",
            "curiosity: 知的好奇心 — 「知りたい」という純粋な欲求",
            "competing: 競合する欲求の優先順位付け",
            "ambivalent: 両価的な感情(惹かれつつ恐れる)の分析",
            "social: 社会的承認欲求 — 「認められたい」の評価"
        ]
    },
    "dox": {
        "phases": [
            "STEP 0: SKILL.md読込 — H4 Doxa 正本参照",
            "Ph1 確信度評価: C(確立された信念)/U(暫定的な見解)の二値判定",
            "Ph2 永続化判断: 重要度に基づく記録フォーマット選択",
            "Ph3 記録先決定: KI(Knowledge Item)/Handoff/dispatch_logから選択"
        ],
        "usecases": [
            "重要な設計判断を後のセッションでも維持 — KIに格納",
            "学んだ教訓を信念として記録 — /byeの前に/doxで永続化",
            "sens: 感覚的信念 — 体験に基づく信念(例:「このUIは使いにくい」)",
            "conc: 概念的信念 — 理論に基づく信念(例:「FEPは認知の統一理論」)",
            "form: 形式的信念 — ルール化された信念(例:「IF テスト失敗 THEN デプロイ禁止」)",
            "delta: 信念変化追跡 — 以前の信念と現在の信念の変化を記録+分析",
            "structured: スキーマ定義付き構造化信念記録(Pythōsis Phase 3)"
        ]
    },
    "kho": {
        "phases": [
            "STEP 0: SKILL.md読込 — P1 Khōra 正本参照",
            "Ph1 対象領域の特定: 「どこで」「何の範囲で」考えるか",
            "Ph2 Micro/Meso/Macro展開: 3つのスケールで影響範囲を分析",
            "Ph3 スコープ境界の決定: In-scope/Out-of-scopeを明確化"
        ],
        "usecases": [
            "タスク開始時にスコープを明確化 — 「何をやるか/やらないか」",
            "影響範囲の見積り — 変更がどこまで波及するか",
            "file: ファイルスコープ — 特定ファイルの変更範囲",
            "module: モジュールスコープ — パッケージ/ディレクトリ単位",
            "system: システムスコープ — アプリケーション全体",
            "reference_class: 参照クラスの特定 — 統計的推定の母集団を定義",
            "スコープクリープの防止 — 「これもやろう」の衝動を制御"
        ]
    },
    "hod": {
        "phases": [
            "STEP 0: SKILL.md読込 — P2 Hodos 正本参照",
            "Ph1 経路候補の列挙: 少なくとも2-3の代替経路を生成",
            "Ph2 Explore/Exploit判断: 探索的か搾取的かの方針決定",
            "Ph3 経路選択: 最適な経路を選択+根拠を記録"
        ],
        "usecases": [
            "実装順序の決定 — 「何から始めるか」の最適な順番",
            "デバッグのアプローチ選択 → bisect派生で二分探索",
            "line: 直線的な経路 — ステップバイステップで進む",
            "bran: 分岐経路 — 条件に応じて異なるルートを取る",
            "cycl: 循環経路 — イテレーティブに繰り返し改善",
            "search: 探索経路 — 最適解を探し回る(幅優先/深さ優先)",
            "backward: 逆算経路 — ゴールから逆に辿る",
            "bisect: 二分探索 — 問題範囲を半分ずつ絞り込む"
        ]
    },
    "tro": {
        "phases": [
            "STEP 0: SKILL.md読込 — P3 Trokhia 正本参照",
            "Ph1 パターン識別: 固定(fixed)/適応(adaptive)/創発(emergent)の分類",
            "Ph2 周期設計: 繰り返し頻度/トリガー条件の定義",
            "Ph3 条件分岐定義: 反復継続/停止の判定基準"
        ],
        "usecases": [
            "CI/CDパイプライン設計 — 自動反復パターンの構築",
            "習慣・ルーチンの構築 — 定期的なワークフローの設計",
            "fixe: 固定軌道 — 同じパターンを繰り返す(cronジョブ等)",
            "adap: 適応軌道 — フィードバックに応じてパターンを変化",
            "emer: 創発軌道 — 初期条件から自己組織化するパターン",
            "state: 状態機械 — 有限状態の遷移パターン",
            "scurve: S曲線 — 成長→飽和のライフサイクルパターン",
            "learning: 学習曲線 — 習熟度の上昇パターン"
        ]
    },
    "tek": {
        "phases": [
            "STEP 0: SKILL.md読込 — P4 Tekhnē 正本参照",
            "Ph1 技法候補の列挙: 利用可能な技法を網羅的にリストアップ",
            "Ph2 manu/mech/auto分類: 手動/半自動/全自動の3つに分類",
            "Ph3 選定+適用: 最適な技法を選択し実行計画を策定"
        ],
        "usecases": [
            "manu: 手動技法 — 頻度が低い/人間判断が必要なタスク",
            "mech: 半自動技法 — 人間と機械の役割分担を設計",
            "auto: 全自動技法 — トリガー条件と監視アラートの設計",
            "template: テンプレート技法 — 構造化されたフォーマットで実行",
            "formal: 形式的手法 — TLA+/Alloy/Coq等で厳密性を担保",
            "arch: アーキテクチャ設計 — Layered/Microservices/Event-Driven等",
            "interface: インターフェース設計 — コンポーネント間の契約定義",
            "api: API設計 — REST/GraphQL/RPC/Eventの選択+契約定義",
            "自動化の判断 — N回/週を超えたら自動化を検討する閾値"
        ]
    },
    "euk": {
        "phases": [
            "STEP 0: SKILL.md読込 — K1 Eukairia 正本参照",
            "Ph1 機会コスト評価: 「今やらなかったら何を失うか」",
            "Ph2 競合状況分析: 他のタスクとの優先度比較",
            "Ph3 時間窓の特定: チャンスが有効な期間を見積る"
        ],
        "usecases": [
            "「このタスクを今やるべきか」の判断 — 機会コストの計算",
            "技術的負債の対処タイミング — 今すぐか/後でまとめてか",
            "dete: 劣化検知 — 放置すると悪化する問題の早期発見",
            "crea: 創造機会 — 新しいアイデアを実現する好機の判定",
            "main: 保全タイミング — メンテナンスの最適時期の判定",
            "stage: ステージ判定 — プロジェクトの現在フェーズを評価",
            "技術トレンドへの対応タイミング — 早すぎず遅すぎず"
        ]
    },
    "chr": {
        "phases": [
            "STEP 0: SKILL.md読込 — K2 Chronos 正本参照",
            "Ph1 短期/中期/長期分類: 時間スケールの3層で制約を配置",
            "Ph2 依存関係分析: タスク間の前後関係と並列可能性を特定",
            "Ph3 期限設定: Hard deadline(絶対)/Soft deadline(目標)の区別"
        ],
        "usecases": [
            "期限設定 — Hard/Softの区別で現実的な計画を策定",
            "作業時間の見積り — 楽観/中央/悲観の3点見積り",
            "regu: 定期作業 — 日次/週次/月次のリズム設計",
            "dead: 締切管理 — 締切からの逆算でマイルストーンを配置",
            "esti: 見積り — 作業時間の推定精度向上",
            "依存関係のクリティカルパス分析 — ボトルネックの特定"
        ]
    },
    "tel": {
        "phases": [
            "STEP 0: SKILL.md読込 — K3 Telos 正本参照",
            "Ph1 目的の明示: 「何のためにやるか」を1文で言い切る",
            "Ph2 5 Whys: なぜを5回繰り返して根源的な目的に到達",
            "Ph3 目的階層の構築: 手段→目的の連鎖を視覚化",
            "Ph4 整合性チェック: 手段が目的にちゃんと繋がっているか検証"
        ],
        "usecases": [
            "手段が目的化していないかの定期自問 — 「これは何のため？」",
            "プロジェクトの存在意義の再確認 — 初心に立ち返る",
            "intr: 内在目的 — 行為そのものに目的がある(例:学習)",
            "extr: 外在目的 — 外部への影響が目的(例:売上向上)",
            "tran: 目的変換 — 目的の再定義/ピボット判断",
            "objective: 目標設定 — SMART基準で具体的な目標を設定",
            "「忙しいだけで成果がない」状況の原因分析"
        ]
    },
    "sop": {
        "phases": [
            "PHASE 0 目的確認: 決定事項/仮説/反証可能性を明確化(必須)",
            "PHASE 0.5 内部KB検索: AIDB+Gnōsisで既知の知識を先に確認",
            "PHASE 1a 経路選択: A(Perplexity)/B(Deep Researcher)/C(両方)を判断",
            "PHASE 1 調査依頼書生成: Hybrid Modelで冒頭最適化したプロンプト作成",
            "PHASE 1.5 デイリーブリーフ: 6列テーブル+3文結論+アクション判定",
            "PHASE 2 論点設計: 必須項目として番号付きで論点を列挙",
            "PHASE 3 品質チェック: 7項目のチェックリストで依頼書の品質を検証",
            "PHASE 4 Creator対話: 追加論点の確認+パプ君へのコピペ実行"
        ],
        "usecases": [
            "外部調査が必要な時 → 依頼書生成 → Perplexityにコピペ実行",
            "学術的根拠の調査 — Deep Researcher(Gemini GEM)で構造化調査",
            "surf: 広く浅く概要把握 — 新しい分野の全体像をスキャン",
            "deep: 徹底的に調査 — 1つのテーマを網羅的に掘り下げ",
            "prag: 使える情報/手順 — 実践的なHowTo情報を収集",
            "track: 調査進捗追跡 — 長期調査の継続管理",
            "デイリーブリーフ — 過去24時間の最新情報を構造化取得",
            "Perplexity + Deep Researcher 両方で相互補完する重要テーマ"
        ]
    },
    "pat": {
        "phases": [
            "STEP 0: SKILL.md読込 — A1 Pathos 正本参照",
            "Ph1 感情の識別: 現在の感情状態を言語化",
            "Ph2 二重傾向分析: 感情に対する感情(+→+/+→-/-→+/-→-)を分析",
            "Ph3 メタ感情の評価: 二重傾向のパターンから深層の心理構造を読む"
        ],
        "usecases": [
            "直感的な不安の分析 — 「なんとなく嫌」の正体を特定",
            "感情と認知の乖離を発見 — 「頭ではOKだが心がNO」",
            "rece: 受容 — 感情をそのまま受け入れる(変えようとしない)",
            "tran: 変換 — ネガティブな感情をポジティブなエネルギーに変換",
            "regu: 調整 — 感情の強度を適切なレベルに調整",
            "delta: 感情変化 — 時間経過による感情の変化を追跡",
            "neutral: 中立化 — 感情的バイアスを除去して客観視"
        ]
    },
    "dia": {
        "phases": [
            "STEP 0: SKILL.md読込 — A2 Krisis 正本参照",
            "Ph1 モード選択: 派生モードの自動推薦+確認",
            "Ph2 対象の分析: 判定対象を構造的に分解",
            "Ph3 4層三角検証: ルール検証→知識検証→LLM検証→静的解析で多角的に判定",
            "Ph4 判定結果出力: PASS/FAIL/WARNING+根拠+改善提案"
        ],
        "usecases": [
            "設計レビュー — 計画の妥当性を批判的に検証",
            "PR検査 — コード変更の品質を4層で検証",
            "安全性判断 → /dia+ — CoVe+Synteleia監査の深い判定",
            "aff: 肯定判定 — 強みと成功要因の特定",
            "neg: 否定判定 — 弱点とリスクの特定",
            "root: 根本原因分析 — 問題の根源を追跡",
            "devil: 悪魔の代弁者 — 意図的に反論して堅牢性を検証",
            "steelman: 最強論証 — 相手の主張を最も強い形で再構成",
            "counterfactual: 反実仮想 — 「もし〜だったら」のシナリオ分析",
            "epochē: 判断停止 — 結論を急がず保留する",
            "audit: 消化品質監査 — /eat の結果を検証",
            "panorama: 6層スキャン — 全体を俯瞰して死角を発見",
            "cold_mirror: 冷徹な鏡 — 感情を排除した客観的評価",
            "explore: UIテスト — ブラウザで実際に動作確認"
        ]
    },
    "gno": {
        "phases": [
            "STEP 0: SKILL.md読込 — A3 Gnōmē 正本参照",
            "Ph1 経験の振り返り: 何が起きたか/何を感じたかを整理",
            "Ph2 パターン抽出: 繰り返し現れる構造を特定",
            "Ph3 格言化+条件記述: IF-THEN形式で再利用可能な教訓にする"
        ],
        "usecases": [
            "セッション終了時に教訓を抽出 — /bye の前に /gno で法則化",
            "失敗からの法則化 — 「二度と同じ間違いをしない」ための原則",
            "analogy: 類推 — 8つのモードでアナロジーを生成",
            "rule: 法則化 — 繰り返しパターンを明示的なルールに変換",
            "invariant: 不変量の特定 — 変化の中で変わらないものを見つける",
            "principle: 原則の策定 — 行動指針を作成",
            "story: 物語化 — 教訓をストーリーとして記憶に残す",
            "check: 格言の検証 — 既存の格言が今でも有効か確認",
            "personify: 擬人化 — 概念に人格を与えて理解を深める",
            "成功パターンの再利用 — 「うまくいった方法」を格言化して標準化"
        ]
    },
    "epi": {
        "phases": [
            "STEP 0: SKILL.md読込 — A4 Epistēmē 正本参照",
            "Ph1 信念の特定: 検証対象の信念/仮説を明確化",
            "Ph2 正当化(Justification): エビデンスによる正当化の度合いを評価",
            "Ph3 真理性(Truth)検証: 信念が事実と一致するか検証",
            "Ph4 反証可能性チェック: 反例探索+予測力評価"
        ],
        "usecases": [
            "仮説を知識に昇格 — Doxa(信念)からEpistēmē(知識)へ",
            "経験則の確立 — パターンを検証済みの知識として格納",
            "prac: 実践知 — ノウハウの体系化(暗黙知の言語化)",
            "theo: 理論知 — 普遍的な原理の構築",
            "tech: 技術知 — ツール/技法の使い方を体系化",
            "case: 事例研究 — 具体的事例から一般化可能な知見を抽出",
            "transfer: 知識転移 — 異分野間で知識を適用",
            "pattern: パターン認識 — データから繰り返しパターンを抽出",
            "triz40: TRIZ40原理 — 技術的矛盾を発明原理で解決",
            "generalize: 一般化 — 具体→抽象化→普遍命題の形成",
            "typed: 型検証 — CCL出力が期待型に適合するか静的検証"
        ]
    },
    # τ層
    "boot": {
        "phases": [
            "Ph0: Identity Stack読込 — CONSTITUTION.md, behavioral_constraints.md 等の自己認識確立",
            "Ph1: 正本読込 (Anti-Stale) — hegemonikon.md, safety-invariants.md の最新版を確認",
            "Ph2: Handoff+Drift+Intent-WAL — 前セッションの引き継ぎ読込+文脈の再構築",
            "Ph2.7: Context Budget — N chat messages 確認+予算オフセット算出",
            "Ph3: 知識読込 — KI(Knowledge Items)やセッション履歴の参照",
            "Ph4: システム更新 — 前セッション以降の変更(git log)を確認",
            "Ph5: 外部入力 — Creator からの今日の目標/方針の受取",
            "Ph6: Boot Report — 起動完了レポートの生成+表示"
        ],
        "usecases": [
            "毎セッション開始時に必ず実行 — 文脈の再構築と自己認識の確立",
            "前セッションからの継続作業がある場合 — Handoffの読込で文脈を回復",
            "長いブランクの後 — Anti-Stale で正本の最新版を確認",
            "新しいプロジェクト開始時 — Identity Stack + 外部入力 で方向性を設定"
        ]
    },
    "bye": {
        "phases": [
            "品質評価: セッション全体の成果と品質を評価",
            "Git状態記録: 未コミット変更を記録/コミット提案",
            "セッションオブジェクト収集: 判断/信念/教訓を収集",
            "Value Pitch: セッションの価値を1文で要約",
            "Handoff生成: 次セッションへの引き継ぎドキュメント作成",
            "Raw Chat Export: 会話データのエクスポート",
            "Dispatch Log: CCL/WF実行履歴の記録",
            "Self-Profile更新: 自己プロファイルの更新(学んだこと)"
        ],
        "usecases": [
            "セッション終了時に必ず実行 — Handoffで文脈を保存",
            "コンテキスト圧迫(🔴)時 — 強制/byeでHandoffを自動生成",
            "教訓があるセッション — /gnoで格言化してから/byeで永続化",
            "長時間セッション — 中間セーブポイントとして/bye-を実行"
        ]
    },
    "eat": {
        "phases": [
            "Ph0: 圏の特定 — 外部知識がどの分野/文脈に属するかを判定",
            "Ph1: F構築(自由構成) — HGK体系のどの概念に対応するかマッピング",
            "Ph2: G構築(第一原理分解) — 外部知識をHGK原理で分解・再構成",
            "Ph3: η/ε構築 — 外部→内部(η)と内部→外部(ε)の変換を定義",
            "Ph4: 三角恒等式検証(/fit) — 変換の整合性を/dia+で検証",
            "Ph5: 統合実行 — 消化された知識をKI/Handoff/WFに反映",
            "Ph6: 最終検証 — Dendronチェック+品質保証"
        ],
        "usecases": [
            "論文の消化 — 学術論文をHGK体系に統合",
            "外部ブログ/レポートの消化 — 実用的知見の取り込み",
            "新しいフレームワークの学習 — 概念をHGK構造にマッピング",
            "AI研究の最新動向 — デイリーブリーフの消化"
        ]
    }
}

# Read current wf-data.js and patch
with open('/home/makaron8426/oikos/hegemonikon/docs/wf-data.js', 'r') as f:
    content = f.read()

# Parse the JSON objects from JS
def extract_js_obj(content, var_name):
    pattern = rf'const {var_name}\s*=\s*'
    m = re.search(pattern, content)
    if not m:
        return None, None, None
    start = m.end()
    # Find matching brace/bracket
    depth = 0
    i = start
    while i < len(content):
        if content[i] in '{[':
            depth += 1
        elif content[i] in '}]':
            depth -= 1
            if depth == 0:
                return start, i+1, content[start:i+1]
        i += 1
    return None, None, None

# Patch WF_DATA
start, end, wf_json = extract_js_obj(content, 'WF_DATA')
if wf_json:
    wf_obj = json.loads(wf_json)
    for cmd, patch in PATCHES.items():
        if cmd in wf_obj:
            if 'phases' in patch and len(patch['phases']) > len(wf_obj[cmd].get('phases', [])):
                wf_obj[cmd]['phases'] = patch['phases']
            if 'usecases' in patch and len(patch['usecases']) > len(wf_obj[cmd].get('usecases', [])):
                wf_obj[cmd]['usecases'] = patch['usecases']

    new_wf = json.dumps(wf_obj, ensure_ascii=False, indent=1)
    content = content[:start] + new_wf + content[end:]

# Patch TAU_DATA
start, end, tau_json = extract_js_obj(content, 'TAU_DATA')
if tau_json:
    tau_obj = json.loads(tau_json)
    for cmd in ['boot', 'bye', 'eat']:
        if cmd in tau_obj and cmd in PATCHES:
            if 'phases' in PATCHES[cmd]:
                tau_obj[cmd]['phases'] = PATCHES[cmd]['phases']
            if 'usecases' in PATCHES[cmd]:
                tau_obj[cmd]['usecases'] = PATCHES[cmd]['usecases']

    new_tau = json.dumps(tau_obj, ensure_ascii=False, indent=1)
    content = content[:start] + new_tau + content[end:]

with open('/home/makaron8426/oikos/hegemonikon/docs/wf-data.js', 'w') as f:
    f.write(content)

# Print stats
wf_obj2 = json.loads(extract_js_obj(content, 'WF_DATA')[2])
print("Patched wf-data.js:")
for cmd in sorted(wf_obj2.keys()):
    d = wf_obj2[cmd]
    print(f"  /{cmd}: {len(d.get('phases',[]))} phases, {len(d.get('derivatives',[]))} derivs, {len(d.get('usecases',[]))} usecases")
