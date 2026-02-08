#!/usr/bin/env python3
"""Tests for wf_postcheck.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.wf_postcheck import (
    load_sel_enforcement,
    list_all_sel_enforcement,
    postcheck,
    check_requirements,
)


class TestLoadSelEnforcement:
    def test_load_existing(self):
        sel = load_sel_enforcement("boot")
        assert "+" in sel, "boot should have + enforcement"

    def test_load_dia(self):
        sel = load_sel_enforcement("dia")
        assert "+" in sel, "dia should have + enforcement after P0"

    def test_load_nonexistent(self):
        sel = load_sel_enforcement("nonexistent_wf_xyz")
        assert sel == {}, "nonexistent WF should return empty dict"

    def test_load_noe(self):
        sel = load_sel_enforcement("noe")
        assert "+" in sel
        reqs = sel["+"].get("minimum_requirements", [])
        assert len(reqs) >= 3, "noe+ should have 3+ requirements"


class TestListAll:
    def test_list_returns_many(self):
        all_sel = list_all_sel_enforcement()
        assert len(all_sel) >= 39, f"Expected >=39 WFs with sel_enforcement, got {len(all_sel)}"


class TestCheckRequirements:
    def test_matching_content(self):
        content = """
## 証拠セクション
具体的なデータを引用する。実験結果は以下の通り。

## 論拠セクション
推論の連鎖: A → B → C。因果関係は明確。

## 反論セクション
最も強い反論: 「サンプルサイズが小さい」

確信度: 推定
"""
        reqs = [
            "証拠セクション: 具体的データ/事実を引用",
            "論拠セクション: 推論の連鎖を明示",
            "反論セクション: 最も強い反論を提示",
            "確信度: [確信/推定/仮説] を明示",
        ]
        checks = check_requirements(content, reqs)
        passed = sum(1 for c in checks if c["passed"])
        assert passed >= 3, f"Expected >=3 passed, got {passed}: {[c['detail'] for c in checks]}"

    def test_empty_content_fails(self):
        checks = check_requirements("", ["証拠セクション: 具体的データを引用"])
        assert not checks[0]["passed"], "Empty content should fail"


class TestPostcheck:
    def test_dia_plus_pass(self):
        content = """
## 証拠 (Evidence)
実験データ: 39WF中5WFに sel_enforcement がなかった。

## 論拠 (Reasoning)
推論の連鎖: 環境強制なし → 意志依存 → 堕落。

## 反論
最も強い反論: 「LLM は毎回異なるので環境強制も万全ではない」

確信度: 推定 (MEDIUM)
"""
        result = postcheck("dia", "+", content)
        assert result["passed"], f"dia+ should pass: {result['formatted']}"

    def test_dia_plus_fail_empty(self):
        result = postcheck("dia", "+", "PASS. 問題なし。")
        assert not result["passed"], "Empty dia+ should fail"

    def test_no_sel_enforcement(self):
        """WF without sel_enforcement should pass (skip)."""
        result = postcheck("nonexistent_wf", "+", "anything")
        assert result["passed"]

    def test_noe_plus(self):
        content = """
## PHASE 0: 派生選択
nous モードを選択。

## PHASE 1: 前提掘出
前提を3つ特定した。

## PHASE 2: ゼロ設計
GoT 分岐: 経路A, 経路B, 経路C の3つを探索。
Analogy 発想モード: 免疫システムからの類推。

## PHASE 3: 分析深化
Graph of Thought で深掘り。

## PHASE 4: 自己検証
メタ認知レビュー。

## PHASE 5: メタ認知出力
最終出力: ファイル保存済み。
"""
        result = postcheck("noe", "+", content)
        print(result["formatted"])
        # noe+ has 4 requirements; this content should pass most
        passed = sum(1 for c in result["checks"] if c["passed"])
        assert passed >= 2, f"Expected >=2 passed for noe+, got {passed}"


def run_tests():
    import traceback
    test_classes = [TestLoadSelEnforcement, TestListAll, TestCheckRequirements, TestPostcheck]
    passed = 0
    failed = 0
    errors = []

    for cls in test_classes:
        print(f"\n{'='*60}")
        print(f"  {cls.__name__}")
        print(f"{'='*60}")
        instance = cls()
        for method_name in sorted(dir(instance)):
            if not method_name.startswith("test_"):
                continue
            method = getattr(instance, method_name)
            try:
                method()
                print(f"  ✅ {method_name}")
                passed += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                errors.append((f"{cls.__name__}.{method_name}", traceback.format_exc()))
                failed += 1

    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    if errors:
        print("\nErrors:")
        for name, tb in errors:
            print(f"\n--- {name} ---")
            print(tb)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
