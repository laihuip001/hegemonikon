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
    ForLoop, IfCondition, WhileLoop, Lambda, TaggedBlock, LetBinding, Program
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
        
        # Colimit 前置演算子: \WF
        if expr.startswith('\\'):
            inner = expr[1:]
            body = self._parse_expression(inner)
            operators = []
            if isinstance(body, Workflow):
                operators = body.operators
            return ColimitExpansion(body=body, operators=operators)
        
        # let マクロ定義: let @name = CCL
        if expr.startswith('let '):
            return self._parse_let(expr)
        
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
        
        # CPL v2.0 意味タグ: V:{}, C:{}, R:{}, M:{}
        if len(expr) >= 3 and expr[0] in 'VCRM' and expr[1] == ':' and expr[2] == '{':
            return self._parse_tagged_block(expr)
        # E:{} は I: のコンテキスト外では TaggedBlock として処理
        if expr.startswith('E:{'):
            return self._parse_tagged_block(expr)
        
        # グループ振動: ~(...) — シーケンス全体を振動（反復実行）
        # 例: ~(/sop_/noe_/ene_/dia-) = 4WFシーケンスを反復
        # 二項演算子より先にチェック（括弧内の _ で分割されるのを防ぐ）
        if expr.startswith('~(') and expr.endswith(')') and self._is_balanced_group(expr[1:], '(', ')'):
            inner = expr[2:-1]  # ~( と ) を除去
            body = self._parse_expression(inner)
            return Oscillation(left=body, right=body)
        
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
            # シーケンス — 空パーツをフィルタリング
            steps = [self._parse_expression(p) for p in parts if p]
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
            # 空左辺の場合（_ 分割の結果 *^/u+ が独立パーツになったケース）
            if not parts[0]:
                right = self._parse_expression('*^'.join(parts[1:]))
                return Fusion(left=right, right=right, meta_display=True)
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
    
    # Relation suffix partner table (v7.2)
    # Generated from .agent/workflows/*.md category_theory: YAML
    RELATION_PARTNERS = {
        # .d = adjunction (diagonal), .h = natural transformation (horizontal), .x = duality (anti-diagonal)
        # O-series
        "noe": {"d": "zet", "h": "bou", "x": ("ene", "transition")},
        "bou": {"d": "ene", "h": "noe", "x": ("zet", "tension")},
        "zet": {"d": "noe", "h": "ene", "x": ("bou", "tension")},
        "ene": {"d": "bou", "h": "zet", "x": ("noe", "transition")},
        # S-series
        "met": {"d": "sta", "h": "mek", "x": ("pra", "transition")},
        "mek": {"d": "pra", "h": "met", "x": ("sta", "tension")},
        "sta": {"d": "met", "h": "pra", "x": ("mek", "tension")},
        "pra": {"d": "mek", "h": "sta", "x": ("met", "transition")},
        # H-series
        "pro": {"d": "ore", "h": "pis", "x": ("dox", "transition")},
        "pis": {"d": "dox", "h": "pro", "x": ("ore", "tension")},
        "ore": {"d": "pro", "h": "dox", "x": ("pis", "tension")},
        "dox": {"d": "pis", "h": "ore", "x": ("pro", "transition")},
        # P-series
        "kho": {"d": "tro", "h": "hod", "x": ("tek", "transition")},
        "hod": {"d": "tek", "h": "kho", "x": ("tro", "tension")},
        "tro": {"d": "kho", "h": "tek", "x": ("hod", "tension")},
        "tek": {"d": "hod", "h": "tro", "x": ("kho", "transition")},
        # K-series
        "euk": {"d": "tel", "h": "chr", "x": ("sop", "transition")},
        "chr": {"d": "sop", "h": "euk", "x": ("tel", "tension")},
        "tel": {"d": "chr", "h": "sop", "x": ("euk", "tension")},
        "sop": {"d": "tel", "h": "chr", "x": ("euk", "transition")},
        # A-series
        "pat": {"d": "gno", "h": "dia", "x": ("epi", "transition")},
        "dia": {"d": "epi", "h": "pat", "x": ("gno", "tension")},
        "gno": {"d": "pat", "h": "epi", "x": ("dia", "tension")},
        "epi": {"d": "dia", "h": "gno", "x": ("pat", "transition")},
    }

    def _parse_workflow(self, expr: str) -> Workflow:
        """ワークフロー式をパース"""
        # /wf.h+- 形式: relation suffix (.d/.h/.x) を認識
        pattern = r"^/?([a-z][a-z0-9]*)(?:\.(d|h|x))?([+\-\^\?\!\'\\\\]*)(.*)$"
        match = re.match(pattern, expr)
        
        if not match:
            raise ValueError(f"Invalid workflow: {expr}")
        
        wf_id = match.group(1)
        relation = match.group(2)  # None or "d"/"h"/"x"
        ops_str = match.group(3)
        rest = match.group(4).strip()
        
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
        
        # .d/.h/.x 展開: パートナーに自動展開
        if relation and wf_id in self.RELATION_PARTNERS:
            partner_info = self.RELATION_PARTNERS[wf_id].get(relation)
            if partner_info:
                source = Workflow(
                    id=wf_id, operators=[], modifiers={}, mode=None
                )
                if relation == "x" and isinstance(partner_info, tuple):
                    partner_id, duality_type = partner_info
                    target = Workflow(
                        id=partner_id, operators=operators,
                        modifiers=modifiers, mode=mode, relation=relation
                    )
                    if duality_type == "tension":
                        # tension → ~ (oscillation)
                        return Oscillation(left=source, right=target)
                    else:
                        # transition → >> (sequence)
                        return Sequence(steps=[source, target])
                else:
                    # .d or .h → >> (sequence)
                    partner_id = partner_info
                    target = Workflow(
                        id=partner_id, operators=operators,
                        modifiers=modifiers, mode=mode, relation=relation
                    )
                    return Sequence(steps=[source, target])
        
        return Workflow(
            id=wf_id,
            operators=operators,
            modifiers=modifiers,
            mode=mode,
            relation=relation
        )
    
    def _parse_condition(self, expr: str) -> Condition:
        """条件式をパース"""
        expr = expr.strip()
        
        # 拡張パターン: V[] < 0.3, E[] > 0.5, E[/growth] > 0.8
        # 関数呼び出し形式を許容: VAR[任意の中身] OP VALUE
        pattern = r'(V\[[^\]]*\]|E\[[^\]]*\]|\w+)\s*(<|>|<=|>=|=)\s*([\d.]+)'
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
        """FOR ループをパース: F:[×N]{body} or F:[A,B]{body} or F:N{body}"""
        # Pattern 1: F:[...]{body} (角括弧あり、ネスト対応)
        bracket_match = re.match(r'F:\[([^\]]+)\]', expr)
        if bracket_match:
            iter_spec = bracket_match.group(1).strip()
            rest_after_bracket = expr[bracket_match.end():]
            body_str, rest = self._extract_braced_body(rest_after_bracket)
            if body_str is not None:
                # ×N 形式
                if iter_spec.startswith('×'):
                    iterations = int(iter_spec[1:])
                else:
                    # リスト形式
                    iterations = [i.strip() for i in iter_spec.split(',')]
                
                body = self._parse_expression(body_str)
                
                # body 後に続く式がある場合 (例: F:[...]{...}, ~(...))
                if rest:
                    for_node = ForLoop(iterations=iterations, body=body)
                    if rest.startswith(','):
                        rest = rest[1:].strip()
                    if rest.startswith('_'):
                        rest = rest[1:].strip()
                    if rest:
                        rest_node = self._parse_expression(rest)
                        return Sequence(steps=[for_node, rest_node])
                    return for_node
                
                return ForLoop(iterations=iterations, body=body)

        # Pattern 2: F:N{body} (角括弧なし、数値直接指定)
        num_match = re.match(r'F:(\d+)', expr)
        if num_match:
            iterations = int(num_match.group(1))
            rest_after_num = expr[num_match.end():]
            body_str, _ = self._extract_braced_body(rest_after_num)
            if body_str is not None:
                body = self._parse_expression(body_str)
                return ForLoop(iterations=iterations, body=body)

        raise ValueError(f"Invalid FOR loop: {expr}")
    
    def _parse_if(self, expr: str) -> IfCondition:
        """IF 条件分岐をパース: I:[cond]{then} EI:[cond]{elif} E:{else}"""
        # Pattern 1: I:[cond]{then} — ネストした [] と {} に対応
        if expr.startswith('I:['):
            # I:[ の後から対応する ] を見つける（]{の並びを閉じ判定に使用）
            depth = 0
            cond_end = -1
            for i in range(3, len(expr)):
                if expr[i] == '[':
                    depth += 1
                elif expr[i] == ']':
                    if depth > 0:
                        depth -= 1
                    else:
                        # 次の文字が { なら正しい閉じ括弧
                        if i + 1 < len(expr) and expr[i + 1] == '{':
                            cond_end = i
                            break
                        # V[] のような内部 [] はスキップ
            
            if cond_end > 0:
                cond_str = expr[3:cond_end]
                condition = self._parse_condition(cond_str)
                rest_after_cond = expr[cond_end + 1:]
                body_str, rest = self._extract_braced_body(rest_after_cond)
                if body_str is not None:
                    then_branch = self._parse_expression(body_str)
                    else_branch = self._parse_else_chain(rest) if rest else None
                    return IfCondition(
                        condition=condition,
                        then_branch=then_branch,
                        else_branch=else_branch
                    )

        # Pattern 2: I:cond{then} (角括弧なし、シンプル条件)
        match2 = re.match(r'I:(\w+)', expr)
        if match2:
            condition = Condition(var=match2.group(1), op=">", value=0)
            rest_after_cond = expr[match2.end():]
            body_str, rest = self._extract_braced_body(rest_after_cond)
            if body_str is not None:
                then_branch = self._parse_expression(body_str)
                else_branch = self._parse_else_chain(rest) if rest else None
                return IfCondition(
                    condition=condition,
                    then_branch=then_branch,
                    else_branch=else_branch
                )

        raise ValueError(f"Invalid IF: {expr}")

    def _parse_else_chain(self, rest: str) -> Any:
        """EI:/E: チェインをパース → ネストされた IfCondition に変換"""
        rest = rest.strip()
        if not rest:
            return None
        
        # EI:[cond]{body}... → 再帰的に IfCondition をネスト
        if rest.startswith('EI:'):
            # EI: を I: に置換して再帰パース
            return self._parse_if('I:' + rest[3:])
        
        # E:{body} → else ブランチ (ネスト対応)
        if rest.startswith('E:'):
            body_str, _ = self._extract_braced_body(rest[2:])
            if body_str is not None:
                return self._parse_expression(body_str)
        
        return None
    
    def _extract_braced_body(self, s: str) -> tuple:
        """先頭の {body} を抽出 (ネスト対応)。
        
        Returns:
            (body_str, rest) — body_str は {} 内の文字列、rest は残りの文字列。
            body_str が None の場合は抽出失敗。
        """
        s = s.strip()
        if not s or s[0] != '{':
            return (None, s)
        
        depth = 0
        for i, c in enumerate(s):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    body = s[1:i].strip()
                    rest = s[i+1:].strip()
                    return (body, rest)
        
        return (None, s)
    
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
        # E[/growth] 等の角括弧内に内容がある関数呼び出しにも対応
        match = re.match(r'lim\[([^\]]*(?:\[[^\]]*\][^\]]*)*)\]\{(.+)\}$', expr)
        if not match:
            raise ValueError(f"Invalid lim: {expr}")
        
        condition = self._parse_condition(match.group(1))
        body = self._parse_expression(match.group(2))
        
        return ConvergenceLoop(body=body, condition=condition)

    def _parse_let(self, expr: str) -> LetBinding:
        """let マクロ定義をパース: let @name = CCL"""
        match = re.match(r'let\s+@(\w+)\s*=\s*(.+)$', expr)
        if not match:
            raise ValueError(f"Invalid let: {expr}")
        
        name = match.group(1)
        body = self._parse_expression(match.group(2))
        
        return LetBinding(name=name, body=body)

    def _parse_tagged_block(self, expr: str) -> 'TaggedBlock':
        """意味タグ付きブロックをパース: V:{body}, C:{body}, R:{body}, M:{body}, E:{body}"""
        tag = expr[0]  # V, C, R, M, or E
        # tag:{ の後の body を抽出 (ネストしたブラケットを考慮)
        if not expr[2] == '{':
            raise ValueError(f"Invalid tagged block: {expr}")
        
        # ネストした {} を考慮して body を抽出
        depth = 0
        body_start = 2  # ':' の次の '{'
        body_end = -1
        for i in range(body_start, len(expr)):
            if expr[i] == '{':
                depth += 1
            elif expr[i] == '}':
                depth -= 1
                if depth == 0:
                    body_end = i
                    break
        
        if body_end == -1:
            raise ValueError(f"Unmatched braces in tagged block: {expr}")
        
        body_str = expr[body_start + 1:body_end].strip()
        body = self._parse_expression(body_str)
        
        # タグブロック後に続く式がある場合（例: V:{/dia}_I:[pass]{...}）
        rest = expr[body_end + 1:].strip()
        if rest:
            # 残りの部分（通常は _ で接続されている）を処理
            if rest.startswith('_'):
                rest = rest[1:].strip()
            rest_node = self._parse_expression(rest)
            tagged = TaggedBlock(tag=tag, body=body)
            return Sequence(steps=[tagged, rest_node])
        
        return TaggedBlock(tag=tag, body=body)


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
        "I:[V[]<0.3]{/ene+} EI:[V[]>0.7]{/pra+} E:{/zet}",  # EI: チェイン
        "W:[E[] > 0.3]{/dia}",
        "L:[wf]{wf+}",
        "lim[V[] < 0.3]{/noe+}",
        "lim[E[/growth]>0.8]{/noe+ _ /dia}",  # E[/growth] 拡張条件
        "let @think = /noe+ _ /dia",  # let マクロ定義
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
