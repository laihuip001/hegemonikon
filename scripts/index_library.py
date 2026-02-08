#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- scripts/
# PURPOSE: Library プロンプトのベクトルインデックス構築
"""
Library 112ファイルを Gnōsis LanceDB にインデックス
PURPOSE: セマンティック検索で /lib を強化 (Layer 3)
USAGE: python3 -u scripts/index_library.py
"""

import os
import re
import sys

import yaml

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mekhane.anamnesis.models.prompt_module import PromptModule
from mekhane.anamnesis.index import Embedder

LIBRARY_BASE = os.path.expanduser(
    "~/Sync/10_📚_ライブラリ｜Library/prompts"
)

TABLE_NAME = "prompts"


def parse_module(filepath: str, rel_path: str) -> PromptModule | None:
    """Markdown ファイルを PromptModule に変換"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return None

    end = content.find('---', 3)
    if end == -1:
        return None

    yaml_str = content[3:end].strip()
    body = content[end + 3:].strip()

    try:
        fm = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        return None

    if not isinstance(fm, dict):
        return None

    name = fm.get('name', os.path.basename(filepath).replace('.md', ''))
    category = fm.get('category', '')

    # ID 生成
    name_slug = re.sub(r'[^\w]', '_', name)[:50].lower()
    cat_slug = re.sub(r'[^\w]', '_', category)[:20].lower()
    module_id = f"prompt_{cat_slug}_{name_slug}"

    triggers = fm.get('activation_triggers', [])
    if isinstance(triggers, str):
        triggers = [triggers]

    return PromptModule(
        id=module_id,
        filepath=rel_path,
        name=name,
        category=category,
        origin=fm.get('origin', 'Brain Vault (pre-FEP)'),
        hegemonikon_mapping=fm.get('hegemonikon_mapping', ''),
        model_target=fm.get('model_target', 'universal'),
        activation_triggers=triggers,
        essence=fm.get('essence', ''),
        body=body[:2000],
    )


def main():
    try:
        import lancedb
    except ImportError:
        print("❌ lancedb not installed: pip install lancedb")
        sys.exit(1)

    # モジュール収集
    modules: list[PromptModule] = []
    for root, dirs, files in os.walk(LIBRARY_BASE):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, LIBRARY_BASE)
            module = parse_module(path, rel)
            if module:
                modules.append(module)
                print(f"  📄 {rel}")

    print(f"\n📊 {len(modules)} モジュール収集")

    # Embeddings 生成
    print("\n🧠 Embeddings 生成中...")
    embedder = Embedder()
    texts = [m.embedding_text for m in modules]

    BATCH_SIZE = 32
    all_vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        vectors = embedder.embed_batch(batch)
        all_vectors.extend(vectors)
        print(f"  Processed {min(i + BATCH_SIZE, len(texts))}/{len(texts)}...")

    # LanceDB に保存
    from pathlib import Path
    lance_dir = Path(__file__).parent.parent / "mekhane" / "anamnesis" / "data"
    lance_dir.mkdir(parents=True, exist_ok=True)

    db = lancedb.connect(str(lance_dir))

    data = []
    for module, vector in zip(modules, all_vectors):
        record = module.to_dict()
        record["vector"] = vector
        data.append(record)

    # テーブル削除 → 再作成 (フルリインデックス)
    if TABLE_NAME in db.table_names():
        db.drop_table(TABLE_NAME)
        print(f"  🗑️ 既存 {TABLE_NAME} テーブル削除")

    db.create_table(TABLE_NAME, data=data)
    print(f"\n✅ {len(data)} モジュールを Gnōsis '{TABLE_NAME}' テーブルに登録")

    # 検証: サンプル検索
    print("\n🔍 検証: セマンティック検索テスト")
    table = db.open_table(TABLE_NAME)

    test_queries = ["品質レビュー", "第一原理", "アイデア出し", "リスク評価"]
    for q in test_queries:
        qv = embedder.embed(q)
        results = table.search(qv).limit(3).to_list()
        names = [r.get("name", "?") for r in results]
        print(f"  '{q}' → {names}")


if __name__ == "__main__":
    main()
