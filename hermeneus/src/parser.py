# PROOF: [L2/インフラ] <- hermeneus/src/ CCL パーサー
"""
Hermēneus Parser — CCL 式を AST に変換

PoC (mekhane/ccl/lmql_translator.py) から正式版へリファクタ。
CPL v2.0 制御構文 (F:, I:, W:, L:) に対応。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import re
from typing import Any, Optional, List, Dict
from .ccl_ast import (
    OpType, Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation, ColimitExpansion,
    Pipeline, Parallel,
    ForLoop, IfCondition, WhileLoop, Lambda, Program
)


class CCLParser:
    """CCL パーサー"""
    
    # 認識するワークフロー ID
    WORKFLOWS = {
        # Ousia
        "noe", "bou", "zet", "ene", "o", "o1", "o2", "o3", "o4",
        # Schema
        "s", "met", "mek", "sta", "pra", "s1", "s2", "s3", "s4",
        # Hormē
        "h", "pro", "pis", "ore", "dox", "h1", "h2", "h3", "h4",
        # Perigraphē
        "p", "kho", "hod", "tro", "tek", "p1", "p2", "p3", "p4",
        # Kairos
        "k", "euk", "chr", "tel", "sop", "k1", "k2", "k3", "k4",
        # Akribeia
        "a", "pat", "dia", "gno", "epi", "a1", "a2", "a3", "a4",
        # Meta
        "boot", "bye", "ax", "u", "syn", "pan", "pre", "poc", "why",
        "vet", "tak", "eat", "fit", "flag", "lex", "epo",
    }
    
    # 単項演算子マッピング
    UNARY_OPS = {
        '+': OpType.DEEPEN,
        '-': OpType.CONDENSE,
        '^': OpType.ASCEND,
        '?': OpType.QUERY,
        '\\': OpType.INVERT,
        "'": OpType.DIFF,
        '!': OpType.EXPAND,
    }
    
    # 二項演算子優先順位 (低い方が先に処理)
    # ~* と ~! は ~ より先にマッチさせる（長いトークン優先）
    BINARY_OPS_PRIORITY = ['||', '|>', '_', '~*', '~!', '~', '*^', '*', '>>']
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse(self, ccl: str) -> Any:
        """CCL 式をパース"""
        # コメント削除 (# 以降を行末まで)
        ccl = re.sub(r'#.*$', '', ccl, flags=re.MULTILINE)
        ccl = ccl.strip()
        self.errors = []
        
        try:
            return self._parse_expression(ccl)
        except Exception as e:
            self.errors.append(str(e))
            raise ValueError(f"Parse error: {e}")
    
    def _parse_expression(self, expr: str) -> Any:
        """式をパース (優先順位に従う)"""
        expr = expr.strip()
        
        # 括弧グループの剤離: (...) や {...} の外側が式全体を囲んでいる場合に剥がす
        if (expr.startswith('(') and expr.endswith(')') and
                self._is_balanced_group(expr, '(', ')')):
            return self._parse_expression(expr[1:-1])
        if (expr.startswith('{') and expr.endswith('}') and
                self._is_balanced_group(expr, '{', '}')):
            return self._parse_expression(expr[1:-1])
        
        # マクロ参照 (二項演算子より先にチェック、完全一致のみ)
        if expr.startswith('@'):
            try:
                return self._parse_macro(expr)
            except ValueError:
                pass  # マクロとしてパースできなければ二項演算子チェックへ

        # 二項演算子を優先順位順にチェック
        for op in self.BINARY_OPS_PRIORITY:
            if op in expr:
                # 最も外側の演算子を見つける
                parts = self._split_binary(expr, op)
                if len(parts) > 1:
                    return self._handle_binary(op, parts)

        # Colimit 前置演算子: \WF
        if expr.startswith('\\'):
            inner = expr[1:]
            body = self._parse_expression(inner)
            operators = []
            if isinstance(body, Workflow):
                operators = body.operators
            return ColimitExpansion(body=body, operators=operators)
        
        # CPL 制御構文チェック
        if expr.startswith('F:'):
            return self._parse_for(expr)
        if expr.startswith('I:'):
            return self._parse_if(expr)
        if expr.startswith('W:'):
            return self._parse_while(expr)
        if expr.startswith('L:'):
            return self._parse_lambda(expr)
        if expr.startswith('lim['):
            return self._parse_lim(expr)
        
        # グループ振動: ~(...) — シーケンス全体を振動（反復実行）
        if expr.startswith('~(') and expr.endswith(')') and self._is_balanced_group(expr[1:], '(', ')'):
            inner = expr[2:-1]  # ~( と ) を除去
            body = self._parse_expression(inner)
            return Oscillation(left=body, right=body)
        
        # ワークフロー
        return self._parse_workflow(expr)
    
    def _is_balanced_group(self, expr: str, open_ch: str, close_ch: str) -> bool:
        """式全体がバランスしたグループかを判定する。
        例: (A~*B) -> True, (A)~*(B) -> False
        """
        if not (expr.startswith(open_ch) and expr.endswith(close_ch)):
            return False
        depth = 0
        for i, c in enumerate(expr):
            if c == open_ch:
                depth += 1
            elif c == close_ch:
                depth -= 1
            if depth == 0 and i < len(expr) - 1:
                return False  # 途中で閉じた = 全体を囲んでいない
        return True
    
    def _split_binary(self, expr: str, op: str) -> List[str]:
        """二項演算子で分割 (ネストを考慮)"""
        parts = []
        current = ""
        depth = 0
        i = 0
        
        while i < len(expr):
            c = expr[i]
            
            if c in '[{(':
                depth += 1
                current += c
            elif c in ']})':
                depth -= 1
                current += c
            elif depth == 0 and expr[i:i+len(op)] == op:
                parts.append(current.strip())
                current = ""
                i += len(op) - 1
            else:
                current += c
            
            i += 1
        
        if current.strip():
            parts.append(current.strip())
        
        return parts
    
    def _handle_binary(self, op: str, parts: List[str]) -> Any:
        """二項演算子を処理"""
        if op == '_':
            # シーケンス
            steps = [self._parse_expression(p) for p in parts]
            return Sequence(steps=steps)
        elif op == '~*':
            # 収束振動
            left = self._parse_expression(parts[0])
            right = self._parse_expression('~*'.join(parts[1:]))
            return Oscillation(left=left, right=right, convergent=True)
        elif op == '~!':
            # 発散振動
            left = self._parse_expression(parts[0])
            right = self._parse_expression('~!'.join(parts[1:]))
            return Oscillation(left=left, right=right, divergent=True)
        elif op == '~':
            # 通常の振動
            left = self._parse_expression(parts[0])
            right = self._parse_expression('~'.join(parts[1:]))
            return Oscillation(left=left, right=right)
        elif op == '*^':
            # 融合 + メタ表示 (fusion with meta display)
            left = self._parse_expression(parts[0])
            right = self._parse_expression('*^'.join(parts[1:]))
            return Fusion(left=left, right=right, meta_display=True)
        elif op == '*':
            # 融合
            left = self._parse_expression(parts[0])
            right = self._parse_expression('*'.join(parts[1:]))
            return Fusion(left=left, right=right, meta_display=False)
        elif op == '>>':
            # 収束ループ
            body = self._parse_expression(parts[0])
            condition = self._parse_condition(parts[1])
            return ConvergenceLoop(body=body, condition=condition)
        elif op == '|>':
            # パイプライン: 前段の出力を次段の入力に
            steps = [self._parse_expression(p) for p in parts]
            return Pipeline(steps=steps)
        elif op == '||':
            # 並列実行
            branches = [self._parse_expression(p) for p in parts]
            return Parallel(branches=branches)
        
        # 未知の演算子
        return self._parse_workflow(parts[0])
    
    def _parse_workflow(self, expr: str) -> Workflow:
        """ワークフロー式をパース"""
        # /wf+- 形式 または wf+-
        pattern = r'^/?([a-z][a-z0-9]*)([\+\-\^\?\!\'\\]*)(.*)$'
        match = re.match(pattern, expr)
        
        if not match:
            raise ValueError(f"Invalid workflow: {expr}")
        
        wf_id = match.group(1)
        ops_str = match.group(2)
        rest = match.group(3).strip()
        
        # 演算子を変換
        operators = [self.UNARY_OPS[op] for op in ops_str if op in self.UNARY_OPS]
        
        # 修飾子パース (例: a1:2, --mode=nous)
        modifiers = {}
        mode = None
        
        # --mode=xxx
        mode_match = re.search(r'--mode=(\w+)', rest)
        if mode_match:
            mode = mode_match.group(1)
        
        # 修飾子 (例: +a1:2)
        mod_pattern = r'([a-z]\d):(\d+)'
        for mod_match in re.finditer(mod_pattern, rest):
            modifiers[mod_match.group(1)] = int(mod_match.group(2))
        
        return Workflow(
            id=wf_id,
            operators=operators,
            modifiers=modifiers,
            mode=mode
        )
    
    def _parse_condition(self, expr: str) -> Condition:
        """条件式をパース"""
        expr = expr.strip()
        
        # V[] < 0.3 形式
        pattern = r'(V\[\]|E\[\]|\w+)\s*(<|>|<=|>=|=)\s*([\d.]+)'
        match = re.match(pattern, expr)
        
        if match:
            return Condition(
                var=match.group(1),
                op=match.group(2),
                value=float(match.group(3))
            )
        
        # デフォルト
        return Condition(var="V[]", op="<", value=0.5)
    
    def _parse_macro(self, expr: str) -> MacroRef:
        """マクロ参照をパース"""
        # regex for name part only
        match = re.match(r'^@(\w+)([·×\+\-]?)', expr)
        if not match:
             raise ValueError(f"Invalid macro name: {expr}")

        name = match.group(1)
        operator = match.group(2)
        if operator:
            name = name + operator
            
        rest = expr[match.end():]
        args = []

        if not rest:
            return MacroRef(name=name, args=[])
            
        # Parse (...) if present
        if rest.startswith('('):
            arg_str, end_idx = self._read_balanced(rest, 0, '(', ')')
            args.extend(self._split_args(arg_str))
            rest = rest[end_idx:]
            
        # Parse {...} if present
        if rest.startswith('{'):
             content, end_idx = self._read_balanced(rest, 0, '{', '}')
             # Treat selector content as one arg
             args.append(content)
             rest = rest[end_idx:]

        if rest:
             raise ValueError(f"Invalid macro args or trailing chars: {rest}")

        return MacroRef(name=name, args=args)

    def _split_args(self, args_str: str) -> List[str]:
        """引数リストを分割 (ネストした括弧を考慮)"""
        args = []
        current = ""
        depth = 0

        for c in args_str:
            if c == '(':
                depth += 1
                current += c
            elif c == ')':
                depth -= 1
                current += c
            elif c == ',' and depth == 0:
                args.append(current.strip())
                current = ""
            else:
                current += c

        if current.strip():
            args.append(current.strip())

        return args

    def _read_balanced(self, expr: str, start_idx: int, open_char: str, close_char: str) -> tuple[str, int]:
        """バランスした括弧の中身を読み取る"""
        if start_idx >= len(expr) or expr[start_idx] != open_char:
            raise ValueError(f"Expected '{open_char}' at {start_idx}")

        depth = 0
        for i in range(start_idx, len(expr)):
            c = expr[i]
            if c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth == 0:
                    # Found matching close char
                    return expr[start_idx+1:i], i+1

        raise ValueError(f"Unbalanced '{open_char}' starting at {start_idx}")
    
    def _parse_for(self, expr: str) -> ForLoop:
        """FOR ループをパース: F:[×N]{body} or F:[A,B]{body} or F:N{body}"""
        # Pattern 1: F:[...]{body} (角括弧あり)
        match = re.match(r'F:\[([^\]]+)\]\{(.+)\}$', expr, re.DOTALL)
        if match:
            iter_spec = match.group(1).strip()
            body_str = match.group(2).strip()

            # ×N 形式
            if iter_spec.startswith('×'):
                iterations = int(iter_spec[1:])
            else:
                # リスト形式
                iterations = [i.strip() for i in iter_spec.split(',')]

            body = self._parse_expression(body_str)
            return ForLoop(iterations=iterations, body=body)

        # Pattern 2: F:N{body} (角括弧なし、数値直接指定)
        match2 = re.match(r'F:(\d+)\{(.+)\}$', expr, re.DOTALL)
        if match2:
            iterations = int(match2.group(1))
            body_str = match2.group(2).strip()
            body = self._parse_expression(body_str)
            return ForLoop(iterations=iterations, body=body)

        raise ValueError(f"Invalid FOR loop: {expr}")
    
    def _parse_if(self, expr: str) -> IfCondition:
        """IF 条件分岐をパース: I:[cond]{then} E:{else} or I:cond{then}
        Supports EI:[cond]{then} by recursion.
        """
        expr = expr.strip()

        # Match "I:" or "EI:"
        prefix = "I:"
        if expr.startswith("EI:"):
            prefix = "EI:"
        elif not expr.startswith("I:"):
            raise ValueError(f"Invalid IF: {expr}")

        pos = len(prefix)
        # Check for [condition] or condition
        if pos < len(expr) and expr[pos] == '[':
            cond_str, pos = self._read_balanced(expr, pos, '[', ']')
            # V[outputs] > 0.8 comes as is
            condition = self._parse_condition(cond_str)
        else:
             # simple condition? e.g. I:cond{...}
             # Scan until {
             brace_idx = expr.find('{', pos)
             if brace_idx == -1:
                 raise ValueError("Missing '{' for IF body")
             cond_str = expr[pos:brace_idx].strip()
             pos = brace_idx
             condition = self._parse_condition(cond_str)

        # Read body
        # Skip optional whitespace?
        while pos < len(expr) and expr[pos].isspace():
            pos += 1

        if pos >= len(expr) or expr[pos] != '{':
             raise ValueError("Expected '{' after condition")

        then_body_str, pos = self._read_balanced(expr, pos, '{', '}')
        then_branch = self._parse_expression(then_body_str)

        # Check for Else/ElseIf
        rest = expr[pos:].strip()
        else_branch = None

        if rest.startswith('EI:'):
             # Recursively parse as IfCondition
             else_branch = self._parse_if(rest)
        elif rest.startswith('E:'):
             # Else block
             pos_e = rest.find('{')
             if pos_e == -1:
                 raise ValueError("Missing '{' for ELSE body")
             else_body_str, _ = self._read_balanced(rest, pos_e, '{', '}')
             else_branch = self._parse_expression(else_body_str)

        return IfCondition(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )
    
    def _parse_while(self, expr: str) -> WhileLoop:
        """WHILE ループをパース: W:[cond]{body}"""
        # V[] を含む条件式を許容するパターン
        match = re.match(r'W:\[([^\]]*(?:\[\][^\]]*)*)\]\{(.+)\}$', expr, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid WHILE: {expr}")
        
        condition = self._parse_condition(match.group(1))
        body = self._parse_expression(match.group(2))
        
        return WhileLoop(condition=condition, body=body)
    
    def _parse_lambda(self, expr: str) -> Lambda:
        """Lambda をパース: L:[x]{body}"""
        match = re.match(r'L:\[([^\]]+)\]\{(.+)\}$', expr, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid Lambda: {expr}")
        
        params = [p.strip() for p in match.group(1).split(',')]
        body = self._parse_expression(match.group(2))
        
        return Lambda(params=params, body=body)
    
    def _parse_lim(self, expr: str) -> ConvergenceLoop:
        """lim 正式形をパース: lim[cond]{body}"""
        # V[] を含む条件式を許容するパターン
        match = re.match(r'lim\[([^\]]*(?:\[\][^\]]*)*)\]\{(.+)\}$', expr, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid lim: {expr}")
        
        condition = self._parse_condition(match.group(1))
        body = self._parse_expression(match.group(2))
        
        return ConvergenceLoop(body=body, condition=condition)


# =============================================================================
# Convenience Function
# =============================================================================

def parse_ccl(ccl: str) -> Any:
    """CCL 式をパース (便利関数)"""
    parser = CCLParser()
    return parser.parse(ccl)


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    test_cases = [
        "/noe+",
        "/bou-",
        "/s+_/ene",
        "/noe+ >> V[] < 0.3",
        "/u+ ~ /noe!",
        "/noe * /dia",
        "F:[×3]{/dia}",
        "I:[V[] > 0.5]{/noe+} E:{/noe-}",
        "W:[E[] > 0.3]{/dia}",
        "L:[wf]{wf+}",
        "lim[V[] < 0.3]{/noe+}",
        "/noe+ |> /dia+",
        "/noe+ |> /dia+ |> /ene",
        "/noe+ || /dia+",
        "/noe+ || /dia+ || /ene",
        "(/noe+ || /dia+) |> /ene",
    ]
    
    parser = CCLParser()
    
    for ccl in test_cases:
        print(f"\n{'='*60}")
        print(f"CCL: {ccl}")
        try:
            ast = parser.parse(ccl)
            print(f"AST: {ast}")
        except Exception as e:
            print(f"Error: {e}")
