#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/dendron/ A0→PROOF自動生成が必要→proof_skeletonが担う
"""
PROOF.md Skeleton Generator — 新ディレクトリ作成時に PROOF.md を自動生成する。

引力原理: 「PROOF を書く」のではなく「PROOF が最初からそこにある」。
書くコストをゼロにすることで、PROOF なしディレクトリを構造的に不可能にする。

Usage:
    python mekhane/dendron/proof_skeleton.py mekhane/new_module/
    python mekhane/dendron/proof_skeleton.py mekhane/ --scan  # PROOF なしを検出
"""

import argparse
import sys
from pathlib import Path
from typing import Optional


# PURPOSE: ディレクトリ名と親ディレクトリから PURPOSE を推定する
def infer_proof_purpose(dir_path: Path) -> str:
    """ディレクトリ名から PURPOSE を推定する。"""
    name = dir_path.name
    patterns = {
        "fep": "自由エネルギー原理 (FEP) に基づく認知評価・意思決定エンジン",
        "dendron": "コード品質・存在証明の検証と自動生成",
        "taxis": "タスク分類・優先順位付け・射提案",
        "anamnesis": "長期記憶・ベクトル検索・知識管理",
        "symploke": "統合・ブート・WF 連携",
        "peira": "システム健全性チェック・ヘルスモニタ",
        "synteleia": "安全性チェック・白血球 (WBC)",
        "poiema": "構造化出力の生成・テンプレート",
        "ergasterion": "外部ツール連携・n8n・Digestor",
        "tests": "テストスイート",
        "scripts": "CLI ツール・ユーティリティスクリプト",
        "api": "API エンドポイント・外部インターフェース",
        "models": "データモデル・型定義",
        "deploy": "デプロイ・CI/CD 構成",
    }
    return patterns.get(name, f"{name} の実装")


# PURPOSE: ディレクトリ名と親パスから REASON を推定する
def infer_proof_reason(dir_path: Path) -> str:
    """ディレクトリが存在する理由を推定する。"""
    parent = dir_path.parent.name
    name = dir_path.name
    return (
        f"{parent} の機能を担う {name} の実装が必要だった"
    )


# PURPOSE: 内容物テーブルの行を生成する
def scan_contents(dir_path: Path) -> list[tuple[str, str]]:
    """ディレクトリ内のファイル/サブディレクトリを走査し、内容物テーブルを生成。"""
    contents = []
    for item in sorted(dir_path.iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        if item.name == "PROOF.md":
            continue
        if item.is_dir():
            contents.append((f"{item.name}/", "サブモジュール"))
        elif item.suffix == ".py":
            # .py ファイルなら docstring の1行目を取得
            try:
                text = item.read_text(encoding="utf-8")
                for line in text.split("\n"):
                    if line.strip().startswith('"""') or line.strip().startswith("'''"):
                        doc = line.strip().strip('"\'').strip()
                        if doc:
                            contents.append((item.name, doc[:60]))
                            break
                else:
                    contents.append((item.name, f"{item.stem} の実装"))
            except Exception:
                contents.append((item.name, f"{item.stem} の実装"))
        else:
            contents.append((item.name, "設定/リソース"))
    return contents


# PURPOSE: PROOF.md テンプレートを生成する
def generate_proof(
    dir_path: Path,
    purpose: Optional[str] = None,
    reason: Optional[str] = None,
) -> str:
    """PROOF.md のスケルトンを生成する。"""
    name = dir_path.name
    purpose = purpose or infer_proof_purpose(dir_path)
    reason = reason or infer_proof_reason(dir_path)
    contents = scan_contents(dir_path) if dir_path.exists() else []

    contents_table = ""
    if contents:
        rows = "\n".join(
            f"| {fname} | P2 → {desc} |" for fname, desc in contents
        )
        contents_table = f"""
## 内容物の正当性

| ファイル/ディレクトリ | 演繹 |
|:---------------------|:-----|
{rows}

---
"""

    return f"""# PROOF.md — 存在証明書

PURPOSE: {purpose}
REASON: {reason}

> **∃ {name}/** — この場所は存在しなければならない

---

## 公理

```
A0: 予測誤差最小化 (Free Energy Principle)
```

---

## 演繹

```
A0: 予測誤差最小化
  ↓ [FEP の定義]
P1: Hegemonikón は FEP に基づく認知フレームワークである
  ↓ [実装の必要性]
P2: {purpose}
  ↓ [名前の必然性]
P3: その場所を {name}/ と呼ぶ
```

---

## 結論

```
∴ {name}/ は存在しなければならない

Q.E.D.
```

---
{contents_table}
*{name}/ は Hegemonikón の体系から演繹される。*
"""


# PURPOSE: PROOF.md が存在しないディレクトリを検出する
def scan_missing(root: Path) -> list[Path]:
    """PROOF.md が存在しない Python パッケージディレクトリを検出。"""
    missing = []
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        if d.name.startswith(".") or d.name == "__pycache__":
            continue
        # Python パッケージ判定: .py ファイルが1つ以上あるか
        has_py = any(f.suffix == ".py" for f in d.iterdir() if f.is_file())
        if not has_py:
            continue
        proof = d / "PROOF.md"
        if not proof.exists():
            missing.append(d)
    return missing


# PURPOSE: CLI エントリポイント
def main():
    parser = argparse.ArgumentParser(
        description="PROOF.md スケルトン自動生成 (引力原理: 書くコスト → ゼロ)"
    )
    parser.add_argument("path", help="対象ディレクトリ")
    parser.add_argument(
        "--scan", action="store_true",
        help="PROOF.md が不足しているディレクトリを検出"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="実際に PROOF.md を書き込む (デフォルトは dry-run)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="既存の PROOF.md を上書き"
    )
    args = parser.parse_args()

    target = Path(args.path)

    if args.scan:
        missing = scan_missing(target)
        if not missing:
            print("✅ 全ディレクトリに PROOF.md が存在します")
        else:
            print(f"⚠️ {len(missing)} ディレクトリに PROOF.md がありません:")
            for d in missing:
                print(f"  {d.relative_to(target)}/")
            print()
            print("生成するには: python mekhane/dendron/proof_skeleton.py <dir> --apply")
        return

    if not target.is_dir():
        print(f"ERROR: {target} はディレクトリではありません", file=sys.stderr)
        sys.exit(1)

    proof_path = target / "PROOF.md"
    if proof_path.exists() and not args.force:
        print(f"⏭️  {proof_path} は既に存在します (--force で上書き)")
        return

    skeleton = generate_proof(target)

    if args.apply:
        proof_path.write_text(skeleton, encoding="utf-8")
        print(f"✅ 生成: {proof_path}")
    else:
        print("🔍 DRY RUN — 以下が生成されます:")
        print()
        print(skeleton)
        print("実際に書き込むには --apply を追加")


if __name__ == "__main__":
    main()
