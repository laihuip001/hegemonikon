# PROOF: [L1/FEP] <- mekhane/fep/
# PURPOSE: Credit Assignment — Creator フィードバックで A行列を教師付き学習する
"""
Credit Assignment: Creator → FEP Agent Teacher Signal

Creator の accept/reject フィードバックを A行列の Dirichlet 学習に接続し、
自己正当化ループを破る教師信号を提供する。

Architecture:
    Creator feedback → FeedbackRecord → JSONL → update_A_with_feedback()
                                                ↓
                                      A行列変化 → fep_attractor_bridge → Attractor bias

Design decisions (/dia+ review 2026-02-08):
    F1: Positive-only Dirichlet (suppress は implicit competition)
    F2: step() 時の beliefs スナップショットを保存・使用
    F3: Standalone API (e2e_loop は変更しない)
    F4: JSONL (YAML はスケールしない)
    F5: bridge_update_needed 通知

Scalability:
    - JSONL append: O(1) per write
    - Monthly rotation: credit_log_YYYY-MM.jsonl
    - Load: streaming parse, constant memory
    - Learning rate decay: prevents saturation over many feedbacks
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import numpy as np

if TYPE_CHECKING:
    from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2

# Series name → A行列 topic row index (rows 8-13)
_SERIES_TO_TOPIC_ROW = {"O": 8, "S": 9, "H": 10, "P": 11, "K": 12, "A": 13}
_VALID_SERIES = set(_SERIES_TO_TOPIC_ROW.keys())

# Default storage directory
_DEFAULT_LOG_DIR = Path.home() / "oikos/mneme/.hegemonikon/feedback"


# ─────────────────────────────────────────────────────────────────────
# Data Model
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: の統一的インターフェースを実現する
@dataclass
class FeedbackRecord:
    """Creator の1回のフィードバックを表現する。

    Attributes:
        timestamp: ISO 8601 timestamp
        user_input: 元の入力テキスト
        recommended_series: Attractor/FEP が推薦した Series
        action_name: FEP agent の選択 (act_O..act_A, observe)
        accepted: Creator が accept したか
        correct_series: reject 時に Creator が指定した正解 Series (なければ None)
        observation: フィードバック時の flat obs index
        confidence: 推薦時の確信度 (1 - entropy/4)
        beliefs_snapshot: step() 時の beliefs 配列 (Dirichlet 更新用)
    """
    timestamp: str
    user_input: str
    recommended_series: str
    action_name: str
    accepted: bool
    correct_series: Optional[str] = None
    observation: int = 0
    confidence: float = 0.5
    beliefs_snapshot: Optional[list[float]] = None

    def __post_init__(self):
        if self.recommended_series not in _VALID_SERIES:
            raise ValueError(
                f"Invalid recommended_series: {self.recommended_series}. "
                f"Must be one of {_VALID_SERIES}"
            )
        if self.correct_series is not None and self.correct_series not in _VALID_SERIES:
            raise ValueError(
                f"Invalid correct_series: {self.correct_series}. "
                f"Must be one of {_VALID_SERIES}"
            )

    # PURPOSE: credit_assignment の effective series 処理を実行する
    @property
    def effective_series(self) -> str:
        """学習対象の Series: accept→推薦, reject+修正→正解, reject のみ→推薦."""
        if self.accepted:
            return self.recommended_series
        return self.correct_series or self.recommended_series


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class FeedbackResult:
    """apply_feedback_to_agent() の結果。"""
    records_applied: int
    accept_count: int
    reject_count: int
    series_updated: dict[str, int] = field(default_factory=dict)
    bridge_update_needed: bool = False
    a_matrix_delta_norm: float = 0.0


# ─────────────────────────────────────────────────────────────────────
# JSONL Persistence
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: JSONL ファイルにフィードバックを append (O(1))
def record_feedback(
    record: FeedbackRecord,
    log_dir: Optional[Path] = None,
) -> Path:
    """フィードバックを JSONL ファイルに追記する。

    月次ローテーション: credit_log_2026-02.jsonl

    Returns:
        書き込んだファイルのパス
    """
    log_dir = log_dir or _DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    # Monthly rotation
    month_str = datetime.now().strftime("%Y-%m")
    log_file = log_dir / f"credit_log_{month_str}.jsonl"

    # Serialize (beliefs_snapshot を丸めて保存容量を抑える)
    data = asdict(record)
    if data.get("beliefs_snapshot"):
        data["beliefs_snapshot"] = [round(v, 6) for v in data["beliefs_snapshot"]]

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    return log_file


# PURPOSE: JSONL からフィードバック履歴をロード
def load_feedback_history(
    log_dir: Optional[Path] = None,
    months: int = 3,
) -> list[FeedbackRecord]:
    """直近 N ヶ月分のフィードバック履歴をロードする。

    Args:
        log_dir: ログディレクトリ (省略時: デフォルト)
        months: 何ヶ月分を読むか (デフォルト: 3)

    Returns:
        FeedbackRecord のリスト (古い順)
    """
    log_dir = log_dir or _DEFAULT_LOG_DIR
    if not log_dir.exists():
        return []

    records: list[FeedbackRecord] = []
    for log_file in sorted(log_dir.glob("credit_log_*.jsonl"))[-months:]:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    records.append(FeedbackRecord(**data))
                except (json.JSONDecodeError, TypeError):
                    continue  # Corrupted line, skip

    return records


# ─────────────────────────────────────────────────────────────────────
# A行列 教師付き学習
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Creator フィードバック → A行列 Dirichlet 更新
def apply_feedback_to_agent(
    agent: "HegemonikónFEPAgentV2",
    records: list[FeedbackRecord],
    base_learning_rate: float = 30.0,
    decay_factor: float = 0.995,
) -> FeedbackResult:
    """フィードバック記録群を A行列に適用する。

    /dia+ F1: Positive-only Dirichlet (suppress なし, implicit competition)
    /dia+ F2: beliefs_snapshot を使用 (なければ均一 beliefs にフォールバック)

    Learning rate decay:
        η_i = base_lr × decay^i
        100 records: η₁₀₀ = 30 × 0.995^100 ≈ 18.2 (39% decay)
        1000 records: η₁₀₀₀ = 30 × 0.995^1000 ≈ 2.0 (93% decay)
        → 初期は強く学習、蓄積するほど保守的に

    Args:
        agent: FEP Agent v2
        records: 適用するフィードバック記録群
        base_learning_rate: 初期学習率
        decay_factor: 学習率減衰係数 (per record)

    Returns:
        FeedbackResult (適用件数、bridge 更新要否など)
    """
    if not records:
        return FeedbackResult(
            records_applied=0, accept_count=0, reject_count=0,
        )

    A_before = agent._get_A_matrix().copy()
    accept_count = 0
    reject_count = 0
    series_updated: dict[str, int] = {}

    for i, record in enumerate(records):
        # Learning rate decay
        eta = base_learning_rate * (decay_factor ** i)
        if eta < 1.0:
            break  # Too small to matter — stop early

        target_series = record.effective_series
        topic_row = _SERIES_TO_TOPIC_ROW[target_series]

        # Construct observation vector: 1-hot at correct topic row
        A = agent._get_A_matrix()
        num_obs = A.shape[0]
        obs_vector = np.zeros(num_obs)
        obs_vector[topic_row] = 1.0

        # Beliefs: use snapshot if available, else uniform fallback
        if record.beliefs_snapshot:
            beliefs = np.array(record.beliefs_snapshot, dtype=np.float64)
            beliefs = beliefs / (beliefs.sum() + 1e-10)  # renormalize
        else:
            beliefs = np.ones(A.shape[1]) / A.shape[1]

        # Positive-only Dirichlet update (/dia+ F1)
        if record.accepted:
            # Accept: reinforce the recommended series
            update = eta * np.outer(obs_vector, beliefs)
            accept_count += 1
        else:
            if record.correct_series:
                # Reject + correction: learn the CORRECT series (stronger signal)
                update = eta * 1.5 * np.outer(obs_vector, beliefs)
                reject_count += 1
            else:
                # Reject without correction: weak positive for all OTHER series
                # This is implicit competition — don't learn the wrong one
                continue

        eps = 1e-10
        A = np.clip(A + update, eps, None)
        A = A / A.sum(axis=0, keepdims=True)
        agent._set_A_matrix(A)

        series_updated[target_series] = series_updated.get(target_series, 0) + 1

    # Compute delta norm
    A_after = agent._get_A_matrix()
    delta_norm = float(np.linalg.norm(A_after - A_before))

    return FeedbackResult(
        records_applied=accept_count + reject_count,
        accept_count=accept_count,
        reject_count=reject_count,
        series_updated=series_updated,
        bridge_update_needed=delta_norm > 1e-6,
        a_matrix_delta_norm=delta_norm,
    )


# ─────────────────────────────────────────────────────────────────────
# 統計・診断
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: フィードバック履歴の統計サマリー
def feedback_summary(
    records: list[FeedbackRecord],
) -> dict[str, Any]:
    """フィードバック履歴の統計を返す。

    Returns:
        {
            "total": int,
            "accept_rate": float,
            "per_series": {series: {"accept": n, "reject": n}},
            "common_corrections": [(from, to, count)],
        }
    """
    if not records:
        return {"total": 0, "accept_rate": 0.0, "per_series": {}, "common_corrections": []}

    total = len(records)
    accepts = sum(1 for r in records if r.accepted)
    accept_rate = accepts / total

    per_series: dict[str, dict[str, int]] = {}
    corrections: dict[tuple[str, str], int] = {}

    for r in records:
        series = r.recommended_series
        if series not in per_series:
            per_series[series] = {"accept": 0, "reject": 0}

        if r.accepted:
            per_series[series]["accept"] += 1
        else:
            per_series[series]["reject"] += 1
            if r.correct_series:
                key = (r.recommended_series, r.correct_series)
                corrections[key] = corrections.get(key, 0) + 1

    common_corrections = sorted(
        [(f, t, c) for (f, t), c in corrections.items()],
        key=lambda x: -x[2],
    )[:5]

    return {
        "total": total,
        "accept_rate": round(accept_rate, 3),
        "per_series": per_series,
        "common_corrections": common_corrections,
    }


# ─────────────────────────────────────────────────────────────────────
# ヘルパー: step() 結果からフィードバック用スナップショットを生成
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: step() 結果を FeedbackRecord に必要なスナップショットに変換
def snapshot_for_feedback(
    user_input: str,
    step_result: dict[str, Any],
    attractor_series: Optional[str] = None,
) -> dict[str, Any]:
    """step() 結果から FeedbackRecord 作成に必要なスナップショットを返す。

    呼び出し側は後で Creator の feedback を受けてから
    FeedbackRecord(accepted=..., correct_series=..., **snapshot) で記録する。

    Args:
        user_input: ユーザー入力テキスト
        step_result: agent.step() の戻り値
        attractor_series: Attractor 推薦 Series (FEP 選択と異なる場合)

    Returns:
        dict suitable for FeedbackRecord(**dict, accepted=..., correct_series=...)
    """
    selected = step_result.get("selected_series") or attractor_series or "O"
    beliefs = step_result.get("beliefs")
    beliefs_list = beliefs.tolist() if hasattr(beliefs, "tolist") else list(beliefs) if beliefs is not None else None

    return {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input[:500],  # Truncate to prevent JSONL bloat
        "recommended_series": selected,
        "action_name": step_result.get("action_name", "unknown"),
        "observation": 0,  # Will be set by caller if available
        "confidence": round(1.0 - min(step_result.get("entropy", 2.0) / 4.0, 1.0), 3),
        "beliefs_snapshot": beliefs_list,
    }
