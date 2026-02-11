#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ O4→収集した論文をGnōsisに投入
# PURPOSE: collected_papers.json → Gnōsis LanceDB インデックスへの投入
"""
FEP Papers → Gnōsis Indexer
=============================

collect_fep_papers.py で収集した論文を Gnōsis (LanceDB) に投入する。

既存テーブルのスキーマ:
    primary_key, title, source, abstract, content, authors,
    doi, arxiv_id, url, citations, vector (dim=1024)

Usage:
    # ドライラン（変換のみ、投入しない）
    python scripts/index_fep_papers.py --dry-run

    # 本番実行
    python scripts/index_fep_papers.py

    # 投入後にインデックス統計を表示
    python scripts/index_fep_papers.py --stats
"""

import sys
import json
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mekhane.anamnesis.index import GnosisIndex, Embedder

# Input / Output
COLLECTED_FILE = PROJECT_ROOT / "data" / "fep_papers" / "collected_papers.json"
GNOSIS_DIR = PROJECT_ROOT / "gnosis_data"
LANCE_DIR = GNOSIS_DIR / "lancedb"
TABLE_NAME = "knowledge"


def build_records(collected: list[dict]) -> list[dict]:
    """collected_papers.json → 既存テーブルスキーマ準拠のレコードに変換"""
    records: list[dict] = []
    skipped = 0

    for entry in collected:
        abstract = entry.get("abstract") or ""
        if len(abstract) < 20:
            skipped += 1
            continue

        paper_id = entry.get("paper_id", "")
        doi = entry.get("doi") or ""
        arxiv_id = entry.get("arxiv_id") or ""
        year = entry.get("year")
        authors = entry.get("authors", [])

        # primary_key: DOI > arXiv > source:id
        if doi:
            pk = f"doi:{doi}"
        elif arxiv_id:
            pk = f"arxiv:{arxiv_id}"
        else:
            pk = f"semantic_scholar:{paper_id}"

        title = entry.get("title", "")

        record = {
            "primary_key": pk,
            "title": title,
            "source": "semantic_scholar",
            "abstract": abstract[:2000],
            "content": f"{title} {abstract[:1000]}",  # embedding_text 相当
            "authors": ", ".join(authors[:10]) if authors else "",
            "doi": doi,
            "arxiv_id": arxiv_id,
            "url": entry.get("url", ""),
            "citations": entry.get("citation_count", 0) or 0,
        }
        records.append(record)

    print(f"  変換: {len(records)} records (abstract 不足で {skipped} skip)")
    return records


def dedupe_against_index(records: list[dict], db) -> list[dict]:
    """既存インデックスとの重複除去"""
    import lancedb
    from mekhane.anamnesis.lancedb_compat import get_table_names

    if TABLE_NAME not in get_table_names(db):
        return records

    table = db.open_table(TABLE_NAME)

    # 既存の primary_key と正規化 title をキャッシュ
    existing_pks = set()
    existing_titles = set()
    try:
        all_rows = table.to_pandas()
        existing_pks = set(all_rows["primary_key"].tolist())
        existing_titles = {
            t.lower().replace(" ", "").replace("-", "")
            for t in all_rows["title"].tolist()
            if t
        }
    except Exception as e:
        print(f"  ⚠️ 既存データ読込エラー: {e}")

    new_records = []
    for r in records:
        if r["primary_key"] in existing_pks:
            continue
        norm_title = r["title"].lower().replace(" ", "").replace("-", "")
        if norm_title and norm_title in existing_titles:
            continue
        new_records.append(r)
        existing_pks.add(r["primary_key"])
        if norm_title:
            existing_titles.add(norm_title)

    print(f"  重複除去: {len(records)} → {len(new_records)} (既存 {len(records) - len(new_records)} 件)")
    return new_records


def main():
    import argparse
    import lancedb

    parser = argparse.ArgumentParser(description="FEP Papers → Gnōsis Indexer")
    parser.add_argument("--dry-run", action="store_true", help="変換のみ、投入しない")
    parser.add_argument("--stats", action="store_true", help="投入後に統計表示")
    args = parser.parse_args()

    if not COLLECTED_FILE.exists():
        print(f"❌ {COLLECTED_FILE} が見つかりません。先に collect_fep_papers.py を実行してください。")
        sys.exit(1)

    # 読み込み
    collected = json.loads(COLLECTED_FILE.read_text())
    print(f"📂 読込: {len(collected)} papers from {COLLECTED_FILE.name}")

    # レコード構築
    records = build_records(collected)

    if args.dry_run:
        print(f"\n🔍 DRY RUN — 投入しません")
        print(f"\n  サンプル (top 5):")
        for r in records[:5]:
            year = "?"
            print(f"    {r['citations']:>5}c | {r['title'][:60]}")
            print(f"      Key: {r['primary_key']}")
            print(f"      Abstract: {r['abstract'][:80]}...")
        return

    # DB 接続 & 重複除去
    LANCE_DIR.mkdir(parents=True, exist_ok=True)
    db = lancedb.connect(str(LANCE_DIR))
    records = dedupe_against_index(records, db)

    if not records:
        print("  ✅ 全て既存。投入不要。")
        return

    # 埋め込み生成
    print(f"\n🚀 Embedding生成中... ({len(records)} records)")
    embedder = Embedder()

    BATCH_SIZE = 32
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        texts = [r["content"] for r in batch]
        vectors = embedder.embed_batch(texts)
        for r, v in zip(batch, vectors):
            r["vector"] = v
        print(f"  Processed {min(i + BATCH_SIZE, len(records))}/{len(records)}...")

    # LanceDB に追加
    from mekhane.anamnesis.lancedb_compat import get_table_names

    if TABLE_NAME in get_table_names(db):
        table = db.open_table(TABLE_NAME)
        table.add(records)
    else:
        db.create_table(TABLE_NAME, data=records)

    print(f"\n✅ 投入完了: {len(records)} papers added to Gnōsis")

    # 統計
    index = GnosisIndex()
    stats = index.stats()
    print(f"\n📊 Gnōsis Index Stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
