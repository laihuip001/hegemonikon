# LLM 論外処理の解決策

## 問題の整理

| 問題 | 症状 |
|------|------|
| **ドキュメント未読** | 演算子 `!` を「否定」と誤解 |
| **トークン節約** | 省略して楽に逃げる |
| **認知的負荷** | 長文脈で思考停止 |

---

## /sop 結果 1: 論外処理の解消

### 1. Guardrails (強制チェック)

```
問題: AI が指示を無視してショートカットを取る
解決: Guardrails = 関数またはエージェントで強制検証

実装案:
- CCL パーサーが演算子を検出
- 各演算子に対応する出力セクションを強制
- 出力がなければエラー
```

### 2. Context Engineering

```
問題: AI の「注意予算」は有限 (Context Rot)
解決: 必要な情報のみを厳選して提供

実装案:
- CCL 実行前に演算子仕様を強制注入
- 毎回 operators.md を読ませる
- 「! = 階乗」のような定義をプロンプトに埋め込む
```

### 3. Mandatory Checkpoints

```
問題: 複雑な CCL 式で途中を省略
解決: 各ステップで明示的出力を要求

実装案:
- @repeat(expr, N) → N回分の独立セクションを強制
- 各演算子 (+, -, !, ~, *, ^) に対応する見出しを要求
- 見出しがなければ「未完了」として再実行要求
```

---

## /sop 結果 2: LLM 認知的負荷

### 1. Lost-in-the-Middle 効果

```
現象: 重要情報が文脈の中央にあると無視される
対策: 重要な演算子仕様は冒頭と末尾に配置
```

### 2. Chain-of-Agents (CoA)

```
現象: 1つのLLMでは長文脈を処理しきれない
対策: 複数エージェントで分担処理

Dendron への示唆:
- CCL 式を分解して複数ターンに分割
- @repeat(expr, x2) → 2回に分けて実行
```

### 3. Hierarchical Summarization

```
現象: 長い出力で後半が劣化
対策: 出力を階層的に要約

Dendron への示唆:
- 各 Phase の出力を個別に保存
- 最後に統合
```

---

## @dendron_prep v1.0 (復元)

```ccl
@dendron_prep = 
  /bou+{goal=Dendron}              # Step 1: 意志明確化
  _/kho+{scope=MVP}                # Step 2: スコープ定義
  _/sta+{criteria=success}         # Step 3: 成功基準
  _/pre+                           # Step 4: Premortem
  _/sop+{query="OSS success"}      # Step 5: 外部調査
  _/syn+{members=Linus,DHH,Rich}   # Step 6: 偉人評議会
  _/pan                            # Step 7: 盲点発見
  _/chr{deadline=?}                # Step 8: 期限設定
  _/euk                            # Step 9: 今やるべきか
```

**9 ステップ、線形、冗長 ← これが正しい**

---

## 構造的強制の実装案

### Zero-Trust CCL Executor

```python
class ZeroTrustCCLExecutor:
    """AI を信用しない CCL 実行エンジン"""
    
    def execute(self, ccl_expr: str, output: str) -> ValidationResult:
        # 1. 演算子を抽出
        operators = self.parse_operators(ccl_expr)
        
        # 2. 各演算子に対応する出力セクションを検証
        for op in operators:
            required_section = self.get_required_section(op)
            if required_section not in output:
                return ValidationResult(
                    valid=False,
                    missing=required_section,
                    error=f"演算子 {op} に対応する出力がありません"
                )
        
        return ValidationResult(valid=True)
    
    def get_required_section(self, op: str) -> str:
        mapping = {
            "!": "## 全派生同時実行",
            "~": "## 振動",
            "*": "## 融合",
            "^": "## メタ分析",
            "+": "## 詳細",
            "_": "## ステップ",
        }
        return mapping.get(op, "")
```

---

## 次のステップ

1. **@dendron_prep v1.0 を使用** — 9 ステップで実行
2. **Zero-Trust Executor を実装** — CCL 出力検証
3. **演算子仕様の強制注入** — 実行前に operators.md を読む
