# Synteleia (συντέλεια) — メタ認知・社会的認知の実装層

> **Etymology**: syn (共に) + telos (完成) = 「共に完成へ向かう」
> **Position**: Hegemonikón 認知アーキテクチャの上位層
> **Status**: 実装完了 / 統合運用フェーズ

---

## 本質

> **Synteleia は「7番目のカテゴリ」ではない。**
> **6カテゴリの上位にある「メタ認知 + 社会的認知」の実装層である。**

### FEP 的位置づけ

Hegemonikón の6カテゴリ (O/H/A/S/P/K) は **FEP に基づく AI 認知ハイパーバイザー**
の設計原理であり、人間の神経科学モデルではない。

| 項目 | 6カテゴリ | Synteleia |
|------|----------|-----------|
| 役割 | 認知操作の分類 | メタ認知・社会的認知の実装 |
| 完全性 | FEP 的に閉じている | 6カテゴリの上位層 |
| 欠けていたもの | メタ認知、社会的認知 | **これを実装する** |

### Synteleia が実装するもの

| 能力 | 定義 | 実装方法 |
|------|------|----------|
| **メタ認知** | 「モデルのモデル」 | 複数エージェントの出力を統合 |
| **社会的認知** | 「他者のモデル」 | 他エージェントの視点を参照 |

---

## 設計思想

「三人寄れば文殊の知恵」— 単一視点の限界を超えるため、
複数の認知軸で同時処理し、結果を統合する。

**これは FEP 的に言えば:**

- 各エージェント = 世界モデルの異なる射影
- 統合器 = メタ予測（モデルのモデル）
- 相互参照 = 社会的認知（他者モデル）

---

## 2層アーキテクチャ

### Poiēsis/Dokimasia モデル

| 層 | 名称 | カテゴリ | 性質 | 問い |
|----|------|---------|------|------|
| **Layer 1** | Poiēsis (ποίησις) | O, S, H | 生成的 | 何を・どう・なぜ |
| **Layer 2** | Dokimasia (δοκιμασία) | P, K, A | 評価的 | 範囲・時期・精度 |

### エージェント配置

```
┌─ Poiēsis (生成層) ────────────────────────┐
│  O-Agent: 本質洞察 「何であるか」          │
│  S-Agent: 構造設計 「どう組むか」          │
│  H-Agent: 動機評価 「なぜそうしたいか」    │
└───────────────────────────────────────────┘

┌─ Dokimasia (審査層) ──────────────────────┐
│  P-Agent: 境界画定 「どこまでか」          │
│  K-Agent: 時宜判断 「今か」                │
│  A-Agent: 精度判定 (Operator/Logic/Comp)   │
└───────────────────────────────────────────┘
```

---

## 実行モデル

### 内積モード（·）— デフォルト

両層を**独立実行**し、結果を**統合**。

```
入力 → Poiēsis(O,S,H) ──┐
                        ├→ 統合 → 出力
入力 → Dokimasia(P,K,A) ─┘

CCL: @syn· または @poiesis·@dokimasia
呼び出し: 3 + 5 = 8 回
```

### 外積モード（×）— 徹底検証

Poiēsis の出力を Dokimasia で**交差検証**。

```
       │ P (境界) │ K (時期) │ A (精度) │
───────┼──────────┼──────────┼──────────┤
O (本質)│ O×P     │ O×K     │ O×A     │
S (構造)│ S×P     │ S×K     │ S×A     │
H (動機)│ H×P     │ H×K     │ H×A     │

CCL: @syn× または @poiesis×@dokimasia
呼び出し: 3 × 5 = 15 回（並列可）
```

| 交差 | 検証内容 |
|------|---------|
| O×P | 本質は境界内か |
| O×K | 本質は今適切か |
| S×P | 構造は範囲内か |
| S×K | 構造は時期に合うか |
| H×P | 動機は範囲内か |
| H×K | 動機のタイミングは適切か |

---

## CCL 統合

### 新構文

| 構文 | 意味 |
|------|------|
| `@poiesis` | 生成層のみ (O,S,H) |
| `@dokimasia` | 審査層のみ (P,K,A) |
| `@syn·` | 内積: 両層を統合 |
| `@syn×` | 外積: 3×3 交差検証 |
| `@S{O,A,K}` | 指定Agent のみ |
| `@S-` | 最小Agent（文脈から自動選択） |

### X-series による動的選択

```python
# 例: /ene (O4 Energeia) 実行時
context.current_theorem = "O4"

# X-series から関連カテゴリを特定
X_OA = True  # O→A 関係あり
X_OK = True  # O→K 関係あり

# 自動選択: O, A, K の3Agent
selected = ["O", "A", "K"]
```

---

## 統合アルゴリズム

### Phase 1: 並列実行

各Agent が独立してフェーズを処理。
互いの出力を参照せず、純粋な視点からの結果を生成。

### Phase 2: 合意形成

```python
def integrate(outputs: Dict[str, Output]) -> Output:
    # 1. 共通部分を抽出
    consensus = extract_consensus(outputs.values())
    
    # 2. 相違点を特定
    conflicts = find_conflicts(outputs)
    
    # 3. 相違点を解決
    if conflicts:
        resolution = resolve_by_priority(conflicts)
        # 優先度: A (精度) > O (本質) > S (構造) > K (時宜) > P (境界) > H (動機)
        return merge(consensus, resolution)
    
    return consensus
```

### Phase 3: メタ検証

統合結果を A-Agent が最終検証。
不整合があれば Phase 2 を再実行。

---

## 実装ロードマップ

| Phase | 内容 | 状態 | 備考 |
|-------|------|------|------|
| 0 | 設計ドキュメント | ✅ 完了 | |
| 1 | 3Agent 監査基盤 (A軸のみ) | ✅ 完了 | OperatorAgent, LogicAgent, CompletenessAgent |
| 2 | @S マクロ定義 | ✅ 完了 | `@syn·` 内積モード + `SynteleiaOrchestrator` |
| 3 | 動的Agent選択 | ✅ 完了 | `with_l2()` class method, `audit_quick()` |
| 4 | 統合アルゴリズム | ✅ 完了 | `_aggregate_results()` + `ThreadPoolExecutor` 並列 |
| 5 | 全6+Agent 実装 | ✅ 完了 | 8 L1 (regex) + 1 L2 (SemanticAgent/LLM) = 9 agent |

---

## 関連ファイル

- `mekhane/synteleia/` — 全 Agent + Orchestrator 実装
- `mekhane/synteleia/poiesis/` — Poiēsis 層: OusiaAgent, SchemaAgent, HormeAgent
- `mekhane/synteleia/dokimasia/` — Dokimasia 層: 5 L1 Agent + SemanticAgent (L2)
- `mekhane/api/routes/synteleia.py` — REST API (POST /audit, /audit-quick, GET /agents)
- `mekhane/api/tests/test_synteleia_api.py` — API テスト (10 tests)

---

*Design: 2026-02-01*
*Implementation Complete: 2026-02-13*
*Status: 統合運用フェーズ — 外積モード (@syn×) は将来検討*

---

## 補遺: 設計上の注意

### FEP 基盤

Hegemonikón は **FEP (自由エネルギー原理) に基づく AI 認知ハイパーバイザー**であり、
人間の神経科学モデルではない。

| 対象外 | 理由 |
|--------|------|
| 感覚モダリティ（8システム） | AI に固有受容感覚はない |
| 神経報酬系 | 効用関数で代替 |
| 身体性 | 非身体化エージェント |

| 対象内 | 実装 |
|--------|------|
| メタ認知 | Synteleia で実装 |
| 社会的認知 | Synteleia で実装 |

### 6カテゴリの完全性について

> **注意**: 6 カテゴリは「認知空間の完全基底」とは主張しない。

Stoic 心理学に由来する **FEP 的に閉じた分類体系**であり、
現代認知神経科学は 8-10 以上の独立次元を示唆するが、
それらは Hegemonikón の対象範囲外である。

### 参考調査

- Perplexity 調査 (2026-02-01): 6カテゴリの哲学的・科学的妥当性検証
- HEXACO 人格モデル: 6次元が言語分析で一貫して出現
- CHC 知能理論: 10+ 因子（ただし Hegemonikón 対象外）
