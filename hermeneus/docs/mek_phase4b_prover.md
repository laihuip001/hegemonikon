# [CCL]/mek+ Hermēneus Phase 4b — Formal Prover Interface

---
sel:
  workflow: /mek+
  scope: P4b=formal_prover
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - Lean4/Dafny 連携
    - 型安全性検証
    - 数学的証明インターフェース
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 4b"
  [target: Formal Prover Interface]
  {
    /s1 "Prover Abstraction"  -- 抽象インターフェース
    /s2 "Type Checker"        -- Python 型チェック (mypy)
    /s3 "Lean4 Bridge"        -- Lean 4 形式証明 (オプション)
    /s4 "Verification Cache"  -- 証明結果キャッシュ
  }
  >> 形式的正確性保証 ✅
```

---

## Phase 4b 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | コード/出力の形式的正確性を検証 |
| **成果物** | `prover.py` |
| **依存** | `mypy` (必須), `lean4` (オプション) |
| **検証** | 型安全性 100%, 形式証明 (選択的) |

---

## 検証レイヤー

```
                    ┌──────────────────────────────────────┐
                    │         CCL Execution Result         │
                    └────────────────┬─────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
   ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
   │  Type Check   │         │  Schema Valid │         │  Formal Proof │
   │   (mypy)      │         │   (JSON)      │         │   (Lean4)     │
   └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                    ┌────────────────▼─────────────────────┐
                    │          ProofResult                 │
                    │    (verified, confidence, proofs)    │
                    └──────────────────────────────────────┘
```

---

## 実装タスク CCL

```ccl
# Phase 4b タスクリスト
let prover_tasks = [
  /s1+ "Prover Abstraction" {
    ProverInterface 抽象基底クラス
    ProofResult データクラス
    ProofType 列挙型 (TYPE, SCHEMA, FORMAL)
    verify() 統一インターフェース
  }
  
  /s2+ "Type Checker" {
    MypyProver 実装
    Python コードの型安全性検証
    型エラーの構造化レポート
    インクリメンタルチェック
  }
  
  /s3+ "Lean4 Bridge" {
    Lean4Prover 実装 (オプション)
    Lean 4 CLI ラッパー
    定理ファイル生成
    証明結果パース
  }
  
  /s4+ "Verification Cache" {
    ProofCache (SQLite)
    証明結果のキャッシュ
    キャッシュヒット判定
    TTL 管理
  }
]

F:[prover_tasks]{/ene+} >> 全タスク完了
```

---

## コンポーネント設計

### ProverInterface

```ccl
/mek "ProverInterface"
  [input: Code/Claim]
  [output: ProofResult]
  {
    class ProofType(Enum):
      TYPE = "type"         # 型チェック
      SCHEMA = "schema"     # スキーマ検証
      FORMAL = "formal"     # 形式証明
      
    @dataclass
    class ProofResult:
      verified: bool
      proof_type: ProofType
      confidence: float
      details: str
      errors: List[str]
      cached: bool = False
      
    class ProverInterface(ABC):
      @abstractmethod
      def verify(
        code: str,
        claim: Optional[str] = None
      ) -> ProofResult:
        pass
  }
```

### MypyProver

```ccl
/mek "MypyProver"
  [input: Python Code]
  [output: Type Safety Report]
  {
    class MypyProver(ProverInterface):
      def __init__(strict: bool = True):
        self.strict = strict
        
      def verify(code: str, claim: str = None) -> ProofResult:
        # 1. 一時ファイルに書き込み
        # 2. mypy --strict で検証
        # 3. 結果をパース
        # 4. ProofResult を返す
        
      def _run_mypy(path: Path) -> Tuple[int, str, str]:
        # subprocess で mypy を実行
        
      def _parse_errors(output: str) -> List[str]:
        # エラーメッセージをパース
  }
```

### Lean4Prover (オプション)

```ccl
/mek "Lean4Prover"
  [input: Mathematical Claim]
  [output: Formal Proof]
  {
    class Lean4Prover(ProverInterface):
      lean_path: Path = Path("~/.elan/bin/lean")
      
      def verify(code: str, claim: str) -> ProofResult:
        # 1. Lean 4 定理ファイルを生成
        # 2. lean4 で検証
        # 3. 結果をパース
        
      def _generate_theorem(claim: str) -> str:
        # claim から Lean 4 構文を生成
        # LLM アシストで変換
        
      def is_available() -> bool:
        # Lean 4 がインストールされているか確認
  }
```

### ProofCache

```ccl
/mek "ProofCache"
  [input: Code Hash + ProofType]
  [output: Cached ProofResult]
  {
    class ProofCache:
      db_path: Path = ~/.hermeneus/proof_cache.db
      default_ttl: int = 86400  # 24時間
      
      def get(code_hash: str, proof_type: ProofType) -> Optional[ProofResult]:
        # キャッシュから取得
        
      def put(code_hash: str, proof_type: ProofType, result: ProofResult):
        # キャッシュに保存
        
      def invalidate(code_hash: str):
        # キャッシュを無効化
        
      def clean_expired():
        # 期限切れエントリを削除
  }
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/prover.py` | [NEW] Prover Interface + 実装 |
| `src/__init__.py` | [MODIFY] v0.4.1 API 更新 |
| `tests/test_prover.py` | [NEW] Prover テスト |

---

## 依存関係

```bash
# 必須
pip install mypy  # 型チェック

# オプション (形式証明)
# Lean 4 インストール: https://leanprover.github.io/lean4/doc/setup.html
# curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
```

---

## 使用例 (目標)

```python
from hermeneus.src import verify_code, MypyProver, ProofType

# Python コードの型チェック
code = '''
def add(x: int, y: int) -> int:
    return x + y
'''

result = verify_code(code, prover=MypyProver())
print(f"Verified: {result.verified}")
print(f"Errors: {result.errors}")

# キャッシュ付き検証
result2 = verify_code(code, use_cache=True)
print(f"Cached: {result2.cached}")  # True (2回目)
```

---

## ユースケース CCL

### 1. CCL 出力の型安全性

```ccl
# 生成コードの型チェック
/ene+![type_check(strict=True)]

# 型エラーがあれば拒否
if errors:
  >> REJECT "型エラー: {errors}"
else:
  >> ACCEPT
```

### 2. Multi-Prover 検証

```ccl
# 複数の検証を組み合わせ
/verify+
  [provers: [mypy, schema, lean4?]]
  {
    type_result = mypy.verify(code)
    schema_result = schema.verify(output)
    
    if lean4.is_available():
      formal_result = lean4.verify(claim)
    
    >> aggregate(type_result, schema_result, formal_result?)
  }
```

### 3. 検証付き実行

```ccl
# 実行 + 検証 パイプライン
/noe+ >> V[] < 0.3
  ![verify(type=True, schema=True)]
  ![audit(record=True)]
```

---

## メトリクス

| 指標 | 目標値 |
|:-----|:-------|
| 型チェック実行時間 | <2秒 |
| キャッシュヒット率 | >80% |
| Lean4 証明成功率 | >70% (対応可能な主張) |

---

## リスク分析 CCL

```ccl
/pre "Phase 4b Risks"
  {
    R1: Lean4 依存性        -- オプション化、mypy は必須
    R2: 証明生成の複雑性    -- LLM アシストで簡略化
    R3: キャッシュ肥大      -- TTL + 手動クリーン
    R4: 型チェックの誤検出  -- strict モードをオプションに
  }
  >> リスク緩和策実装
```

---

## 次ステップ

```ccl
# Phase 4b 完了後 → Phase 5 (Production Ready)
/mek+ "Production Hardening"
  {
    API サーバー化
    CLI ツール整備
    ドキュメント整備
  }
  _/ene+
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 4b*
