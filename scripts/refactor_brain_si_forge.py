#!/usr/bin/env python3
# PROOF: [L3/移行] <- scripts/
# PURPOSE: SI/Forge モジュールのリファクタリング自動化
"""
Brain Phase 3+4: System Instructions + Forge Prompt Structure → Library 変換
PURPOSE: SI 12個 + Forge 43個を統一形式でLibraryに配置
"""

import os
import re
import yaml

BRAIN_BASE = os.path.expanduser(
    "~/ダウンロード/Brain/99_🗃️_保管庫｜Archive/プロンプト ライブラリー"
)
LIBRARY_BASE = os.path.expanduser(
    "~/Sync/10_📚_ライブラリ｜Library/prompts"
)

# ========== Phase 3: System Instructions ==========

SI_HGK_MAP = {
    "1": {"ja": "統合システム指示 v6.1", "hgk": "KERNEL_DOCTRINE + behavioral_constraints.md"},
    "2": {"ja": "指示書(2)", "hgk": "参考資料"},
    "3": {"ja": "指示書(3)", "hgk": "参考資料"},
    "AI Clipboard Pro開発": {"ja": "AI Clipboard Pro開発", "hgk": "プロジェクト固有"},
    "Deep-Dive Profiler": {"ja": "深掘りプロファイラー", "hgk": "O1 Noēsis (/noe)"},
    "GDR　KB化": {"ja": "GDR KB化", "hgk": "K4 Sophia (/sop)"},
    "GrapheneOS": {"ja": "GrapheneOS", "hgk": "プロジェクト固有"},
    "「Dual-Core Strategy（Gemini 3 Pro & Claude Opus 4.5 Thinking）」": {"ja": "デュアルコア戦略", "hgk": "/vet ワークフロー"},
    "メタプロンプト(for Gemini 3 pro)": {"ja": "メタプロンプト", "hgk": "KERNEL_DOCTRINE"},
    "事実でぶん殴るやつ": {"ja": "ファクトチェッカー", "hgk": "A2 Krisis (/dia)"},
    "品質審問官": {"ja": "品質審問官", "hgk": "A2 Krisis (/dia)"},
    "無題のファイル": {"ja": "無題", "hgk": "不明"},
}

# ========== Phase 4: Forge HGK マッピング ==========

FORGE_HGK_MAP = {
    "脳内を吐き出す": "O3 Zētēsis (/zet)",
    "情報を集める": "K4 Sophia (/sop)",
    "声を聞く": "O3 Zētēsis (/zet)",
    "頭を切り替える": "O3 Zētēsis (/zet)",
    "全体を眺める": "Panorama (/pan)",
    "状況を把握する": "P1 Khōra (/kho)",
    "問題を特定する": "O3 Zētēsis (/zet)",
    "関係者を整理する": "P1 Khōra (/kho)",
    "前提を疑う": "O1 Noēsis (/noe)",
    "アイデアを出す": "O3 Zētēsis (/zet)",
    "点をつなぐ": "A3 Gnōmē (/gno)",
    "逆転させる": "O1 Noēsis (/noe)",
    "揺らぎを与える": "O3 Zētēsis (/zet)",
    "前提を破壊する": "O1 Noēsis (/noe)",
    "選択肢を比較する": "A2 Krisis (/dia)",
    "決断を下す": "A2 Krisis (/dia)",
    "計画を立てる": "P2 Hodos (/hod)",
    "リスクを見積もる": "O2 Boulēsis (/pre)",
    "優先順位をつける": "S1 Metron (/met)",
    "やめる決断をする": "A2 Krisis (/dia)",
    "未来を分岐させる": "K1 Eukairia (/euk)",
    "ボトルネックを突く": "S1 Metron (/met)",
    "本質だけ残す": "S1 Metron (/met)",
    "テコを見つける": "S1 Metron (/met)",
    "悪魔の代弁をする": "A2 Krisis (/dia) devil",
    "断る": "S4 Praxis (/pra)",
    "交渉する": "S4 Praxis (/pra)",  # guessing a close WF
    "演じる": "Synedrion (/syn)",
    "クエスト化する": "S4 Praxis (/pra)",
    "環境をデザインする": "P1 Khōra (/kho)",
    "任せる": "S4 Praxis (/pra)",
    "文章を書く": "S4 Praxis (/pra)",
    "プレゼンを作る": "S4 Praxis (/pra)",
    "仕組み化する": "S2 Mekhanē (/mek)",
    "名前をつける": "O1 Noēsis (/noe)",
    "手順を組む": "S2 Mekhanē (/mek)",
    "図解する": "S4 Praxis (/pra)",
    "プロトタイプを作る": "O4 Energeia (/ene)",
    "品質を確かめる": "A2 Krisis (/dia)",
    "改善案を出す": "O3 Zētēsis (/zet)",
    "経験を振り返る": "A3 Gnōmē (/gno)",
    "記録する": "H4 Doxa (/dox)",
    "賢人に聞く": "Synedrion (/syn)",
    "働きかける": "S4 Praxis (/pra)",
}

FORGE_PHASE_MAP = {
    "見つける": "find",
    "考える/広げる": "think_expand",
    "考える/絞る": "think_focus",
    "働きかける/固める": "act_prepare",
    "働きかける/生み出す": "act_create",
    "振り返る": "reflect",
}


def convert_si(name: str, content: str) -> str:
    """System Instruction を新形式に変換"""
    mapping = SI_HGK_MAP.get(name, {"ja": name, "hgk": "不明"})

    # Gemini 固有を汎用化
    content_clean = content.replace("Gemini 3 Pro", "AI")
    content_clean = content_clean.replace("Geminiに", "AIに")
    content_clean = content_clean.replace("Geminiは", "AIは")
    content_clean = content_clean.replace("Geminiの", "AIの")

    frontmatter = {
        "name": f"SI: {mapping['ja']}",
        "origin": "Brain Vault (pre-FEP)",
        "category": "システム指示｜System Instructions",
        "hegemonikon_mapping": mapping["hgk"],
        "model_target": "universal",
    }
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return f"""---
{yaml_str.strip()}
---

# SI: {mapping['ja']}

> **Hegemonikón 対応**: {mapping['hgk']}

## 原文

{content_clean}
"""


def convert_forge(name_raw: str, content: str, phase: str) -> str:
    """Forge モジュールを新形式に変換"""
    # 絵文字を除去して日本語名を抽出
    name_clean = re.sub(r'^[^\s]+\s+', '', name_raw.replace('.md', ''))
    hgk = FORGE_HGK_MAP.get(name_clean, "未マッピング")

    # Gemini 固有を汎用化
    content_clean = content.replace("Gemini 3 Pro", "AI")
    content_clean = content_clean.replace("Geminiに", "AIに")
    content_clean = content_clean.replace("Geminiは", "AIは")
    content_clean = content_clean.replace("Geminiの", "AIの")

    frontmatter = {
        "name": f"Forge: {name_clean}",
        "origin": "Brain Vault / Forge v2.0",
        "category": f"Forge/{phase}",
        "hegemonikon_mapping": hgk,
        "model_target": "universal",
    }
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return f"""---
{yaml_str.strip()}
---

{content_clean}
"""


def process_si():
    """Phase 3: System Instructions"""
    si_dir = os.path.join(BRAIN_BASE, "System instructions")
    dst_dir = os.path.join(LIBRARY_BASE, "system-instructions")
    os.makedirs(dst_dir, exist_ok=True)

    files = [f for f in os.listdir(si_dir) if f.endswith('.md')]
    print(f"\n=== Phase 3: System Instructions ({len(files)} 個) ===")

    for f in files:
        src = os.path.join(si_dir, f)
        with open(src, 'r', encoding='utf-8') as fp:
            content = fp.read()

        name = f.replace('.md', '')
        converted = convert_si(name, content)

        # ファイル名を安全な形式に
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_').lower()
        if not safe_name:
            safe_name = "unnamed"
        dst = os.path.join(dst_dir, f"si_{safe_name}.md")

        with open(dst, 'w', encoding='utf-8') as fp:
            fp.write(converted)

        mapping = SI_HGK_MAP.get(name, {"hgk": "?"})
        print(f"  ✅ {name} → {mapping['hgk']}")

    print(f"  📁 出力: {dst_dir}")


def process_forge():
    """Phase 4: Forge Prompt Structure"""
    forge_dir = os.path.join(BRAIN_BASE, "Forge Prompt Structure")
    dst_base = os.path.join(LIBRARY_BASE, "templates", "forge")
    os.makedirs(dst_base, exist_ok=True)

    # ファイル構成.md (インデックス) を変換
    index_path = os.path.join(forge_dir, "ファイル構成.md")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as fp:
            content = fp.read()
        dst = os.path.join(dst_base, "00_index.md")
        with open(dst, 'w', encoding='utf-8') as fp:
            fp.write(convert_forge("📋 ファイル構成", content, "index"))
        print("  ✅ ファイル構成 → インデックス")

    # ディレクトリ走査
    walk_map = {
        "見つける": "01_find",
        "考える/広げる": "02_think_expand",
        "考える/絞る": "03_think_focus",
        "働きかける/固める": "04_act_prepare",
        "働きかける/生み出す": "05_act_create",
        "振り返る": "06_reflect",
    }

    total = 0
    for rel_path, dst_folder in walk_map.items():
        src_path = os.path.join(forge_dir, *rel_path.split('/'))
        if not os.path.isdir(src_path):
            print(f"  ⚠️ {rel_path} ディレクトリなし")
            continue

        dst_dir = os.path.join(dst_base, dst_folder)
        os.makedirs(dst_dir, exist_ok=True)

        files = sorted([f for f in os.listdir(src_path) if f.endswith('.md')])
        for f in files:
            with open(os.path.join(src_path, f), 'r', encoding='utf-8') as fp:
                content = fp.read()

            converted = convert_forge(f, content, rel_path)

            # ファイル名の絵文字を除去
            safe_name = re.sub(r'^[^\s]+\s+', '', f.replace('.md', ''))
            safe_name = safe_name.strip().replace(' ', '_')
            dst = os.path.join(dst_dir, f"{safe_name}.md")

            with open(dst, 'w', encoding='utf-8') as fp:
                fp.write(converted)

            name_clean = re.sub(r'^[^\s]+\s+', '', f.replace('.md', ''))
            hgk = FORGE_HGK_MAP.get(name_clean, "?")
            print(f"  ✅ [{rel_path}] {name_clean} → {hgk}")
            total += 1

    print(f"\n  📁 出力: {dst_base}")
    return total


def main():
    print("🔄 Brain Phase 3+4 変換開始")

    process_si()
    total_forge = process_forge()

    print(f"\n✅ Phase 3+4 完了")
    print(f"  SI: 12個 → system-instructions/")
    print(f"  Forge: {total_forge}個 → templates/forge/")


if __name__ == "__main__":
    main()
