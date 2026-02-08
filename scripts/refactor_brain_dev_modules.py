#!/usr/bin/env python3
# PROOF: [L3/移行] <- scripts/
# PURPOSE: dev モジュールのリファクタリング自動化
"""
Brain 開発用 Module 01-25 → Hegemonikón Library 変換スクリプト
PURPOSE: 旧形式(XML)の開発プロトコルをMarkdown+YAMLに変換
"""

import os
import re
import yaml

SRC_DIR = os.path.expanduser(
    "~/ダウンロード/Brain/99_🗃️_保管庫｜Archive/プロンプト ライブラリー/モジュール（開発用）/個別のモジュール"
)
DST_DIR = os.path.expanduser(
    "~/Sync/10_📚_ライブラリ｜Library/prompts/modules/dev"
)

# HGK マッピング
HGK_MAP = {
    "01": {"ja": "非武装地帯プロトコル", "en": "DMZ Protocol", "hgk": "behavioral_constraints.md", "cat": "安全｜Safety"},
    "02": {"ja": "ディレクトリ構造固定", "en": "Directory Topology Lock", "hgk": "S3 Stathmos (/sta)", "cat": "構造｜Structure"},
    "03": {"ja": "依存関係隔離", "en": "Dependency Quarantine", "hgk": "Code Protocols", "cat": "安全｜Safety"},
    "04": {"ja": "テスト駆動開発強制", "en": "TDD Enforcement", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "05": {"ja": "ドメイン言語統一", "en": "Ubiquitous Language", "hgk": "O1 Noēsis + CCL", "cat": "設計｜Design"},
    "06": {"ja": "複雑度予算", "en": "Complexity Budget", "hgk": "S1 Metron (/met)", "cat": "設計｜Design"},
    "07": {"ja": "悪魔の代弁者", "en": "Devil's Advocate", "hgk": "A2 Krisis (/dia) devil", "cat": "品質｜Quality"},
    "08": {"ja": "認知チェックポイント", "en": "Anti-Drift System", "hgk": "O4 Energeia (/ene)", "cat": "品質｜Quality"},
    "09": {"ja": "変異テスト", "en": "Mutation Testing", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "10": {"ja": "波及効果分析", "en": "Ripple Effect Analysis", "hgk": "K1 Eukairia (/euk)", "cat": "分析｜Analysis"},
    "11": {"ja": "自動レッドチーム", "en": "Red Teaming", "hgk": "A2 Krisis (/dia)", "cat": "安全｜Safety"},
    "12": {"ja": "カオスモンキー", "en": "Chaos Monkey", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "13": {"ja": "コード考古学", "en": "Chesterton's Fence", "hgk": "O1 Noēsis (/noe)", "cat": "分析｜Analysis"},
    "14": {"ja": "物語的コミット", "en": "Narrative Commit", "hgk": "Code Protocols", "cat": "運用｜Operations"},
    "15": {"ja": "アトミックデザイン", "en": "Atomic Design", "hgk": "S2 Mekhanē (/mek)", "cat": "設計｜Design"},
    "16": {"ja": "アクセシビリティ義務", "en": "a11y Protocol", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "17": {"ja": "構造化ログ", "en": "Structured Logging", "hgk": "Code Protocols", "cat": "運用｜Operations"},
    "18": {"ja": "フィーチャーフラグ", "en": "Feature Flag", "hgk": "O4 Energeia (/flag)", "cat": "運用｜Operations"},
    "19": {"ja": "Docker優先", "en": "Docker First", "hgk": "Code Protocols", "cat": "運用｜Operations"},
    "20": {"ja": "デッドコード刈取", "en": "Dead Code Reaper", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "21": {"ja": "TODO期限管理", "en": "TODO Expiration", "hgk": "K2 Chronos (/chr)", "cat": "運用｜Operations"},
    "22": {"ja": "自動ドキュメント", "en": "Auto-Documentation", "hgk": "Code Protocols", "cat": "品質｜Quality"},
    "23": {"ja": "モック優先", "en": "Mock First", "hgk": "Code Protocols", "cat": "設計｜Design"},
    "24": {"ja": "パフォーマンス予算", "en": "Performance Budget", "hgk": "S1 Metron (/met)", "cat": "品質｜Quality"},
    "25": {"ja": "ロールバック戦略", "en": "Rollback Strategy", "hgk": "Code Protocols", "cat": "安全｜Safety"},
}


def convert_dev_module(filename: str, content: str) -> str:
    """開発用モジュールを新形式に変換"""
    # Module 番号を抽出
    num_match = re.search(r'Module\s+(\d+)', filename)
    num = num_match.group(1) if num_match else "00"
    mapping = HGK_MAP.get(num, {"ja": "不明", "en": "Unknown", "hgk": "?", "cat": "?"})

    # 目的を抽出
    purpose_match = re.search(r'\*\*目的:\*\*\s*\n(.+?)(?:\n\n|\n\*\*)', content, re.DOTALL)
    purpose = purpose_match.group(1).strip() if purpose_match else ""

    # 技術的アプローチを抽出
    tech_match = re.search(r'\*\*技術的アプローチ:\*\*\s*\n(.+?)(?:\n\n|### )', content, re.DOTALL)
    tech_approach = tech_match.group(1).strip() if tech_match else ""

    # XMLプロンプト本体を抽出
    xml_blocks = re.findall(r'```xml\n(.*?)```', content, re.DOTALL)
    xml_body = "\n".join(xml_blocks) if xml_blocks else ""

    # Gemini 固有記述を汎用化
    xml_body = xml_body.replace("Gemini 3 Pro", "AI")
    xml_body = xml_body.replace("Geminiに", "AIに")
    xml_body = xml_body.replace("Geminiは", "AIは")

    # Architect's Insight を抽出
    insight_match = re.search(r"(### 💡 Architect's Insight.*?)(?:\n\*\*Status|\Z)", content, re.DOTALL)
    insight = insight_match.group(1).strip() if insight_match else ""

    # YAML frontmatter
    frontmatter = {
        "name": f"Module {num}: {mapping['ja']}｜{mapping['en']}",
        "origin": "Brain Vault (pre-FEP)",
        "category": mapping["cat"],
        "hegemonikon_mapping": mapping["hgk"],
        "model_target": "universal",
        "priority": "MEDIUM",
    }
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return f"""---
{yaml_str.strip()}
---

# Module {num}: {mapping['ja']}｜{mapping['en']}

> **Hegemonikón 対応**: {mapping['hgk']}

## 目的

{purpose}

## 技術的アプローチ

{tech_approach}

## プロトコル定義

```xml
{xml_body.strip()}
```

{insight}
"""


def main():
    os.makedirs(DST_DIR, exist_ok=True)

    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.md')])
    print(f"📂 {len(files)} 開発モジュールを変換開始")

    for f in files:
        src_path = os.path.join(SRC_DIR, f)
        with open(src_path, 'r', encoding='utf-8') as fp:
            content = fp.read()

        converted = convert_dev_module(f, content)

        # ファイル名を簡素化: "Module 01 ..." → "module_01.md"
        num_match = re.search(r'Module\s+(\d+)', f)
        num = num_match.group(1) if num_match else "00"
        mapping = HGK_MAP.get(num, {"en": "unknown"})
        slug = mapping["en"].lower().replace("'", "").replace(" ", "_")
        dst_name = f"module_{num}_{slug}.md"

        dst_path = os.path.join(DST_DIR, dst_name)
        with open(dst_path, 'w', encoding='utf-8') as fp:
            fp.write(converted)

        print(f"  ✅ Module {num}: {mapping['ja']} → {mapping['hgk']}")

    print(f"\n✅ 全 {len(files)} 開発モジュール変換完了")
    print(f"📁 出力先: {DST_DIR}")


if __name__ == "__main__":
    main()
