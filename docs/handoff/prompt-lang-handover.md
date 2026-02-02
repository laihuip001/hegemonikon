# 🔄 引継ぎ: prompt-lang v1.0

**更新日**: 2026-01-21
**ステータス**: ✅ 完了 (統合済み)
**優先度**: 高 (運用開始)

---

## 概要

**「AIにとっての言語」** prompt-lang v1.0。
仕様策定、パーサ実装、AIワークフロー統合、Peira連携まで完了。

## 成果物 (参照用)

| コンポーネント | パス | 状態 |
|----------------|------|------|
| **仕様書** | `M:/.gemini/Forge/experimental/prompt-lang/SPEC.md` | ✅ v0.2 + Tools/Resources |
| **パーサ** | `m:/Hegemonikon/forge/prompt-lang/prompt_lang.py` | ✅ v0.3 (Block対応) |
| **統合ツール** | `m:/Hegemonikon/forge/prompt-lang/prompt_lang_integrate.py` | ✅ v1.0 (Integration) |
| **単体テスト** | `m:/Hegemonikon/forge/prompt-lang/test_prompt_lang.py` | ✅ All Pass |
| **自動適用ルール** | `M:/.gemini/.agent/rules/prompt-lang-auto-fire.md` | ✅ Always On |

## 使い方

### 1. プロンプト作成
`.prompt` ファイルを `forge/prompt-lang/staging/` または任意の場所に作成。

### 2. コンパイル & 実行
```powershell
# 内容を確認
python m:/Hegemonikon/forge/prompt-lang/prompt_lang_integrate.py load <path>

# AIに適用（自動発火ルールにより、ファイルを開くだけでAIが認識）
# または M5 Peira 内で必要に応じて自動ロードされる
```

### 3. M5 Peira 連携
情報収集時に prompt-lang 形式の指示があれば、M5 Peira はそれを解釈して実行する。

## 次のステップ (Future)

- [ ] (v1.1) VSCode拡張機能の開発 (シンタックスハイライト)
- [ ] (v1.2) スニペット機能の拡充

---

```
┌─[Hegemonikon]──────────────────────┐
│ M8 Anamnēsis: Handover Updated     │
│ Project: prompt-lang v1.0          │
│ Status: COMPLETE / DEPLOYED        │
└────────────────────────────────────┘
```
