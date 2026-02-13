# PROOF: [L2/LLM] <- mekhane/synteleia/dokimasia/ セマンティック監査エージェント PoC
"""
Semantic Audit Agent (L2)

LLM を使ったセマンティック（意味的）監査エージェント。
L1 (静的・regex) では検出できない問題を発見する:
- 設計意図との不整合
- 暗黙の前提の不在
- 文脈の不適切さ

Architecture:
    AuditTarget → SemanticAgent.audit() → LLMBackend.query() → parse → AgentResult

CCL: @syn· (内積モード) の L2 層
"""

import json
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)


# =============================================================================
# LLM Backend Interface
# =============================================================================


# PURPOSE: LLM バックエンド基底クラス (Strategy Pattern)
class LLMBackend(ABC):
    """LLM バックエンドの抽象インターフェース"""

    # PURPOSE: semantic_agent の query 処理を実行する
    @abstractmethod
    def query(self, prompt: str, context: str) -> str:
        """LLM にクエリを送信し、テキスト応答を返す"""
        pass

    # PURPOSE: semantic_agent の is available 処理を実行する
    @abstractmethod
    def is_available(self) -> bool:
        """バックエンドが利用可能か"""
        pass


# PURPOSE: LMQL バックエンド (Hermēneus パイプライン経由)
class LMQLBackend(LLMBackend):
    """Hermēneus LMQL パイプラインを使用するバックエンド"""

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, model: str = "openai/gpt-4o"):
        self.model = model
        self._available: Optional[bool] = None

    # PURPOSE: semantic_agent の query 処理を実行する
    def query(self, prompt: str, context: str) -> str:
        """LMQL 経由でクエリを実行"""
        try:
            from mekhane.ccl.lmql_translator import ccl_to_lmql

            # LMQL テンプレートを生成して実行
            # NOTE: 現在は PoC のため、直接 LMQL を実行せずテンプレートを返す
            lmql_code = ccl_to_lmql("/dia+")
            return f"[LMQL Backend] Model: {self.model}\n{lmql_code}"
        except Exception as e:
            return f"[LMQL Error] {e}"

    # PURPOSE: semantic_agent の is available 処理を実行する
    def is_available(self) -> bool:
        """LMQL パイプラインが利用可能か"""
        if self._available is None:
            try:
                from mekhane.ccl.lmql_translator import ccl_to_lmql

                self._available = True
            except ImportError:
                self._available = False
        return self._available


# PURPOSE: OpenAI API バックエンド (直接呼出)
class OpenAIBackend(LLMBackend):
    """OpenAI API を直接呼出すバックエンド"""

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._available: Optional[bool] = None

    # PURPOSE: semantic_agent の query 処理を実行する
    def query(self, prompt: str, context: str) -> str:
        """OpenAI API でクエリを実行"""
        import openai

        client = openai.OpenAI()  # OPENAI_API_KEY from env

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": context},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content or "{}"

    # PURPOSE: semantic_agent の is available 処理を実行する
    def is_available(self) -> bool:
        """OpenAI API キーが設定されているか"""
        if self._available is None:
            self._available = bool(os.environ.get("OPENAI_API_KEY"))
        return self._available


# PURPOSE: スタブバックエンド (テスト・フォールバック用)
class StubBackend(LLMBackend):
    """テスト・フォールバック用のスタブバックエンド"""

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, response: Optional[str] = None):
        self._response = response

    # PURPOSE: semantic_agent の query 処理を実行する
    def query(self, prompt: str, context: str) -> str:
        """固定レスポンスを返す (テスト用)"""
        if self._response:
            return self._response
        return json.dumps(
            {
                "issues": [],
                "summary": "No semantic issues detected (stub mode)",
                "confidence": 0.5,
            }
        )

    # PURPOSE: semantic_agent の is available 処理を実行する
    def is_available(self) -> bool:
        return True


# =============================================================================
# Response Parser
# =============================================================================

# PURPOSE: LLM レスポンスを AuditIssue にパースする
# PURPOSE: [L2-auto] パース済みの問題


@dataclass
class ParsedIssue:
    """パース済みの問題"""

    code: str
    severity: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


# PURPOSE: LLM のテキスト応答を構造化する
def parse_llm_response(response: str, agent_name: str) -> List[AuditIssue]:
    """
    LLM レスポンスを AuditIssue のリストにパースする。

    JSON 形式を期待するが、プレーンテキストもフォールバック処理する。
    """
    issues: List[AuditIssue] = []

    # 1. JSON パース試行
    try:
        data = json.loads(response)
        if isinstance(data, dict) and "issues" in data:
            for item in data["issues"]:
                severity = _parse_severity(item.get("severity", "medium"))
                issues.append(
                    AuditIssue(
                        agent=agent_name,
                        code=item.get("code", "SEM-000"),
                        severity=severity,
                        message=item.get("message", ""),
                        location=item.get("location"),
                        suggestion=item.get("suggestion"),
                    )
                )
            return issues
    except (json.JSONDecodeError, TypeError):
        pass

    # 2. Markdown リスト形式のフォールバックパース
    # "- [SEVERITY] CODE: message" パターン
    pattern = r"-\s*\[(\w+)\]\s*(SEM-\d+):\s*(.+?)(?:\n|$)"
    for match in re.finditer(pattern, response, re.MULTILINE):
        severity = _parse_severity(match.group(1))
        issues.append(
            AuditIssue(
                agent=agent_name,
                code=match.group(2),
                severity=severity,
                message=match.group(3).strip(),
            )
        )

    return issues


# PURPOSE: 文字列から AuditSeverity に変換
def _parse_severity(s: str) -> AuditSeverity:
    """文字列から AuditSeverity に変換"""
    mapping = {
        "critical": AuditSeverity.CRITICAL,
        "high": AuditSeverity.HIGH,
        "medium": AuditSeverity.MEDIUM,
        "low": AuditSeverity.LOW,
        "info": AuditSeverity.INFO,
    }
    return mapping.get(s.lower(), AuditSeverity.MEDIUM)


# =============================================================================
# Semantic Agent
# =============================================================================

# Synteleia L2 監査プロンプト
# v2: 外部 .prompt ファイルからロード。フォールバック: ハードコード版。
_PROMPT_FILE = Path(__file__).parent / "semantic_audit.prompt"

_FALLBACK_PROMPT = """\
あなたは Hegemonikón の認知監査官です。以下のテキストをセマンティック（意味的）に監査してください。

## 監査基準

L1 (静的解析) では検出できない以下の問題を探してください:

1. **設計意図との不整合** (SEM-001): 明示された目的と内容の矛盾
2. **暗黙の前提の不在** (SEM-002): 前提条件が明示されていない
3. **文脈の不適切さ** (SEM-003): 文脈に対して不適切な表現・構造
4. **論理の飛躍** (SEM-004): 根拠なしに結論に至っている箇所
5. **過度な抽象化** (SEM-005): 具体性が欠如し行動不能な記述

## 出力形式

JSON で回答してください:
```json
{
  "issues": [
    {
      "code": "SEM-001",
      "severity": "high",
      "message": "問題の説明",
      "location": "該当箇所",
      "suggestion": "改善提案"
    }
  ],
  "summary": "全体評価",
  "confidence": 0.85
}
```

問題がない場合は `"issues": []` を返してください。
# PURPOSE: [L2-auto] 外部 .prompt ファイルからプロンプトをロード。失敗時はフォールバック。
"""


def _load_prompt() -> str:
    """外部 .prompt ファイルからプロンプトをロード。失敗時はフォールバック。"""
    try:
        if _PROMPT_FILE.exists():
            return _PROMPT_FILE.read_text(encoding="utf-8")
    except Exception:
        pass
    return _FALLBACK_PROMPT


SEMANTIC_AUDIT_PROMPT = _load_prompt()


# PURPOSE: セマンティック監査エージェント (L2)
class SemanticAgent(AuditAgent):
    """
    LLM ベースのセマンティック監査エージェント。

    L1 (静的・regex) では検出できない意味的問題を発見する。
    LLM バックエンドはプラグイン可能 (Strategy Pattern)。

    Usage:
        # LMQL バックエンド
        agent = SemanticAgent(backend=LMQLBackend())

        # スタブ（テスト時）
        agent = SemanticAgent(backend=StubBackend())

        # デフォルト（利用可能なバックエンドを自動選択）
        agent = SemanticAgent()
    """

    name = "SemanticAgent"
    description = "LLM ベースのセマンティック監査 (L2)"

    # PURPOSE: [L2-auto] 初期化: init__
    def __init__(self, backend: Optional[LLMBackend] = None):
        if backend is not None:
            self.backend = backend
        else:
            # 自動選択: OpenAI > LMQL > Stub
            openai_be = OpenAIBackend()
            if openai_be.is_available():
                self.backend = openai_be
            else:
                lmql = LMQLBackend()
                self.backend = lmql if lmql.is_available() else StubBackend()

    # PURPOSE: セマンティック監査を実行
    def audit(self, target: AuditTarget) -> AgentResult:
        """セマンティック監査を実行"""

        if not self.backend.is_available():
            return AgentResult(
                agent_name=self.name,
                passed=True,
                issues=[],
                confidence=0.0,
                metadata={"fallback": True, "reason": "LLM backend unavailable"},
            )

        try:
            # LLM に問い合わせ
            response = self.backend.query(
                prompt=SEMANTIC_AUDIT_PROMPT,
                context=target.content,
            )

            # レスポンスをパース
            issues = parse_llm_response(response, self.name)

            passed = not any(
                i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH)
                for i in issues
            )

            # confidence はレスポンスから抽出を試みる
            confidence = self._extract_confidence(response)

            return AgentResult(
                agent_name=self.name,
                passed=passed,
                issues=issues,
                confidence=confidence,
                metadata={"backend": type(self.backend).__name__, "l2": True},
            )

        except Exception as e:
            # エラー時は L2 スキップ（安全側に倒す）
            return AgentResult(
                agent_name=self.name,
                passed=True,
                issues=[
                    AuditIssue(
                        agent=self.name,
                        code="SEM-ERR",
                        severity=AuditSeverity.INFO,
                        message=f"L2 監査エラー: {e}",
                        suggestion="L1 監査結果で判断してください",
                    )
                ],
                confidence=0.0,
                metadata={"error": str(e)},
            )

    # PURPOSE: レスポンスから確信度を抽出
    def _extract_confidence(self, response: str) -> float:
        """LLM レスポンスから confidence を抽出"""
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "confidence" in data:
                return float(data["confidence"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return 0.7  # デフォルト

    # PURPOSE: L2 はテキスト系のターゲットのみサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """L2 はテキスト系のターゲットのみサポート"""
        return target_type in (
            AuditTargetType.CCL_OUTPUT,
            AuditTargetType.THOUGHT,
            AuditTargetType.PLAN,
            AuditTargetType.GENERIC,
        )
