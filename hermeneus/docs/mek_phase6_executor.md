# [CCL]/mek+ Hermēneus Phase 6 — Workflow Executor + Synergeia 統合

---
sel:
  workflow: /mek+
  scope: P6=workflow_executor+synergeia
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - 実ワークフロー (/noe+, /ene+ 等) 実行
    - Synergeia API 統合
    - E2E テスト
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 6"
  [target: Workflow Executor + Synergeia]
  {
    /s1 "Workflow Registry"   -- ワークフロー定義ロード
    /s2 "Executor Engine"     -- 実行エンジン
    /s3 "Synergeia Adapter"   -- Synergeia 統合
    /s4 "E2E Pipeline"        -- 完全パイプライン
  }
  >> Real CCL Execution ✅
```

---

## Phase 6 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | 実際の CCL ワークフローを Hermēneus 経由で実行 |
| **成果物** | `executor.py`, `registry.py`, `synergeia_adapter.py` |
| **依存** | Synergeia API, ワークフロー定義 (.agent/workflows/) |
| **検証** | E2E テスト (compile → execute → verify → audit) |

---

## アーキテクチャ

```
                    ┌─────────────────────────────────────────┐
                    │          Synergeia Coordinator          │
                    └────────────────┬────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────────┐
                    │         Hermēneus Executor              │
                    │  ┌─────────────────────────────────┐    │
                    │  │     Workflow Registry           │    │
                    │  │  (/noe+, /bou+, /ene+ 定義)     │    │
                    │  └───────────────┬─────────────────┘    │
                    │                  │                      │
                    │  ┌───────────────▼─────────────────┐    │
                    │  │      Executor Engine            │    │
                    │  │  (compile → execute → verify)   │    │
                    │  └───────────────┬─────────────────┘    │
                    │                  │                      │
                    │  ┌───────────────▼─────────────────┐    │
                    │  │       LLM Backends              │    │
                    │  │  (Claude, GPT-4, Gemini)        │    │
                    │  └─────────────────────────────────┘    │
                    └─────────────────────────────────────────┘
```

---

## 実装タスク CCL

```ccl
# Phase 6 タスクリスト
let phase_6_tasks = [
  /s1+ "Workflow Registry" {
    WorkflowDefinition データクラス
    ワークフロー YAML/MD パーサー
    .agent/workflows/ からのロード
    キャッシュ機構
  }
  
  /s2+ "Executor Engine" {
    WorkflowExecutor クラス
    execute(ccl, context) メソッド
    verify + audit 統合
    結果の構造化
  }
  
  /s3+ "Synergeia Adapter" {
    SynergeiaAdapter クラス
    スレッド設定との統合
    非同期実行サポート
    結果のマージ
  }
  
  /s4+ "E2E Pipeline" {
    完全パイプラインテスト
    /noe+ → LMQL → 実行 → 検証 → 監査
    メトリクス収集
  }
]

F:[phase_6_tasks]{/ene+} >> 全タスク完了
```

---

## コンポーネント設計

### WorkflowRegistry

```ccl
/mek "WorkflowRegistry"
  [input: Workflow Path]
  [output: WorkflowDefinition]
  {
    @dataclass
    class WorkflowDefinition:
      name: str           # ワークフロー名 (例: "noe", "bou")
      ccl: str            # CCL シグネチャ
      description: str    # 説明
      stages: List[str]   # ステージ
      output_format: str  # 出力形式
      
    class WorkflowRegistry:
      def __init__(workflows_dir: Path):
        self.workflows_dir = workflows_dir
        self._cache: Dict[str, WorkflowDefinition] = {}
        
      def get(name: str) -> Optional[WorkflowDefinition]:
        # キャッシュチェック → ファイルロード → パース
        
      def load_all() -> Dict[str, WorkflowDefinition]:
        # 全ワークフローをロード
        
      def _parse_workflow_file(path: Path) -> WorkflowDefinition:
        # YAML frontmatter + Markdown をパース
  }
```

### WorkflowExecutor

```ccl
/mek "WorkflowExecutor"
  [input: CCL + Context]
  [output: ExecutionResult]
  {
    class WorkflowExecutor:
      def __init__(
        registry: WorkflowRegistry,
        model: str = "openai/gpt-4o"
      ):
        self.registry = registry
        self.model = model
        
      async def execute(
        ccl: str,
        context: str,
        verify: bool = True,
        audit: bool = True
      ) -> ExecutionPipeline:
        # 1. CCL パース
        # 2. ワークフロー定義ロード
        # 3. LMQL 生成
        # 4. LLM 実行
        # 5. 検証 (オプション)
        # 6. 監査記録 (オプション)
        
      def _resolve_workflow(name: str) -> WorkflowDefinition:
        # レジストリからワークフロー取得
  }
```

### SynergeiaAdapter

```ccl
/mek "SynergeiaAdapter"
  [input: Thread Config]
  [output: Execution Result]
  {
    class SynergeiaAdapter:
      def __init__(executor: WorkflowExecutor):
        self.executor = executor
        
      async def execute_thread(
        thread_config: Dict[str, Any]
      ) -> ThreadResult:
        # Synergeia スレッド設定を Hermēneus 実行に変換
        
      async def execute_parallel(
        threads: List[Dict]
      ) -> List[ThreadResult]:
        # 並列実行
        
      def to_synergeia_format(result: ExecutionResult) -> Dict:
        # 結果を Synergeia 形式に変換
  }
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/registry.py` | [NEW] Workflow Registry |
| `src/executor.py` | [NEW] Workflow Executor |
| `src/synergeia_adapter.py` | [NEW] Synergeia 統合 |
| `src/__init__.py` | [MODIFY] v0.6.0 API 更新 |
| `tests/test_executor.py` | [NEW] E2E テスト |

---

## 使用例 (目標)

```python
from hermeneus.src import WorkflowExecutor, WorkflowRegistry

# レジストリ初期化
registry = WorkflowRegistry(Path(".agent/workflows"))

# エグゼキューター作成
executor = WorkflowExecutor(registry)

# CCL 実行
result = await executor.execute(
    ccl="/noe+",
    context="プロジェクト分析",
    verify=True,
    audit=True
)

print(result.output)
print(f"Verified: {result.verification.accepted}")
print(f"Audit ID: {result.audit_id}")
```

### Synergeia 統合

```python
from hermeneus.src import SynergeiaAdapter

adapter = SynergeiaAdapter(executor)

# Synergeia スレッド設定
thread_config = {
    "name": "deep_analysis",
    "ccl": "/noe+ >> /dia+ >> /gno+",
    "context": "分析対象",
    "model": "claude-3-sonnet"
}

result = await adapter.execute_thread(thread_config)
```

---

## ワークフロー定義例

既存の `.agent/workflows/noe.md` から:

```yaml
---
description: Noēsis (深い認識) を発動
---

# /noe

## STAGE 0: 初期化
...

## STAGE 1: 多角的分析
...
```

これを `WorkflowDefinition` に変換:

```python
WorkflowDefinition(
    name="noe",
    ccl="/noe+",
    description="Noēsis (深い認識) を発動",
    stages=["初期化", "多角的分析", "統合"],
    output_format="markdown"
)
```

---

## 依存関係

```bash
# 既存依存のみ (新規追加なし)
pip install aiohttp  # 非同期 HTTP (Synergeia 連携)
```

---

## リスク分析 CCL

```ccl
/pre "Phase 6 Risks"
  {
    R1: ワークフロー解釈の曖昧さ    -- 構造化されたフロントマター必須
    R2: LLM 応答の不確実性         -- 検証レイヤーで保証
    R3: Synergeia API 変更        -- アダプターで抽象化
    R4: パフォーマンス             -- キャッシュ + 並列実行
  }
  >> リスク緩和策実装
```

---

## メトリクス

| 指標 | 目標値 |
|:-----|:-------|
| ワークフロー実行成功率 | >95% |
| 平均実行時間 | <5秒 (単一WF) |
| 検証カバレッジ | 100% |

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 6*
