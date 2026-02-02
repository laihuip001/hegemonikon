# PROOF: [L2/インフラ] <- hermeneus/src/ CCL パーサー
"""
Hermēneus Parser — CCL 式を AST に変換

PoC (mekhane/ccl/lmql_translator.py) から正式版へリファクタ。
CPL v2.0 制御構文 (F:, I:, W:, L:) に対応。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import re
from typing import Any, Optional, List, Dict
from .ast import (
    OpType, Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation,
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
    BINARY_OPS_PRIORITY = ['_', '~', '*', '>>', '|>', '||']
    
    def __init__(self):
        self.errors: List[str] = []
    
    def parse(self, ccl: str) -> Any:
        """CCL 式をパース"""
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
        
        # 二項演算子を優先順位順にチェック
        for op in self.BINARY_OPS_PRIORITY:
            if op in expr:
                # 最も外側の演算子を見つける
                parts = self._split_binary(expr, op)
                if len(parts) > 1:
                    return self._handle_binary(op, parts)
        
        # マクロ参照
        if expr.startswith('@'):
            return self._parse_macro(expr)
        
        # ワークフロー
        return self._parse_workflow(expr)
    
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
        elif op == '~':
            # 振動
            left = self._parse_expression(parts[0])
            right = self._parse_expression('~'.join(parts[1:]))
            return Oscillation(left=left, right=right)
        elif op == '*':
            # 融合
            left = self._parse_expression(parts[0])
            right = self._parse_expression('*'.join(parts[1:]))
            meta = parts[0].endswith('^')  # *^ パターン
            return Fusion(left=left, right=right, meta_display=meta)
        elif op == '>>':
            # 収束ループ
            body = self._parse_expression(parts[0])
            condition = self._parse_condition(parts[1])
            return ConvergenceLoop(body=body, condition=condition)
        
        # パイプライン・並列は未実装 (将来)
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
        # 拡張パターン: @name[·×+-]? または @name{...} または @name(...)
        # 1. @syn· @syn× など演算子付き
        # 2. @S{O,A,K} などセレクタ付き
        # 3. @think(param) など引数付き
        match = re.match(r'@(\w+)([·×\+\-]?)(?:\{([^}]*)\}|\(([^)]*)\))?', expr)
        if match:
            name = match.group(1)
            operator = match.group(2)
            selector = match.group(3)  # {} 内
            args_str = match.group(4)  # () 内
            
            # 演算子があれば名前に付加
            if operator:
                name = name + operator
            
            # 引数解析
            args = []
            if selector:
                args = [selector]  # セレクタは1つの引数として扱う
            elif args_str:
                args = [a.strip() for a in args_str.split(',')]
            
            return MacroRef(name=name, args=args)
        raise ValueError(f"Invalid macro: {expr}")
    
    def _parse_for(self, expr: str) -> ForLoop:
        """FOR ループをパース: F:[×N]{body} or F:[A,B]{body}"""
        match = re.match(r'F:\[([^\]]+)\]\{(.+)\}$', expr)
        if not match:
            raise ValueError(f"Invalid FOR loop: {expr}")
        
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
    
    def _parse_if(self, expr: str) -> IfCondition:
        """IF 条件分岐をパース: I:[cond]{then} E:{else}"""
        # V[] を含む条件式を許容するパターン
        pattern = r'I:\[([^\]]*(?:\[\][^\]]*)*)\]\{([^}]+)\}(?:\s*E:\{([^}]+)\})?'
        match = re.match(pattern, expr)
        if not match:
            raise ValueError(f"Invalid IF: {expr}")
        
        condition = self._parse_condition(match.group(1))
        then_branch = self._parse_expression(match.group(2))
        else_branch = self._parse_expression(match.group(3)) if match.group(3) else None
        
        return IfCondition(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch
        )
    
    def _parse_while(self, expr: str) -> WhileLoop:
        """WHILE ループをパース: W:[cond]{body}"""
        # V[] を含む条件式を許容するパターン
        match = re.match(r'W:\[([^\]]*(?:\[\][^\]]*)*)\]\{(.+)\}$', expr)
        if not match:
            raise ValueError(f"Invalid WHILE: {expr}")
        
        condition = self._parse_condition(match.group(1))
        body = self._parse_expression(match.group(2))
        
        return WhileLoop(condition=condition, body=body)
    
    def _parse_lambda(self, expr: str) -> Lambda:
        """Lambda をパース: L:[x]{body}"""
        match = re.match(r'L:\[([^\]]+)\]\{(.+)\}$', expr)
        if not match:
            raise ValueError(f"Invalid Lambda: {expr}")
        
        params = [p.strip() for p in match.group(1).split(',')]
        body = self._parse_expression(match.group(2))
        
        return Lambda(params=params, body=body)
    
    def _parse_lim(self, expr: str) -> ConvergenceLoop:
        """lim 正式形をパース: lim[cond]{body}"""
        # V[] を含む条件式を許容するパターン
        match = re.match(r'lim\[([^\]]*(?:\[\][^\]]*)*)\]\{(.+)\}$', expr)
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
