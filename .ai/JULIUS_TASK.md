# Prompt Generation Task

## 🎯 Task: セキュリティレビュー用プロンプト生成

Date: {{date}}
Source: Claude (設計者)
Target: Jules (生成者)

---

## 要件

### Phase 0 分析結果
- **Archetype**: Precision
- **勝利条件**: 脆弱性見落とし率 < 1%
- **許容トレードオフ**: 速度、簡潔さ

### Prompt-Lang 要件
- **@role**: シニアセキュリティエンジニア + 勝利条件明記
- **@goal**: セキュリティレビュー + 確信度ルーティング
- **@context**: file: (対象コード), ki: (OWASP), mcp: (gnosis_search)
- **@constraints**: 5項目以上
- **@rubric**: 4次元以上 (scale, criteria 付き)
- **@if**: Python / TypeScript 分岐
- **@examples**: 1つ以上の詳細な入出力例
- **@fallback**: エッジケース対応

---

## 参照資料

1. **meta-prompt-generator Skill**: `.agent/skills/utils/meta-prompt-generator/SKILL.md`
2. **Prompt-Lang v2 仕様**: `docs/specs/prompt-lang-v2-spec.md`

---

## 出力要件

- **ファイルパス**: `forge/prompt-lang/prompts/security_review_v2.prompt`
- **言語**: 日本語
- **フォーマット**: Prompt-Lang v2

---

## 成功基準

- [ ] パーサーでエラーなくパースできる
- [ ] @rubric が 4次元以上
- [ ] @examples が詳細（入力 + 出力）
- [ ] @fallback が定義されている

---

## 実行手順

1. `meta-prompt-generator/SKILL.md` を読む
2. `prompt-lang-v2-spec.md` を読む
3. Phase 0-6 のワークフローに従って生成
4. `forge/prompt-lang/prompts/security_review_v2.prompt` に保存
5. パーサーで検証: `python prompt_lang.py parse prompts/security_review_v2.prompt`
