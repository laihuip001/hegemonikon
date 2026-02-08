# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: Basin の使用ログを収集し、非等方性学習の基盤を作る
"""
Basin Logger — Attractor 使用ログ & 非等方性学習の雛形

問い C への回答:
  Basin の非等方性を手動設定するのは前提の棚卸しに反する。
  正しい方法: 使用ログからパターンを学習する。

ログ構造:
  - suggest() の推薦 (predicted)
  - Creator の実際の選択 (actual) — 後から記録
  - 推薦と選択の乖離 → basin bias として蓄積

将来: bias データから SeriesAttractor の threshold/margin を
Series ごとに調整 → 非等方的 basin の実現
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from mekhane.fep.attractor import OscillationType


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JST = timezone(timedelta(hours=9))
DEFAULT_LOG_DIR = Path.home() / "oikos" / "hegemonikon" / "mneme" / ".hegemonikon" / "attractor_logs"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
# PURPOSE: 1回の Attractor 推薦ログ
class AttractorLogEntry:
    """1回の Attractor 推薦ログ"""
    timestamp: str
    user_input: str
    predicted_series: list[str]       # suggest() の推薦
    top_similarity: float
    oscillation: str
    actual_series: Optional[str] = None   # Creator の実際の選択
    correction: bool = False               # 推薦 ≠ 実際の選択

    # PURPOSE: 予測ログをJSON永続化可能な形式に変換
    def to_dict(self) -> dict:
        return asdict(self)


# PURPOSE: 各 Series の basin bias (非等方性の種)
@dataclass
class BasinBias:
    """各 Series の basin bias (非等方性の種)"""
    series: str
    over_predict_count: int = 0    # この Series を推薦したが選ばれなかった回数
    under_predict_count: int = 0   # この Series が選ばれたが推薦しなかった回数
    correct_count: int = 0          # 正しく推薦した回数
    total_count: int = 0

    @property
    # PURPOSE: 推薦の精度: 推薦した中で実際に選ばれた割合
    def precision(self) -> float:
        """推薦の精度: 推薦した中で実際に選ばれた割合"""
        predicted = self.correct_count + self.over_predict_count
        return self.correct_count / predicted if predicted > 0 else 0.0

    @property
    # PURPOSE: 推薦の再現率: 実際に選ばれた中で推薦できた割合
    def recall(self) -> float:
        """推薦の再現率: 実際に選ばれた中で推薦できた割合"""
        actual = self.correct_count + self.under_predict_count
        return self.correct_count / actual if actual > 0 else 0.0

    @property
    # PURPOSE: Basin の歪み方向
    def bias_direction(self) -> str:
        """Basin の歪み方向"""
        if self.over_predict_count > self.under_predict_count * 1.5:
            return "too_wide"   # basin が広すぎる
        elif self.under_predict_count > self.over_predict_count * 1.5:
            return "too_narrow"  # basin が狭すぎる
        return "balanced"


# PURPOSE: Attractor の使用ログを収集し、Basin の非等方性を学習する雛形。
# ---------------------------------------------------------------------------
# BasinLogger
# ---------------------------------------------------------------------------

class BasinLogger:
    """
    Attractor の使用ログを収集し、Basin の非等方性を学習する雛形。

    Usage:
        logger = BasinLogger()

        # 推薦時にログ
        entry = logger.log_prediction(
            user_input="Why does this exist?",
            predicted_series=["O"],
            top_similarity=0.633,
            oscillation="clear",
        )

        # Creator が実際に選んだ Series を後から記録
        logger.log_correction(entry, actual_series="O")

        # Bias レポート
        report = logger.bias_report()
    """

    # PURPOSE: 予測vs実績の偏り蓄積とbiasチューニング提案
    def __init__(self, log_dir: Path | None = None):
        self.log_dir = log_dir or DEFAULT_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._entries: list[AttractorLogEntry] = []
        self._biases: dict[str, BasinBias] = {
            s: BasinBias(series=s) for s in ["O", "S", "H", "P", "K", "A"]
        }

    # PURPOSE: 推薦をログに記録
    def log_prediction(
        self,
        user_input: str,
        predicted_series: list[str],
        top_similarity: float,
        oscillation: str,
    ) -> AttractorLogEntry:
        """推薦をログに記録"""
        entry = AttractorLogEntry(
            timestamp=datetime.now(JST).isoformat(),
            user_input=user_input,
            predicted_series=predicted_series,
            top_similarity=top_similarity,
            oscillation=oscillation,
        )
        self._entries.append(entry)
        return entry

    # PURPOSE: Creator の実際の選択を記録し、bias を更新
    def log_correction(
        self,
        entry: AttractorLogEntry,
        actual_series: str,
    ) -> None:
        """Creator の実際の選択を記録し、bias を更新"""
        entry.actual_series = actual_series
        entry.correction = actual_series not in entry.predicted_series

        # Bias 更新
        for pred in entry.predicted_series:
            if pred == actual_series:
                self._biases[pred].correct_count += 1
            else:
                self._biases[pred].over_predict_count += 1
            self._biases[pred].total_count += 1

        if actual_series not in entry.predicted_series:
            self._biases[actual_series].under_predict_count += 1
            self._biases[actual_series].total_count += 1

    # PURPOSE: 全 Series の bias レポートを返す
    def bias_report(self) -> dict[str, dict]:
        """全 Series の bias レポートを返す"""
        report = {}
        for series, bias in self._biases.items():
            if bias.total_count > 0:
                report[series] = {
                    "precision": round(bias.precision, 3),
                    "recall": round(bias.recall, 3),
                    "direction": bias.bias_direction,
                    "total": bias.total_count,
                    "over": bias.over_predict_count,
                    "under": bias.under_predict_count,
                    "correct": bias.correct_count,
                }
        return report

    # PURPOSE: ログを JSONL ファイルに保存
    def save(self) -> Path:
        """ログを JSONL ファイルに保存"""
        today = datetime.now(JST).strftime("%Y%m%d")
        log_file = self.log_dir / f"attractor_log_{today}.jsonl"

        with open(log_file, "a", encoding="utf-8") as f:
            for entry in self._entries:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

        saved_count = len(self._entries)
        self._entries.clear()
        return log_file

    # PURPOSE: 過去のログから bias を再計算
    def load_biases(self, log_file: Path) -> None:
        """過去のログから bias を再計算"""
        if not log_file.exists():
            return

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line.strip())
                if data.get("actual_series"):
                    # bias を再構築
                    actual = data["actual_series"]
                    predicted = data["predicted_series"]
                    for pred in predicted:
                        if pred == actual:
                            self._biases[pred].correct_count += 1
                        else:
                            self._biases[pred].over_predict_count += 1
                        self._biases[pred].total_count += 1
                    if actual not in predicted:
                        self._biases[actual].under_predict_count += 1
                        self._biases[actual].total_count += 1

    @property
    # PURPOSE: Bias データから、各 Series の定義テキスト改善の方向性を提案する。
    def suggestions_for_tuning(self) -> dict[str, str]:
        """
        Bias データから、各 Series の定義テキスト改善の方向性を提案する。
        これが非等方性学習の最終出力。
        """
        suggestions = {}
        for series, bias in self._biases.items():
            if bias.total_count < 5:
                continue  # データ不足
            if bias.bias_direction == "too_wide":
                suggestions[series] = (
                    f"{series}: Basin が広すぎる (precision={bias.precision:.2f}). "
                    f"定義テキストをより具体的にすべき。"
                )
            elif bias.bias_direction == "too_narrow":
                suggestions[series] = (
                    f"{series}: Basin が狭すぎる (recall={bias.recall:.2f}). "
                    f"定義テキストに関連語彙を追加すべき。"
                )
        return suggestions
