#!/usr/bin/env python3
# PROOF: [L3/ユーティリティ] <- scripts/ ルールファイルのfrontmatter一括修正→構造整合性維持
"""
Antigravity Rules frontmatter 一括修正スクリプト
- activation → trigger に変換
- フロントマターがないファイルには追加
- 各ファイルに適切な trigger 値を割り当て
"""
import re
from pathlib import Path

RULES_DIR = Path("/home/makaron8426/oikos/hegemonikon/.agent/rules")

# ファイル → trigger 値のマッピング
# always_on: 常時注入すべきルール
# model_decision: モデルが判断して参照するルール  
# glob: 特定ファイルパターンにマッチ時のみ
TRIGGER_MAP = {
    # === always_on: 核心ルール ===
    "behavioral_constraints.md": ("always_on", "", "認知プロテーゼ — 能力を最大化するための環境支援"),
    "hegemonikon.md": ("always_on", "", "Hegemonikón 公理体系 v3.3 — 96要素認知フレームワーク"),
    "CONSTITUTION.md": ("always_on", "", "Hegemonikón Identity Architecture — 不変ルール"),
    "destructive_ops.md": ("always_on", "", "破壊的操作の安全ガード — ファイル削除・上書き防止"),
    "safety-invariants.md": ("always_on", "", "安全不変条件 — 最高優先度ルール"),
    "ethics-constraints.md": ("always_on", "", "倫理的制約 — 安全性とプライバシー"),
    
    # === model_decision: 状況に応じて参照 ===
    "artifact-language.md": ("model_decision", "", "アーティファクト言語ルール — 出力言語制御"),
    "ccl-manifest.md": ("model_decision", "", "CCL式の透明性・再現性・学習性の必須規約"),
    "derivative-selection.md": ("model_decision", "", "ワークフロー実行時の派生選択ルール"),
    "dispatch.md": ("model_decision", "", "Dispatch Protocol — 静的ルール Phase A"),
    "dispatch-logging.md": ("model_decision", "", "運用ログ収集機構 — Phase B移行判定用"),
    "error-prevention-protocols.md": ("model_decision", "", "エラー防止プロトコル体系 P1-P9"),
    "gemini_sop.md": ("model_decision", "", "Gemini エージェント向け標準作業手順書"),
    "handoff.md": ("model_decision", "", "AI間引き継ぎフォーマット — Handoff Format"),
    "hgk-app-arsenal.md": ("always_on", "", "HGK Desktop App 開発: 既存 PJ を使え"),
    "k-series-activation.md": ("model_decision", "", "K-series 文脈定理の発動条件"),
    "ki-activation.md": ("model_decision", "", "Knowledge Item 活用パターン発動ルール"),
    "metacognition.md": ("model_decision", "", "Metacognition Checkpoints — 自己評価"),
    "model-selection-guide.md": ("model_decision", "", "モデル選択ガイド — 用途別推奨"),
    "protocol-d.md": ("always_on", "", "Protocol D: 外部サービス検証 — 常時適用"),
    "protocol-d-extended.md": ("model_decision", "", "Protocol D-Extended: 存在系断言禁止"),
    "protocol-v.md": ("model_decision", "", "Protocol V: バージョン検証"),
    "session-protocol.md": ("model_decision", "", "セッションプロトコル — 開始/終了手順"),
    "task_template.md": ("model_decision", "", "task.md テンプレート — フェーズ依存関係付き"),
    
    # === manual: 手動参照 ===
    "gemini_handoff_protocol.md": ("manual", "", "Gemini専用 Handoff Protocol"),
    
    # === glob: ファイルパターン ===
    "prompt-generation.md": ("glob", "**/*.prompt", ".prompt ファイル編集時のプロンプト生成ルール"),
    "typos-auto-fire.md": ("glob", "**/*.prompt", "Týpos 自動発火ルール"),
}

def fix_frontmatter(filepath: Path, trigger: str, glob: str, description: str) -> bool:
    """ファイルのフロントマターを正しい形式に修正"""
    content = filepath.read_text(encoding="utf-8")
    
    # 新しいフロントマター
    new_fm = f"---\ntrigger: {trigger}\nglob: {glob}\ndescription: {description}\n---"
    
    # 既存のフロントマターがあるか
    fm_pattern = re.compile(r'^---\s*\n.*?\n---\s*\n', re.DOTALL)
    match = fm_pattern.match(content)
    
    if match:
        # 既存のフロントマターを置換
        new_content = new_fm + "\n" + content[match.end():]
    else:
        # フロントマターがない場合は先頭に追加
        new_content = new_fm + "\n\n" + content
    
    filepath.write_text(new_content, encoding="utf-8")
    return True

def main():
    results = {"success": [], "skip": [], "error": []}
    
    for filename, (trigger, glob, description) in TRIGGER_MAP.items():
        filepath = RULES_DIR / filename
        if not filepath.exists():
            # always/ にある可能性
            alt = RULES_DIR / "always" / filename
            if alt.exists():
                filepath = alt
            else:
                results["skip"].append(f"{filename} (not found)")
                continue
        
        try:
            fix_frontmatter(filepath, trigger, glob, description)
            results["success"].append(f"{filename} → trigger: {trigger}")
        except Exception as e:
            results["error"].append(f"{filename}: {e}")
    
    print("=== 修正結果 ===")
    print(f"\n✅ 成功 ({len(results['success'])}件):")
    for r in results["success"]:
        print(f"  {r}")
    
    if results["skip"]:
        print(f"\n⏭ スキップ ({len(results['skip'])}件):")
        for r in results["skip"]:
            print(f"  {r}")
    
    if results["error"]:
        print(f"\n❌ エラー ({len(results['error'])}件):")
        for r in results["error"]:
            print(f"  {r}")

if __name__ == "__main__":
    main()
