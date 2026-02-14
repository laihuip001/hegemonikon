#!/usr/bin/env python3
# PROOF: [L2/コア] <- mekhane/exagoge/
# PURPOSE: データエクスポートの基底クラスとファイル形式変換機能
"""
Exagoge Extractor — エクスポート基盤モジュール

Hegemonikón の内部データ (Handoff, Doxa, KI, Ideas) を
外部フォーマットに変換するための基底クラスとユーティリティ。
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# PURPOSE: エクスポート結果を表現するデータクラス
@dataclass
class ExportResult:
    """エクスポート操作の結果。"""
    success: bool
    output_path: Path | None = None
    record_count: int = 0
    format: str = "json"
    errors: list[str] = field(default_factory=list)
    exported_at: str = field(default_factory=lambda: datetime.now().isoformat())


# PURPOSE: エクスポーターの共通インターフェースを定義する抽象基底クラス
class BaseExporter(ABC):
    """エクスポーターの基底クラス。

    各データソース (Handoff, Doxa, KI) ごとにサブクラスを実装する。
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def extract(self, **kwargs: Any) -> list[dict[str, Any]]:
        """データソースからレコードを抽出する。"""
        ...

    @abstractmethod
    def transform(self, records: list[dict[str, Any]], **kwargs: Any) -> Any:
        """抽出したレコードを出力形式に変換する。"""
        ...

    # PURPOSE: 抽出 → 変換 → 保存の ETL パイプラインを実行する
    def export(self, format: str = "json", **kwargs: Any) -> ExportResult:
        """ETL パイプラインを実行する。

        1. extract() でデータを抽出
        2. transform() で変換
        3. ファイルに保存

        Args:
            format: 出力形式 ("json", "yaml", "csv")
            **kwargs: サブクラス固有のオプション

        Returns:
            ExportResult: エクスポート結果
        """
        errors: list[str] = []

        try:
            records = self.extract(**kwargs)
        except Exception as e:
            return ExportResult(
                success=False,
                errors=[f"Extract failed: {e}"],
            )

        try:
            transformed = self.transform(records, format=format, **kwargs)
        except Exception as e:
            return ExportResult(
                success=False,
                record_count=len(records),
                errors=[f"Transform failed: {e}"],
            )

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{self.__class__.__name__}_{timestamp}.{format}"
        output_path = self.output_dir / filename

        try:
            if format == "json":
                output_path.write_text(
                    json.dumps(transformed, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            else:
                output_path.write_text(str(transformed), encoding="utf-8")
        except Exception as e:
            errors.append(f"Save failed: {e}")
            return ExportResult(
                success=False,
                record_count=len(records),
                format=format,
                errors=errors,
            )

        return ExportResult(
            success=True,
            output_path=output_path,
            record_count=len(records),
            format=format,
        )


# PURPOSE: Handoff データをエクスポートするクラス
class HandoffExporter(BaseExporter):
    """Handoff セッションログのエクスポーター。"""

    def __init__(self, sessions_dir: Path, output_dir: Path):
        super().__init__(output_dir)
        self.sessions_dir = sessions_dir

    # PURPOSE: Handoff ファイルから構造化データを抽出する
    def extract(self, count: int = 10, **kwargs: Any) -> list[dict[str, Any]]:
        """最新の Handoff ファイルからメタデータを抽出する。"""
        if not self.sessions_dir.exists():
            return []

        handoffs = sorted(
            self.sessions_dir.glob("handoff_*.md"),
            reverse=True,
        )[:count]

        records = []
        for hf in handoffs:
            content = hf.read_text(encoding="utf-8")
            records.append({
                "filename": hf.name,
                "date": hf.stem.replace("handoff_", ""),
                "size_bytes": hf.stat().st_size,
                "line_count": len(content.split("\n")),
                "preview": content[:200],
            })
        return records

    # PURPOSE: Handoff レコードを指定形式に変換する
    def transform(self, records: list[dict[str, Any]], **kwargs: Any) -> Any:
        """レコードリストを出力形式に変換する。"""
        return {
            "source": "hegemonikon_handoffs",
            "exported_at": datetime.now().isoformat(),
            "count": len(records),
            "records": records,
        }
