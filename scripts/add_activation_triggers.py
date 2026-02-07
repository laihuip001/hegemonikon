#!/usr/bin/env python3
"""
Library 111ファイルに activation_triggers と essence を追加
PURPOSE: /dia+ で指摘された「静的ルーティングテーブル問題」の解決
         データ側に意味を持たせ、Skill は動的ルーターにする
"""

import os
import re
import yaml

LIBRARY_BASE = os.path.expanduser(
    "~/Sync/10_📚_ライブラリ｜Library/prompts"
)

# カテゴリ → activation_triggers マッピング
# YAML frontmatter の既存情報 (name, category, hegemonikon_mapping) から自動推定
TRIGGER_MAP = {
    # 一般プロンプトモジュール (modules/)
    "分析": ["分析", "深掘り", "構造化", "investigate", "analyze"],
    "品質": ["レビュー", "評価", "品質", "監査", "review", "quality", "audit"],
    "設計": ["設計", "構造", "アーキテクチャ", "design", "structure"],
    "実行": ["実装", "実行", "作る", "build", "implement", "execute"],
    "対話": ["対話", "コミュニケーション", "プレゼン", "communicate"],
    "計画": ["計画", "スケジュール", "見積もり", "plan", "estimate"],
    "学習": ["振り返り", "学び", "法則化", "learn", "retrospect"],
    "思考": ["思考", "発想", "アイデア", "think", "ideate"],

    # 開発用モジュール (modules/dev/)
    "安全": ["セキュリティ", "安全", "DMZ", "隔離", "security", "safety"],
    "品質": ["テスト", "TDD", "品質", "test", "quality"],
    "構造": ["構造", "ディレクトリ", "設計", "structure", "directory"],
    "運用": ["デプロイ", "ログ", "運用", "Docker", "deploy", "operations"],
}

# name から activation_triggers を推定するためのキーワードマッピング
NAME_TRIGGER_MAP = {
    # 一般モジュール
    "第一原理": ["分析", "根本", "前提を疑う", "first_principles", "noe", "zet"],
    "敵対的レビュー": ["レビュー", "品質", "批判", "review", "dia"],
    "おべっか": ["評価", "正直", "フィードバック", "honest_review", "dia"],
    "オッカム": ["簡素化", "複雑度", "削減", "simplify", "met"],
    "コンテキスト": ["文脈", "構造化", "言語化", "context", "kho"],
    "自律思考": ["自律", "多角的", "深い思考", "autonomous", "noe"],
    "経験の法則化": ["振り返り", "学び", "教訓", "lessons", "gno"],
    "発散": ["アイデア", "ブレスト", "創造", "diverge", "zet"],
    "収束": ["決定", "優先", "絞る", "converge", "dia"],
    "七世代": ["長期", "未来", "影響", "long_term", "bou"],
    "逆ピラミッド": ["要約", "構造", "情報設計", "summary"],
    "WBS": ["計画", "スケジュール", "見積もり", "planning", "chr"],
    "仮想ユーザー": ["ユーザー", "座談会", "フィードバック", "user_test", "syn"],
    "プロンプト外科手術": ["プロンプト", "改善", "リファクタ", "prompt_surgery", "mek"],
    "プロンプト構造監査": ["プロンプト", "監査", "品質", "prompt_audit", "dia"],
    "システム構造監査": ["システム", "監査", "アーキテクチャ", "system_audit", "dia"],
    "システム・ダイナミクス": ["予測", "システム", "動的", "dynamics", "euk"],
    "リバースエンジニアリング": ["解析", "分解", "理解", "reverse", "noe"],
    "コード外科手術": ["コード", "修正", "リファクタ", "code_fix", "dev"],
    "コード監査": ["コード", "品質", "レビュー", "code_review", "dev"],
    "コーディング仕様書": ["仕様", "設計書", "ドキュメント", "spec", "dev"],
    "天才的簡潔": ["簡潔", "圧縮", "本質", "concise", "met"],
    "問いの爆撃": ["質問", "問い", "探求", "questioning", "zet"],
    "感情共鳴": ["感情", "共感", "対人", "empathy", "pat"],
    "結論準備": ["結論", "まとめ", "決定", "conclusion", "dia"],
    "構造化ブレスト": ["ブレスト", "アイデア", "創造", "brainstorm", "zet"],
    "潜在リスク": ["リスク", "危険", "予防", "risk", "pre"],
    "説得力": ["説得", "提案", "プレゼン", "persuasion", "pra"],

    # 開発モジュール
    "DMZ": ["設定", "危険", "安全", "dmz", "safety"],
    "ディレクトリ": ["構造", "フォルダ", "ファイル", "directory", "sta"],
    "依存関係": ["依存", "パッケージ", "隔離", "dependency"],
    "テスト駆動": ["テスト", "TDD", "品質", "testing"],
    "ドメイン言語": ["命名", "用語", "統一", "naming", "noe"],
    "複雑度予算": ["複雑度", "シンプル", "予算", "complexity", "met"],
    "悪魔の代弁": ["反論", "批判", "devils", "dia"],
    "認知チェックポイント": ["ドリフト", "集中", "確認", "checkpoint", "ene"],
    "変異テスト": ["テスト", "品質", "mutation", "testing"],
    "波及効果": ["影響", "リスク", "変更", "ripple", "euk"],
    "レッドチーム": ["セキュリティ", "攻撃", "脆弱性", "redteam", "dia"],
    "カオスモンキー": ["耐障害", "テスト", "chaos", "testing"],
    "コード考古学": ["歴史", "なぜ", "理由", "archaeology", "noe"],
    "物語的コミット": ["コミット", "Git", "説明", "commit"],
    "アトミックデザイン": ["コンポーネント", "UI", "設計", "atomic", "mek"],
    "アクセシビリティ": ["a11y", "アクセス", "inclusivity"],
    "構造化ログ": ["ログ", "観測", "デバッグ", "logging"],
    "フィーチャーフラグ": ["リリース", "フラグ", "段階的", "flag", "ene"],
    "Docker": ["コンテナ", "環境", "Docker", "container"],
    "デッドコード": ["削除", "不要", "クリーン", "cleanup"],
    "TODO期限": ["TODO", "期限", "管理", "deadline", "chr"],
    "自動ドキュメント": ["ドキュメント", "自動", "生成", "documentation"],
    "モック優先": ["モック", "テスト", "分離", "mock"],
    "パフォーマンス予算": ["パフォーマンス", "速度", "予算", "performance", "met"],
    "ロールバック": ["ロールバック", "復旧", "安全", "rollback"],
}

# Forge カテゴリ → triggers
FORGE_TRIGGER_MAP = {
    "find": ["探す", "見つける", "情報収集", "discover", "find"],
    "think_expand": ["広げる", "発散", "アイデア", "expand", "diverge"],
    "think_focus": ["絞る", "収束", "決定", "focus", "converge"],
    "act_prepare": ["準備", "交渉", "段取り", "prepare"],
    "act_create": ["作る", "書く", "生成", "create", "write"],
    "reflect": ["振り返る", "評価", "改善", "reflect", "review"],
}


def get_triggers_for_module(name: str, category: str) -> list[str]:
    """モジュール名とカテゴリから activation_triggers を推定"""
    triggers = []

    # 名前ベースのマッチング
    for key, trigs in NAME_TRIGGER_MAP.items():
        if key in name:
            triggers.extend(trigs)
            break

    # カテゴリベースのマッチング (Forge)
    for key, trigs in FORGE_TRIGGER_MAP.items():
        if key in category.lower():
            triggers.extend(trigs)
            break

    # 重複排除して返す
    return list(dict.fromkeys(triggers)) if triggers else ["general"]


def extract_essence(content: str, max_lines: int = 5) -> str:
    """モジュールの核心3-5行を抽出（コンテキスト注入用）"""
    # YAML frontmatter を除去
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    # Core Objective / 目的 / System Request セクションを探す
    patterns = [
        r'## (?:Core Objective|目的)\s*\n(.*?)(?:\n##|\n---|\Z)',
        r'## System Request\s*\n(.*?)(?:\n##|\n---|\Z)',
        r'# .*?\n\n(.*?)(?:\n##|\n---|\Z)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            text = match.group(1).strip()
            lines = [l for l in text.split('\n') if l.strip()][:max_lines]
            return '\n'.join(lines)

    # フォールバック: 最初の非空行から max_lines 行
    lines = [l for l in content.split('\n') if l.strip()][:max_lines]
    return '\n'.join(lines)


def process_file(filepath: str) -> bool:
    """1ファイルに activation_triggers と essence を追加"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 既に activation_triggers がある場合はスキップ
    if 'activation_triggers:' in content:
        return False

    # YAML frontmatter を解析
    if not content.startswith('---'):
        return False

    end = content.find('---', 3)
    if end == -1:
        return False

    yaml_str = content[3:end].strip()
    body = content[end + 3:]

    try:
        fm = yaml.safe_load(yaml_str)
    except yaml.YAMLError:
        return False

    if not isinstance(fm, dict):
        return False

    # triggers と essence を追加
    name = fm.get('name', '')
    category = fm.get('category', '')
    triggers = get_triggers_for_module(name, category)
    essence = extract_essence(body)

    fm['activation_triggers'] = triggers
    fm['essence'] = essence

    # 再出力
    yaml_out = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{yaml_out.strip()}\n---{body}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    updated = 0
    skipped = 0

    for root, dirs, files in os.walk(LIBRARY_BASE):
        for f in files:
            if not f.endswith('.md'):
                continue
            path = os.path.join(root, f)
            if process_file(path):
                rel = os.path.relpath(path, LIBRARY_BASE)
                print(f"  ✅ {rel}")
                updated += 1
            else:
                skipped += 1

    print(f"\n✅ {updated} ファイル更新, {skipped} スキップ")


if __name__ == "__main__":
    main()
