# PROOF: [L2/インフラ]
# Phase 2: CCL 出力検証

"""
CCL Output Validator - 出力検証モジュール

目的:
- 演算子別必須セクションの存在確認
- 最小長の検証
- 違反時のリジェクト + 再生成指示
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import re


@dataclass
class ValidationError:
    """検証エラー"""
    operator: str
    error_type: str
    message: str
    suggestion: str


@dataclass
class ValidationResult:
    """検証結果"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[str]
    
    @property
    def regeneration_instruction(self) -> str:
        """再生成用の指示を生成"""
        if self.valid:
            return ""
        
        lines = ["## ❌ 検証失敗 — 再生成が必要\n"]
        lines.append("以下の問題を修正して再生成してください:\n")
        
        for i, err in enumerate(self.errors, 1):
            lines.append(f"### {i}. {err.error_type}")
            lines.append(f"- **演算子**: `{err.operator}`")
            lines.append(f"- **問題**: {err.message}")
            lines.append(f"- **修正**: {err.suggestion}\n")
        
        return "\n".join(lines)


# 演算子と必須セクションのマッピング
OPERATOR_REQUIRED_SECTIONS: Dict[str, List[str]] = {
    "!": ["## 全派生", "派生リスト", "同時実行"],
    "~": ["## 振動", "↔", "←", "→"],
    "*": ["## 融合", "統合結果"],
    "^": ["## メタ", "メタ分析", "メタ視点"],
    "+": ["## 詳細", "詳細展開"],
}

# 演算子ごとの最小出力行数
OPERATOR_MIN_LINES: Dict[str, int] = {
    "!": 20,  # 全派生は長くなるはず
    "~": 15,  # 振動は両方向必要
    "*": 10,
    "^": 10,
    "+": 15,
}


class CCLOutputValidator:
    """CCL 出力検証器"""
    
    def parse_operators(self, ccl_expr: str) -> Set[str]:
        """CCL 式から演算子を抽出"""
        operators = set()
        for char in ccl_expr:
            if char in OPERATOR_REQUIRED_SECTIONS:
                operators.add(char)
        return operators
    
    def check_required_sections(self, output: str, operators: Set[str]) -> List[ValidationError]:
        """必須セクションの存在確認"""
        errors = []
        
        for op in operators:
            if op not in OPERATOR_REQUIRED_SECTIONS:
                continue
            
            required = OPERATOR_REQUIRED_SECTIONS[op]
            found = False
            
            for keyword in required:
                if keyword.lower() in output.lower():
                    found = True
                    break
            
            if not found:
                errors.append(ValidationError(
                    operator=op,
                    error_type="必須セクション欠落",
                    message=f"演算子 `{op}` に必要なセクションがありません",
                    suggestion=f"以下のいずれかを出力に含めてください: {', '.join(required)}"
                ))
        
        return errors
    
    def check_oscillation_bidirectional(self, output: str) -> List[ValidationError]:
        """振動演算子の両方向確認"""
        errors = []
        
        # 振動の両方向を示すパターン
        has_forward = bool(re.search(r'→|方向[12AB]|←.*→|A.*B', output))
        has_backward = bool(re.search(r'←|方向[12AB]|→.*←|B.*A', output))
        
        if "振動" in output and not (has_forward and has_backward):
            errors.append(ValidationError(
                operator="~",
                error_type="振動の一方向のみ",
                message="振動演算子は両方向の分析が必要です",
                suggestion="「A ↔ B」のように両方向を明示してください"
            ))
        
        return errors
    
    def check_minimum_length(self, output: str, operators: Set[str]) -> List[ValidationError]:
        """最小長の確認"""
        errors = []
        lines = output.strip().split("\n")
        
        for op in operators:
            if op in OPERATOR_MIN_LINES:
                min_lines = OPERATOR_MIN_LINES[op]
                if len(lines) < min_lines:
                    errors.append(ValidationError(
                        operator=op,
                        error_type="出力が短すぎる",
                        message=f"演算子 `{op}` を使用した出力は最低 {min_lines} 行必要ですが、{len(lines)} 行しかありません",
                        suggestion="より詳細な出力を生成してください"
                    ))
        
        return errors
    
    def check_operator_understanding(self, output: str, operators: Set[str]) -> List[ValidationError]:
        """演算子理解の証拠確認"""
        errors = []
        
        # 理解確認セクションの存在
        has_understanding = "理解" in output or "確認" in output or "A:" in output
        
        if not has_understanding:
            errors.append(ValidationError(
                operator="*",  # 汎用
                error_type="理解証明欠落",
                message="演算子理解の証明がありません",
                suggestion="「## 理解確認」セクションで各演算子の意味を説明してください"
            ))
        
        return errors
    
    def validate(self, output: str, ccl_expr: str) -> ValidationResult:
        """出力を検証"""
        operators = self.parse_operators(ccl_expr)
        errors = []
        warnings = []
        
        # 各種チェック
        errors.extend(self.check_required_sections(output, operators))
        errors.extend(self.check_oscillation_bidirectional(output) if "~" in operators else [])
        errors.extend(self.check_minimum_length(output, operators))
        errors.extend(self.check_operator_understanding(output, operators))
        
        # 警告（エラーではないがベストプラクティス違反）
        if len(output) < 500:
            warnings.append("⚠️ 出力が500文字未満です。省略していませんか？")
        
        if "自己監査" not in output and "self-audit" not in output.lower():
            warnings.append("⚠️ 自己監査セクションがありません")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


# テスト用
if __name__ == "__main__":
    validator = CCLOutputValidator()
    
    # 不完全な出力をテスト
    bad_output = """
    分析結果です。
    終わり。
    """
    
    result = validator.validate(bad_output, "/noe!~/u+")
    print(f"Valid: {result.valid}")
    print(f"Errors: {len(result.errors)}")
    for err in result.errors:
        print(f"  - {err.error_type}: {err.message}")
    print(result.regeneration_instruction)
