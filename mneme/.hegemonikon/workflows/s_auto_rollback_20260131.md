# /s- 自動ロールバック機構設計

> **Date**: 2026-01-31
> **Mode**: /s- (最小計画)
> **Origin**: Recoverable Autonomy パターン (/noe+ 2026-01-31)

---

## STAGE 0: Scale Determination

```
📊 Scale 宣言: 🔭 Meso
   → 強制レベル: L2-std
   → 理由: 新規インフラ概念の導入
           Git + 状態管理の統合
```

---

## STAGE 1: Strategy Selection

```
⚖️ Explore/Exploit: Exploit (確実なパス)
📋 Plans: A (Conservative) — Git ベースの最小実装

📅 Y-1 評価:
  Fast:    ✅ 即座にロールバック可能
  Slow:    ✅ 6ヶ月でパターン蓄積
  Eternal: ✅ Git は標準、技術負債なし

🌊 D-1 評価:
  T+0:     rollback.py 作成、/ene 統合
  T+1:     Doxa がロールバック履歴を学習
  T+2:     自動判断精度向上
```

---

## STAGE 2: Success Criteria

| 軸 | Must | Should | Could |
|:---|:-----|:-------|:------|
| 機能 | Git ベースのロールバック | 状態スナップショット | DB ロールバック |
| 品質 | 既存 WF と整合 | ロールバック確認 | 差分表示 |
| 性能 | < 5秒 | — | — |

---

## STAGE 3: Blueprint

### アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                    Rollback Manager                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │ Git Layer   │   │ State Layer │   │ Doxa Layer  │       │
│  │             │   │             │   │             │       │
│  │ - commit    │   │ - snapshot  │   │ - record    │       │
│  │ - revert    │   │ - restore   │   │ - learn     │       │
│  │ - diff      │   │ - validate  │   │ - predict   │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│         │                 │                 │               │
│         └────────────────┼────────────────┘               │
│                          ↓                                  │
│                  ┌─────────────────┐                        │
│                  │ Recovery Engine │                        │
│                  │                 │                        │
│                  │ rollback()      │                        │
│                  │ validate()      │                        │
│                  │ snapshot()      │                        │
│                  └─────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 実装仕様

```python
# mekhane/fep/rollback.py (概念設計)

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import subprocess

@dataclass
class RollbackPoint:
    """ロールバックポイント"""
    id: str
    timestamp: str
    operation: str
    risk_level: str  # low/medium/high
    git_commit: Optional[str]
    state_snapshot: Optional[dict]
    
@dataclass
class RollbackResult:
    """ロールバック結果"""
    success: bool
    reverted_files: List[Path]
    error: Optional[str]

class RollbackManager:
    """自動ロールバック機構"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.history: List[RollbackPoint] = []
    
    def create_checkpoint(self, operation: str, risk_level: str) -> RollbackPoint:
        """操作前にチェックポイントを作成"""
        # 1. Git の現在状態を記録
        git_commit = self._get_current_commit()
        
        # 2. 状態スナップショット（高リスクのみ）
        state = None
        if risk_level == "high":
            state = self._capture_state()
        
        point = RollbackPoint(
            id=self._generate_id(),
            timestamp=self._now(),
            operation=operation,
            risk_level=risk_level,
            git_commit=git_commit,
            state_snapshot=state,
        )
        self.history.append(point)
        return point
    
    def rollback(self, point_id: str) -> RollbackResult:
        """指定ポイントまでロールバック"""
        point = self._find_point(point_id)
        if not point:
            return RollbackResult(False, [], "Point not found")
        
        # Git ベースのロールバック
        try:
            reverted = self._git_rollback(point.git_commit)
            
            # 状態復元（スナップショットがある場合）
            if point.state_snapshot:
                self._restore_state(point.state_snapshot)
            
            return RollbackResult(True, reverted, None)
        except Exception as e:
            return RollbackResult(False, [], str(e))
    
    def rollback_last(self) -> RollbackResult:
        """直前の操作をロールバック"""
        if not self.history:
            return RollbackResult(False, [], "No history")
        return self.rollback(self.history[-1].id)
    
    # Private methods
    def _get_current_commit(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def _git_rollback(self, commit: str) -> List[Path]:
        """Git でロールバック"""
        # 変更されたファイルを取得
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", commit, "HEAD"],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        files = [Path(f) for f in diff_result.stdout.strip().split('\n') if f]
        
        # ロールバック実行
        subprocess.run(
            ["git", "checkout", commit, "--", "."],
            cwd=self.workspace,
            check=True
        )
        
        return files
```

### ワークフロー統合

```markdown
## /ene (O4 Energeia) への統合

[BEFORE ACTION] チェックポイント作成
  - RollbackManager.create_checkpoint() を呼び出し
  - リスクレベルに応じたスナップショット深度

[AFTER ACTION] 結果検証
  - 成功 → チェックポイントを確定
  - 失敗 → 自動ロールバックを提案

[ON ERROR] 自動リカバリ
  - 🟢 低: ログのみ
  - 🟡 中: ロールバック提案 (y/n)
  - 🔴 高: 自動ロールバック + 通知
```

### CCL 拡張

```text
# ロールバック関連演算子（提案）
/ene!{rollback=auto}  → 失敗時自動ロールバック
/ene{checkpoint}      → 明示的にチェックポイント作成
/rollback             → 直前操作のロールバック
/rollback@{id}        → 特定ポイントへのロールバック
```

---

## STAGE 4: Devil's Advocate

| 視点 | 質問 | 回答 |
|:-----|:-----|:-----|
| Feasibility | Git だけで十分？ | 80%のケースをカバー、残りは手動 |
| Necessity | エラー時に手動復旧で十分？ | 自動化により復旧時間を短縮 |
| Alternatives | DB トランザクション？ | Git 優先、DB は Phase 2 |
| Risks | 誤ってロールバック？ | 確認ステップを必須化 |

---

## STAGE 5: SE振り返り

```
🔄 KPT
  Keep:    Git ベースの最小実装で開始
  Problem: 状態スナップショットの範囲が未定義
  Try:     P1 で Git のみ、P2 で状態拡張

⏱️ 時間検証
  所要時間: 6分 / 45分 (13%)
```

---

## 実装計画

| Phase | 内容 | 成果物 |
|:------|:-----|:-------|
| P1 | rollback.py 基本実装 | Git ベースのロールバック |
| P2 | 状態スナップショット | 拡張ロールバック |
| P3 | /ene 統合 | ワークフロー更新 |
| P4 | Doxa 学習 | 自動判断改善 |

---

*Generated by /s- v5.6 — 2026-01-31*
