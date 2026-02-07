#!/usr/bin/env python3
"""
Brain モジュール → Hegemonikón Library 変換スクリプト
PURPOSE: 旧形式(XML/HTML)のプロンプトモジュールをMarkdown+YAMLに変換

変換ルール:
1. XML タグを除去 → Markdown 構造に変換
2. YAML frontmatter を追加（name, origin, hegemonikon_mapping, model_target）
3. Gemini 3 Pro 固有記述を汎用化
4. Architect's Note を補足として保持
"""

import os
import re
import yaml

# ソース・宛先
SRC_DIR = os.path.expanduser(
    "~/ダウンロード/Brain/99_🗃️_保管庫｜Archive/プロンプト ライブラリー/モジュール"
)
DST_DIR = os.path.expanduser(
    "~/Sync/10_📚_ライブラリ｜Library/prompts/modules"
)

# Hegemonikon WF/Skill マッピング
HGK_MAP = {
    "第一原理思考": {"en": "First Principles", "hgk": "O1 Noēsis (/noe)", "cat": "思考｜Thinking"},
    "自律思考": {"en": "Autonomous Thinking", "hgk": "O4 Energeia (/ene)", "cat": "思考｜Thinking"},
    "発散と収束": {"en": "Diverge & Converge", "hgk": "O3 Zētēsis (/zet) + A2 Krisis (/dia)", "cat": "思考｜Thinking"},
    "多角的ラテラル・シンキング": {"en": "Lateral Thinking", "hgk": "O3 Zētēsis (/zet)", "cat": "思考｜Thinking"},
    "七世代先の視点": {"en": "Seven Generations Ahead", "hgk": "K3 Telos (/tel)", "cat": "思考｜Thinking"},
    "オッカムのカミソリ": {"en": "Occam's Razor", "hgk": "S1 Metron (/met)", "cat": "思考｜Thinking"},
    "単純性原理と平易な説明": {"en": "Simplicity Principle", "hgk": "S1 Metron (/met)", "cat": "思考｜Thinking"},
    "論理的背景の補強": {"en": "Logical Reinforcement", "hgk": "A4 Epistēmē (/epi)", "cat": "思考｜Thinking"},
    "経験の法則化": {"en": "Experience Crystallization", "hgk": "A3 Gnōmē (/gno) + H4 Doxa (/dox)", "cat": "学習｜Learning"},
    "成功の解体新書": {"en": "Success Deconstruction", "hgk": "A3 Gnōmē (/gno)", "cat": "学習｜Learning"},
    "未踏の改善点": {"en": "Unexplored Improvements", "hgk": "O3 Zētēsis (/zet)", "cat": "学習｜Learning"},
    "現実への接地": {"en": "Grounding to Reality", "hgk": "S4 Praxis (/pra)", "cat": "学習｜Learning"},
    "敵対的レビュー凸": {"en": "Adversarial Review", "hgk": "A2 Krisis (/dia) devil mode", "cat": "評価｜Evaluation"},
    "おべっかの無い評価": {"en": "Honest Evaluation", "hgk": "A2 Krisis (/dia)", "cat": "評価｜Evaluation"},
    "エレガンススマート監査": {"en": "Elegance Audit", "hgk": "A2 Krisis (/dia)", "cat": "評価｜Evaluation"},
    "プロンプト構造監査凸": {"en": "Prompt Structure Audit", "hgk": "A2 Krisis (/dia)", "cat": "評価｜Evaluation"},
    "プロンプト外科手術凹": {"en": "Prompt Surgery", "hgk": "S2 Mekhanē (/mek)", "cat": "評価｜Evaluation"},
    "システム構造監査": {"en": "System Structure Audit", "hgk": "A2 Krisis (/dia)", "cat": "評価｜Evaluation"},
    "システム・ダイナミクス予想": {"en": "System Dynamics Forecast", "hgk": "K1 Eukairia (/euk)", "cat": "評価｜Evaluation"},
    "コード監査凸": {"en": "Code Audit", "hgk": "Code Protocols", "cat": "開発｜Development"},
    "コード外科手術凹": {"en": "Code Surgery", "hgk": "Code Protocols", "cat": "開発｜Development"},
    "コーディング仕様書コンパイル": {"en": "Coding Spec Compiler", "hgk": "Code Protocols", "cat": "開発｜Development"},
    "リバースエンジニアリング": {"en": "Reverse Engineering", "hgk": "Code Protocols + O1 Noēsis", "cat": "開発｜Development"},
    "外科的再構築凹": {"en": "Surgical Reconstruction", "hgk": "S2 Mekhanē (/mek)", "cat": "開発｜Development"},
    "仮想ユーザー座談会": {"en": "Virtual User Panel", "hgk": "Synedrion (/syn)", "cat": "対話｜Dialogue"},
    "回答の解像度向上": {"en": "Answer Resolution Up", "hgk": "S1 Metron (/met)", "cat": "対話｜Dialogue"},
    "コンテキスト構造化": {"en": "Context Structuring", "hgk": "P1 Khōra (/kho)", "cat": "文脈｜Context"},
    "コンテキストの言語化": {"en": "Context Verbalization", "hgk": "P1 Khōra (/kho)", "cat": "文脈｜Context"},
    "外部文脈の結合": {"en": "External Context Binding", "hgk": "P1 Khōra (/kho)", "cat": "文脈｜Context"},
    "形態素解析マトリクス": {"en": "Morphological Analysis", "hgk": "O3 Zētēsis (/zet)", "cat": "分析｜Analysis"},
    "WBSスケジューリング": {"en": "WBS Scheduling", "hgk": "K2 Chronos (/chr)", "cat": "計画｜Planning"},
}


def strip_xml_tags(text: str) -> str:
    """XML タグを除去し、内容のみ残す"""
    # コードブロック内のXMLは保持（プロンプト本体として）
    return text


def extract_sections(content: str) -> dict:
    """旧形式のセクションを抽出"""
    sections = {
        "header": "",
        "optimization": "",
        "prompt_body": "",
        "expansions": "",
        "architects_note": "",
    }

    lines = content.split("\n")
    current = "header"
    code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            code_block = not code_block

        if "Expansion" in line and "###" in line and not code_block:
            current = "expansions"
        elif "Architect's Note" in line and not code_block:
            current = "architects_note"
        elif "最適化ロジック" in line and not code_block:
            current = "optimization"
        elif line.strip().startswith("```markdown") and current == "optimization":
            current = "prompt_body"

        sections[current] += line + "\n"

    return sections


def convert_module(filename: str, content: str) -> str:
    """1モジュールを新形式に変換"""
    name_ja = filename.replace(".md", "")
    mapping = HGK_MAP.get(name_ja, {"en": name_ja, "hgk": "未マッピング", "cat": "その他｜Other"})

    # Module ID を抽出
    module_id_match = re.search(r'Module\s+([A-Z]-?\d+(?:\.\d+)?)\s+\[(\w+)\]', content)
    module_id = module_id_match.group(1) if module_id_match else "?"
    codename = module_id_match.group(2) if module_id_match else "?"

    # 最適化ロジックを抽出
    opt_match = re.search(r'\*\*最適化ロジック:\*\*\s*\n(.+?)(?:\n\n|\n```)', content, re.DOTALL)
    optimization = opt_match.group(1).strip() if opt_match else ""

    # YAML frontmatter
    frontmatter = {
        "name": f"{name_ja}｜{mapping['en']}",
        "original_id": f"Module {module_id} [{codename}]",
        "origin": "Brain Vault (pre-FEP)",
        "category": mapping["cat"],
        "hegemonikon_mapping": mapping["hgk"],
        "model_target": "universal",
    }

    # プロンプト本体を抽出（```markdown ... ``` の間）
    prompt_blocks = re.findall(r'```markdown\n(.*?)```', content, re.DOTALL)
    prompt_body = "\n---\n".join(prompt_blocks) if prompt_blocks else ""

    # XML タグを Markdown に変換
    prompt_body = re.sub(r'<module_config>.*?</module_config>\s*', '', prompt_body, flags=re.DOTALL)
    prompt_body = re.sub(r'</?instruction>', '', prompt_body)
    prompt_body = re.sub(r'</?rules>', '', prompt_body)
    prompt_body = re.sub(r'</?steps>', '', prompt_body)
    prompt_body = re.sub(r'</?constraint_checklist>', '', prompt_body)
    prompt_body = re.sub(r'</?input_context>\s*', '', prompt_body)
    prompt_body = re.sub(r'</?input_source>\s*', '', prompt_body)
    prompt_body = re.sub(r'</?output_template>', '', prompt_body)
    prompt_body = re.sub(r'</?thinking_steps>', '', prompt_body)
    prompt_body = re.sub(r'<([a-z_]+)>', r'### \1', prompt_body)
    prompt_body = re.sub(r'</[a-z_]+>', '', prompt_body)
    prompt_body = re.sub(r'{{(\w+)}}', r'[入力: \1]', prompt_body)

    # Gemini 固有記述を汎用化
    prompt_body = prompt_body.replace("Gemini 3 Pro", "AI")
    prompt_body = prompt_body.replace("Geminiに", "AIに")
    prompt_body = prompt_body.replace("Geminiは", "AIは")
    prompt_body = prompt_body.replace("Geminiの", "AIの")

    # 派生モジュール
    exp_match = re.search(r'(## 🔮 New Expansion Modules.*?)(?:---\s*\n## 💡|---\s*$|\Z)', content, re.DOTALL)
    expansions = exp_match.group(1).strip() if exp_match else ""
    if expansions:
        expansions = expansions.replace("Gemini 3 Pro", "AI")

    # Architect's Note
    note_match = re.search(r'(## 💡 Architect\'s Note.*?)$', content, re.DOTALL)
    architects_note = note_match.group(1).strip() if note_match else ""
    if architects_note:
        architects_note = architects_note.replace("Gemini 3 Pro", "AI")
        architects_note = architects_note.replace("Geminiに", "AIに")
        architects_note = architects_note.replace("Geminiは", "AIは")
        architects_note = architects_note.replace("Geminiの", "AIの")

    # 組み立て
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)

    output = f"""---
{yaml_str.strip()}
---

# {name_ja}｜{mapping['en']}

> **旧ID**: Module {module_id} [{codename}]
> **Hegemonikón 対応**: {mapping['hgk']}

## 概要

{optimization}

## プロンプト本体

{prompt_body.strip()}
"""

    if expansions:
        output += f"\n{expansions}\n"

    if architects_note:
        output += f"\n{architects_note}\n"

    return output


def main():
    os.makedirs(DST_DIR, exist_ok=True)

    files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.md')])
    print(f"📂 {len(files)} モジュールを変換開始")

    for f in files:
        src_path = os.path.join(SRC_DIR, f)
        with open(src_path, 'r', encoding='utf-8') as fp:
            content = fp.read()

        converted = convert_module(f, content)

        dst_path = os.path.join(DST_DIR, f)
        with open(dst_path, 'w', encoding='utf-8') as fp:
            fp.write(converted)

        name_ja = f.replace(".md", "")
        mapping = HGK_MAP.get(name_ja, {})
        hgk = mapping.get("hgk", "?")
        print(f"  ✅ {name_ja} → {hgk}")

    print(f"\n✅ 全 {len(files)} モジュール変換完了")
    print(f"📁 出力先: {DST_DIR}")


if __name__ == "__main__":
    main()
