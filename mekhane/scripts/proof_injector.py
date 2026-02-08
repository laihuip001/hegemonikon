#!/usr/bin/env python3
# PROOF: [L3/ツール] <- mekhane/scripts/
"""
PROOF Header Batch Injector

Usage:
    python3 proof_injector.py [--dry-run]
"""

import argparse
import re
from pathlib import Path

# ファイルごとのPROOFレベル設定
FILE_LEVELS = {
    # mekhane/fep - 定理実装
    "fep_agent.py": "L1/定理",
    "horme_evaluator.py": "L1/定理",
    "akribeia_evaluator.py": "L1/定理",
    "telos_checker.py": "L1/定理",
    "krisis_judge.py": "L1/定理",
    "chronos_evaluator.py": "L1/定理",
    "eukairia_detector.py": "L1/定理",
    "zetesis_inquirer.py": "L1/定理",
    "sophia_researcher.py": "L1/定理",
    "energeia_executor.py": "L1/定理",
    "doxa_persistence.py": "L1/定理",
    "derivative_selector.py": "L1/定理",
    "meaningful_traces.py": "L1/定理",
    "perigraphe_engine.py": "L1/定理",
    # mekhane/fep - インフラ
    "fep_bridge.py": "L2/インフラ",
    "encoding.py": "L2/インフラ",
    "persistence.py": "L2/インフラ",
    "state_spaces.py": "L2/インフラ",
    "llm_evaluator.py": "L2/インフラ",
    "config.py": "L2/インフラ",
    "schema_analyzer.py": "L2/インフラ",
    "tekhne_registry.py": "L2/インフラ",
    "se_principle_validator.py": "L2/インフラ",
    "__init__.py": "L2/インフラ",
    # mekhane/anamnesis
    "module_indexer.py": "L2/インフラ",
    "mneme_cli.py": "L2/インフラ",
    "memory_search.py": "L2/インフラ",
    "antigravity_logs.py": "L2/インフラ",
    "logger.py": "L2/インフラ",
    "index_v2.py": "L2/インフラ",
    "vault.py": "L2/インフラ",
    "test_extract.py": "L3/テスト",
    "export_chats.py": "L2/インフラ",
    "index.py": "L2/インフラ",
    "export_simple.py": "L2/インフラ",
    "night_review.py": "L2/インフラ",
    "workflow_inventory.py": "L2/インフラ",
    "lancedb_indexer.py": "L2/インフラ",
    "cli.py": "L2/インフラ",
    "workflow_artifact_batch.py": "L2/インフラ",
    # collectors
    "arxiv.py": "L2/インフラ",
    "semantic_scholar.py": "L2/インフラ",
    "base.py": "L2/インフラ",
    "openalex.py": "L2/インフラ",
    # models
    "paper.py": "L2/インフラ",
    # symploke
    "factory.py": "L2/インフラ",
}

# デフォルトレベル
DEFAULT_LEVEL = "L2/インフラ"


# PURPOSE: ファイル名からPROOFレベルを取得
def get_proof_level(filename: str) -> str:
    """ファイル名からPROOFレベルを取得"""
    return FILE_LEVELS.get(filename, DEFAULT_LEVEL)


# PURPOSE: ファイルにPROOFヘッダーを追加
def add_proof_header(filepath: Path, dry_run: bool = False) -> bool:
    """ファイルにPROOFヘッダーを追加"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ❌ 読み込みエラー: {e}")
        return False

    # 既存のPROOFヘッダーをチェック
    if re.search(r"#\s*PROOF:", content[:500]):
        print(f"  ⏭️ 既存: {filepath}")
        return True

    level = get_proof_level(filepath.name)
    header = f"# PROOF: [{level}]\n"

    # shebangがある場合はその後に挿入
    if content.startswith("#!"):
        lines = content.split("\n", 1)
        new_content = lines[0] + "\n" + header + (lines[1] if len(lines) > 1 else "")
    else:
        new_content = header + content

    if dry_run:
        print(f"  🔍 [DRY-RUN] {filepath} → [{level}]")
    else:
        filepath.write_text(new_content, encoding="utf-8")
        print(f"  ✅ 追加: {filepath} → [{level}]")

    return True


# PURPOSE: 関数: main
def main():
    parser = argparse.ArgumentParser(description="PROOF Header Batch Injector")
    parser.add_argument("--dry-run", action="store_true", help="実際には変更しない")
    args = parser.parse_args()

    root = Path(__file__).parent.parent  # mekhane ディレクトリ

    # 対象ファイルリスト
    targets = [
        # fep
        root / "fep/schema_analyzer.py",
        root / "fep/chronos_evaluator.py",
        root / "fep/fep_agent.py",
        root / "fep/eukairia_detector.py",
        root / "fep/telos_checker.py",
        root / "fep/krisis_judge.py",
        root / "fep/horme_evaluator.py",
        root / "fep/fep_bridge.py",
        root / "fep/__init__.py",
        root / "fep/encoding.py",
        root / "fep/perigraphe_engine.py",
        root / "fep/doxa_persistence.py",
        root / "fep/persistence.py",
        root / "fep/energeia_executor.py",
        root / "fep/state_spaces.py",
        root / "fep/zetesis_inquirer.py",
        root / "fep/sophia_researcher.py",
        root / "fep/derivative_selector.py",
        root / "fep/llm_evaluator.py",
        root / "fep/config.py",
        root / "fep/meaningful_traces.py",
        root / "fep/akribeia_evaluator.py",
        root / "fep/tekhne_registry.py",
        root / "fep/se_principle_validator.py",
        # anamnesis
        root / "anamnesis/module_indexer.py",
        root / "anamnesis/mneme_cli.py",
        root / "anamnesis/memory_search.py",
        root / "anamnesis/antigravity_logs.py",
        root / "anamnesis/logger.py",
        root / "anamnesis/index_v2.py",
        root / "anamnesis/vault.py",
        root / "anamnesis/test_extract.py",
        root / "anamnesis/export_chats.py",
        root / "anamnesis/index.py",
        root / "anamnesis/export_simple.py",
        root / "anamnesis/night_review.py",
        root / "anamnesis/workflow_inventory.py",
        root / "anamnesis/lancedb_indexer.py",
        root / "anamnesis/cli.py",
        root / "anamnesis/workflow_artifact_batch.py",
        root / "anamnesis/models/paper.py",
        root / "anamnesis/collectors/arxiv.py",
        root / "anamnesis/collectors/semantic_scholar.py",
        root / "anamnesis/collectors/base.py",
        root / "anamnesis/collectors/openalex.py",
        # symploke
        root / "symploke/factory.py",
        root / "symploke/config.py",
    ]

    print(f"📋 PROOF Header Injector")
    print(f"   対象: {len(targets)} ファイル")
    print(f"   モード: {'DRY-RUN' if args.dry_run else '実行'}")
    print()

    success = 0
    for target in targets:
        if target.exists():
            if add_proof_header(target, args.dry_run):
                success += 1
        else:
            print(f"  ⚠️ 見つからない: {target}")

    print()
    print(f"✅ 完了: {success}/{len(targets)} ファイル")


if __name__ == "__main__":
    main()
