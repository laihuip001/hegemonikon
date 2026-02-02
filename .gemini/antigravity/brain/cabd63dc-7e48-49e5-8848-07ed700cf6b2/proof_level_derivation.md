# PROOF 粒度の FEP 演繹

## 1. 前提: 公理階層構造

Hegemonikón は FEP (予測誤差最小化) を頂点とする 4 層構造:

```
L0:   FEP (What)
L1:   Flow, Value (Who/Why)
L1.5: Scale, Function (Where-When/How)
L1.75: Valence, Precision (Which/How much)
```

これらから 24 定理が生成される:

| Level | Series | 生成 |
|-------|--------|------|
| L0 | O (Ousia) | Flow × Value |
| L1 | S (Schema) | Flow × Scale |
| L2a | H (Hormē) | Flow × Valence |
| L2b | P (Perigraphē) | Scale × Scale |
| L3 | K (Kairos) | Scale × Valence |
| L4 | A (Akribeia) | Valence × Valence |

---

## 2. L1/L2/L3 への対応付け

### 仮説: PROOF レベルは定理レベルに対応する

| PROOF Level | 対応する公理 Level | 意味 |
|-------------|-------------------|------|
| **L1 定理** | L0-L1 (O, S) | システムの存在理由。不可欠。 |
| **L2 インフラ** | L2-L3 (H, P, K) | 定理を実現するための構造。 |
| **L3 テスト** | L4 (A) | 品質検証。なくても動作する。 |

### 演繹的導出

**公理 A0 (FEP)**:
> システムは予測誤差を最小化する方向に構成される

**定理 1**: 不可欠なファイルは予測誤差を直接減少させる

ファイル F が存在しないとき、システムの予測誤差 ΔE:

- ΔE → ∞ (システム機能不全) → L1
- ΔE > 0 (機能低下) → L2
- ΔE ≈ 0 (品質低下のみ) → L3

**定理 2**: L1 は O/S に対応する

O (Ousia) = 本質的認識、S (Schema) = 構造設計
→ これらを実装するファイルがなければシステムは成立しない
→ 予測誤差は無限大

**定理 3**: L2 は H/P/K に対応する

H (Hormē) = 動機、P (Perigraphē) = 境界、K (Kairos) = タイミング
→ なくても動作するが、精度が落ちる
→ 予測誤差は増加するが有限

**定理 4**: L3 は A (Akribeia) に対応する

A (Akribeia) = 精密さ、検証、批判
→ テストコードは品質保証だが、本番機能ではない
→ 予測誤差は間接的にのみ影響

---

## 3. 実装への適用

### ファイル分類基準

| 条件 | Level |
|------|-------|
| CCL パーサー、FEP 統合、コア定理ロジック | L1 |
| アダプタ、ファクトリ、MCP サーバー、索引 | L2 |
| テストコード、ユーティリティスクリプト | L3 |

### メタ検証

この分類自体を FEP で検証:

- L1/L2/L3 の区分は予測誤差を最小化するか?
- 区分がないとき: 全ファイルが等価に見え、優先順位がつかない
- 区分があるとき: 重要度が明確になり、保守効率が向上

→ 区分は予測誤差を減少させる ✓

---

## 4. CI 統合設計

### check_proof.py

```python
#!/usr/bin/env python3
"""
PROOF Header Checker - CI Integration

mekhane/ 以下の全 Python ファイルに PROOF ヘッダーがあることを検証。
"""

import sys
from pathlib import Path

MEKHANE = Path(__file__).parent.parent / "mekhane"
REQUIRED_PATTERN = "PROOF:"

def check_proofs() -> tuple[int, int]:
    """Check all Python files for PROOF headers."""
    total = 0
    missing = []
    
    for f in MEKHANE.rglob("*.py"):
        if "__pycache__" in str(f):
            continue
        total += 1
        content = f.read_text(encoding="utf-8", errors="ignore")
        if REQUIRED_PATTERN not in content:
            missing.append(f)
    
    return total, missing

def main():
    total, missing = check_proofs()
    
    if missing:
        print(f"❌ PROOF missing in {len(missing)}/{total} files:")
        for f in missing[:10]:
            print(f"  - {f.relative_to(MEKHANE.parent)}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        sys.exit(1)
    
    print(f"✅ All {total} files have PROOF headers")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### pre-commit hook (.pre-commit-config.yaml)

```yaml
repos:
  - repo: local
    hooks:
      - id: check-proof
        name: Check PROOF headers
        entry: python mekhane/scripts/check_proof.py
        language: python
        types: [python]
        pass_filenames: false
```

---

## 5. 次のステップ

1. [ ] この設計をレビュー
2. [ ] `check_proof.py` を実装
3. [ ] pre-commit または CI に統合
4. [ ] PROOF レベル検証 (L1/L2/L3 の妥当性チェック)
