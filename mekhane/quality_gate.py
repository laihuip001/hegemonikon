# PROOF: [L2/インフラ] <- mekhane/ A0→品質管理が必要→quality_gate が担う
"""
Quality Gate Module - Hegemonikón品質体系

Metrika (5門) + Chreos (技術負債) + Palimpsest (コード考古学) の自動検証。

Usage:
    from mekhane.quality_gate import QualityGate

    gate = QualityGate()
    result = gate.check_file("path/to/file.py")
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
# PURPOSE: Metrika 5門の検証結果
class MetrikaResult:
    """Metrika 5門の検証結果"""

    dokime: bool = True  # テスト先行
    syntomia: bool = True  # 複雑度制限
    prosbasimotes: bool = True  # アクセシビリティ
    atomos: bool = True  # 単一責任
    katharos: bool = True  # 死コードなし

    violations: list[str] = field(default_factory=list)

    @property
    # PURPOSE: passed — システムの処理
    def passed(self) -> bool:
        """passed — システムの処理"""
        return all(
            [self.dokime, self.syntomia, self.prosbasimotes, self.atomos, self.katharos]
        )


# PURPOSE: 技術負債項目
@dataclass
class ChreosItem:
    """技術負債項目"""

    owner: str
    deadline: datetime
    description: str
    line_number: int
    status: str  # "healthy", "warning", "rotten"


# PURPOSE: コード考古学発見物
@dataclass
class PalimpsestItem:
    """コード考古学発見物"""

    pattern: str  # "HACK", "FIXME", "magic_number"
    line_number: int
    content: str
    hypothesis: str


# PURPOSE: 品質門 - Hegemonikón品質体系の実装
class QualityGate:
    """品質門 - Hegemonikón品質体系の実装"""

    # Metrika 閾値
    MAX_NESTING = 3
    MAX_FUNCTION_LINES = 30
    MAX_ARGS = 4
    MAX_COMPONENT_LINES = 120

    # Chreos パターン
    CHREOS_PATTERN = re.compile(
        r"#\s*TODO\(([^,]+),\s*(\d{4}-\d{2}-\d{2})\):\s*(.+)", re.IGNORECASE
    )
    INVALID_TODO = re.compile(r"#\s*TODO[:\s]", re.IGNORECASE)

    # Palimpsest パターン
    LEGACY_PATTERNS = {
        "HACK": re.compile(r"#.*\bHACK\b", re.IGNORECASE),
        "FIXME": re.compile(r"#.*\bFIXME\b", re.IGNORECASE),
        "XXX": re.compile(r"#.*\bXXX\b", re.IGNORECASE),
        "WORKAROUND": re.compile(r"#.*\bWORKAROUND\b", re.IGNORECASE),
    }
    MAGIC_NUMBER = re.compile(r"(?<![a-zA-Z_])\d{3,}(?![a-zA-Z_])")

    # PURPOSE: ファイルの品質を検証
    def check_file(self, file_path: str) -> dict:
        """ファイルの品質を検証"""
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        return {
            "file": str(path),
            "metrika": self.check_metrika(lines),
            "chreos": self.check_chreos(lines),
            "palimpsest": self.check_palimpsest(lines),
        }

    # PURPOSE: Metrika 5門の検証
    def check_metrika(self, lines: list[str]) -> MetrikaResult:
        """Metrika 5門の検証"""
        result = MetrikaResult()

        # Syntomia: 複雑度制限
        max_nesting = self._measure_nesting(lines)
        if max_nesting > self.MAX_NESTING:
            result.syntomia = False
            result.violations.append(
                f"📉 Syntomia: ネスト深度 {max_nesting} > {self.MAX_NESTING}"
            )

        # Atomos: 行数制限
        if len(lines) > self.MAX_COMPONENT_LINES:
            result.atomos = False
            result.violations.append(
                f"⚛️ Atomos: {len(lines)}行 > {self.MAX_COMPONENT_LINES}行"
            )

        # Katharos: コメントアウトコード検出
        commented_code = self._detect_commented_code(lines)
        if commented_code:
            result.katharos = False
            result.violations.append(
                f"💀 Katharos: コメントアウトコード {len(commented_code)}箇所"
            )

        return result

    # PURPOSE: Chreos: 技術負債検出
    def check_chreos(self, lines: list[str]) -> list[ChreosItem]:
        """Chreos: 技術負債検出"""
        items = []
        today = datetime.now()
        warning_threshold = timedelta(days=7)

        for i, line in enumerate(lines, 1):
            # 正しい形式のTODO
            match = self.CHREOS_PATTERN.search(line)
            if match:
                owner, date_str, desc = match.groups()
                deadline = datetime.strptime(date_str, "%Y-%m-%d")

                if deadline < today:
                    status = "rotten"
                elif deadline - today < warning_threshold:
                    status = "warning"
                else:
                    status = "healthy"

                items.append(
                    ChreosItem(
                        owner=owner,
                        deadline=deadline,
                        description=desc,
                        line_number=i,
                        status=status,
                    )
                )

            # 不正形式のTODO (期限・担当者なし)
            elif self.INVALID_TODO.search(line) and not match:
                items.append(
                    ChreosItem(
                        owner="unknown",
                        deadline=today,
                        description="不正形式TODO",
                        line_number=i,
                        status="rotten",
                    )
                )

        return items

    # PURPOSE: Palimpsest: コード考古学
    def check_palimpsest(self, lines: list[str]) -> list[PalimpsestItem]:
        """Palimpsest: コード考古学"""
        items = []

        for i, line in enumerate(lines, 1):
            # レガシーパターン検出
            for name, pattern in self.LEGACY_PATTERNS.items():
                if pattern.search(line):
                    items.append(
                        PalimpsestItem(
                            pattern=name,
                            line_number=i,
                            content=line.strip(),
                            hypothesis=self._generate_hypothesis(name),
                        )
                    )

            # マジックナンバー検出 (コメント外)
            if not line.strip().startswith("#"):
                if self.MAGIC_NUMBER.search(line):
                    items.append(
                        PalimpsestItem(
                            pattern="magic_number",
                            line_number=i,
                            content=line.strip()[:50],
                            hypothesis="過去の修正で追加された可能性",
                        )
                    )

        return items

    # PURPOSE: ネスト深度を測定
    def _measure_nesting(self, lines: list[str]) -> int:
        """ネスト深度を測定"""
        max_depth = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                depth = indent // 4  # 4スペース = 1ネスト
                max_depth = max(max_depth, depth)
        return max_depth

    # PURPOSE: コメントアウトされたコード行を検出
    def _detect_commented_code(self, lines: list[str]) -> list[int]:
        """コメントアウトされたコード行を検出"""
        code_patterns = [
            r"#\s*(def |class |import |from |return |if |for |while )",
            r"#\s*\w+\s*=\s*",
            r"#\s*\w+\.\w+\(",
        ]

        commented = []
        for i, line in enumerate(lines, 1):
            for pattern in code_patterns:
                if re.search(pattern, line):
                    commented.append(i)
                    break
        return commented

    # PURPOSE: 考古学的仮説を生成
    def _generate_hypothesis(self, pattern: str) -> str:
        """考古学的仮説を生成"""
        hypotheses = {
            "HACK": "一時的回避策として追加。本来の解決策が見つかるまで保持",
            "FIXME": "既知の問題。修正が必要だが条件が揃っていない",
            "XXX": "注意が必要な箇所。レビュー時に確認すべき",
            "WORKAROUND": "根本解決ではない回避策。上流の修正待ち",
        }
        return hypotheses.get(pattern, "不明 — git log で調査が必要")

    # PURPOSE: 検証結果をフォーマット
    def format_report(self, result: dict) -> str:
        """検証結果をフォーマット"""
        lines = [
            f"📋 品質門レポート: {result['file']}",
            "=" * 50,
            "",
        ]

        # Metrika
        metrika = result["metrika"]
        status = "✅ PASS" if metrika.passed else "❌ FAIL"
        lines.append(f"📏 Metrika: {status}")
        for v in metrika.violations:
            lines.append(f"   {v}")
        lines.append("")

        # Chreos
        chreos = result["chreos"]
        rotten = [c for c in chreos if c.status == "rotten"]
        warning = [c for c in chreos if c.status == "warning"]
        lines.append(
            f"⏰ Chreos: {len(chreos)}件 (腐敗: {len(rotten)}, 警告: {len(warning)})"
        )
        for c in rotten:
            lines.append(f"   🔴 L{c.line_number}: {c.description}")
        for c in warning:
            lines.append(f"   ⚠️ L{c.line_number}: {c.description}")
        lines.append("")

        # Palimpsest
        palimpsest = result["palimpsest"]
        lines.append(f"📜 Palimpsest: {len(palimpsest)}件")
        for p in palimpsest[:5]:  # 最大5件表示
            lines.append(f"   📍 L{p.line_number} [{p.pattern}]: {p.hypothesis}")
        if len(palimpsest) > 5:
            lines.append(f"   ... 他 {len(palimpsest) - 5}件")

        return "\n".join(lines)


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python quality_gate.py <file_path>")
        sys.exit(1)

    gate = QualityGate()
    result = gate.check_file(sys.argv[1])

    if "error" in result:
        print(result["error"])
        sys.exit(1)

    print(gate.format_report(result))
